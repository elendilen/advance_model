from flask import Flask, request, render_template, redirect, jsonify, Response
from flask_cors import CORS
import time
from datetime import datetime
from arduino_controller import ArduinoController
from camera_controller import CameraController
from teammate_sender import TeammateSender

app = Flask(__name__)
CORS(app)
# 初始化控制器
arduino = ArduinoController()
camera = CameraController()
teammate = TeammateSender("http://192.168.235.41:5000")

# 存储角度数据
latest_angles = {
    'angles': None,
    'timestamp': None,
    'status': '等待数据'
}

@app.route('/')
def index():
    return render_template('index.html', data=latest_angles)

@app.route('/video')
def video_page():
    """视频流页面"""
    return render_template('video_stream.html')

@app.route('/api/receive_angles', methods=['POST'])
def receive_angles():
    """接收队友发送的角度数据"""
    try:
        data = request.get_json()
        if not data or 'angles' not in data:
            return jsonify({'success': False, 'error': '数据格式错误'})
        
        angles = data['angles']
        
        # 验证角度数据
        if len(angles) != 4:
            return jsonify({'success': False, 'error': '需要4个角度值'})
        
        for i, angle in enumerate(angles):
            if not isinstance(angle, (int, float)) or not (0 <= angle <= 180):
                return jsonify({'success': False, 'error': f'角度{i+1}无效'})
        
        # 更新数据
        latest_angles['angles'] = angles
        latest_angles['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        latest_angles['status'] = '已接收角度数据'
        
        print(f"收到角度数据: {angles}")
        return jsonify({'success': True, 'message': '角度数据已接收'})
    
    except Exception as e:
        print(f"处理角度数据出错: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get_status')
def get_status():
    """获取当前状态"""
    return jsonify(latest_angles)

@app.route('/start_rotation', methods=['POST'])
def start_rotation():
    """开始两阶段旋转：完整旋转拍照 + 角度精确旋转"""
    try:
        print("开始两阶段旋转任务...")
        
        # 先停止视频流（如果正在运行）
        camera.stop_streaming()
        time.sleep(1)  # 给一点时间停止
        
        if not camera.initialize_camera():
            return "错误: 无法初始化相机"
        
        # 阶段1：完整旋转拍照
        print("=== 阶段1：完整旋转拍照 ===")
        for i in range(90):
            rotation_number = i + 1
            print(f"旋转 {rotation_number}/90...")
            
            success = arduino.send_rotate()
            if not success:
                camera.release_camera()
                return f"错误: 旋转命令{rotation_number}失败"
            
            if not arduino.recieve_end(timeout=10):
                camera.release_camera()
                return f"错误: 旋转{rotation_number}未收到END信号"
            
            # 拍照并发送
            photo_path = camera.take_rotation_photo(rotation_number)
            if photo_path:
                teammate.send_photo(photo_path, rotation_number, {
                    'rotation_type': 'full_rotation',
                    'progress': f"{rotation_number}/90"
                })
        arduino.return_start() 
        print("=== 阶段2：等待角度数据 ===")
        
        # 等待角度数据
        wait_timeout = 300  # 5分钟
        start_time = time.time()
        
        while True:
            if time.time() - start_time > wait_timeout:
                camera.release_camera()
                return "错误: 等待角度数据超时"
            
            if latest_angles['angles'] is not None:
                angles = latest_angles['angles']
                print(f"收到角度数据: {angles}")
                break
            
            time.sleep(1)
        
        print("=== 阶段3：角度精确旋转 ===")
        
        # 角度旋转
        for i, angle in enumerate(angles):
            angle_number = i + 1
            print(f"角度旋转 {angle_number}/4 ({angle}度)...")
            
            if not arduino.send_single_angle(angle):
                camera.release_camera()
                return f"错误: 发送角度{angle_number}失败"
            
            if not arduino.recieve_end(timeout=30):
                camera.release_camera()
                return f"错误: 角度{angle_number}旋转超时"
            
        
        camera.release_camera()
        print("=== 旋转任务完成 ===")
        arduino.return_start()  
        return "旋转任务完成"
        
    except Exception as e:
        print(f"旋转任务出错: {e}")
        camera.release_camera()
        return f"错误: {str(e)}"

@app.route('/clear_angles', methods=['POST'])
def clear_angles():
    """清除角度数据"""
    latest_angles['angles'] = None
    latest_angles['timestamp'] = None
    latest_angles['status'] = '等待数据'
    return "角度数据已清除"

@app.route('/api/video_feed')
def video_feed():
    """视频流接口"""
    try:
        if not camera.start_streaming():
            return "无法启动视频流", 500
        
        return Response(camera.generate_frames(),
                       mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"视频流出错: {e}")
        return f"视频流错误: {str(e)}", 500

@app.route('/api/start_stream', methods=['POST'])
def start_stream():
    """启动视频流"""
    try:
        if camera.start_streaming():
            return jsonify({'success': True, 'message': '视频流已启动'})
        else:
            return jsonify({'success': False, 'error': '无法启动视频流'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stop_stream', methods=['POST'])
def stop_stream():
    """停止视频流"""
    try:
        camera.stop_streaming()
        return jsonify({'success': True, 'message': '视频流已停止'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stream_status')
def stream_status():
    """获取视频流状态"""
    return jsonify({
        'streaming': camera.streaming,
        'camera_initialized': camera.picam2 is not None
    })

@app.route('/api/camera_status')
def camera_status():
    """获取相机状态"""
    return jsonify(camera.get_camera_status())

if __name__ == '__main__':
    print("启动服务器...")
    print("API地址: http://你的IP:5000/api/receive_angles")
    app.run(host='0.0.0.0', port=5000, debug=False)
