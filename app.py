from flask import Flask, request, render_template, redirect, jsonify
import time
from datetime import datetime
from arduino_controller import ArduinoController
from camera_controller import CameraController
from teammate_sender import TeammateSender

app = Flask(__name__)

# 初始化控制器
arduino = ArduinoController()
camera = CameraController()
teammate = TeammateSender("http://192.168.1.100:5000")

# 存储角度数据
latest_angles = {
    'angles': None,
    'timestamp': None,
    'status': '等待数据'
}

@app.route('/')
def index():
    return render_template('index.html', data=latest_angles)

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
            
            # 拍照并发送
            photo_name = f"angle_{angle_number}_{angle}deg.jpg"
            photo_path = camera.take_photo(photo_name)
            if photo_path:
                teammate.send_photo(photo_path, angle_number, {
                    'rotation_type': 'angle_rotation',
                    'angle_value': angle
                })
        
        camera.release_camera()
        print("=== 旋转任务完成 ===")
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

if __name__ == '__main__':
    print("启动服务器...")
    print("API地址: http://你的IP:5000/api/receive_angles")
    app.run(host='0.0.0.0', port=5000, debug=False)
