from flask import Flask, request, render_template, redirect, jsonify
import serial
import time
import json
from datetime import datetime
from arduino_controller import ArduinoController

app = Flask(__name__)

# 初始化Arduino控制器
arduino = ArduinoController()

# 存储最新接收的角度数据
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
    """接收队友发送的角度数据并自动传给Arduino"""
    try:
        data = request.get_json()
        if not data or 'angles' not in data:
            return jsonify({'success': False, 'error': '数据格式错误，需要angles字段'})
        
        angles = data['angles']
        
        # 验证角度数据
        if len(angles) != 4:
            return jsonify({'success': False, 'error': '需要4个角度值'})
        
        for i, angle in enumerate(angles):
            if not isinstance(angle, (int, float)) or not (0 <= angle <= 180):
                return jsonify({'success': False, 'error': f'角度{i+1}无效: {angle}'})
        
        # 更新存储的数据
        latest_angles['angles'] = angles
        latest_angles['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        latest_angles['status'] = '正在发送...'
        
        print(f"收到队友角度数据: {angles}")
        
        # 发送到Arduino
        success = arduino.send_angles(angles)
        
        if success:
            latest_angles['status'] = '发送成功'
            return jsonify({'success': True, 'message': '角度已发送到Arduino'})
        else:
            latest_angles['status'] = '发送失败'
            return jsonify({'success': False, 'error': 'Arduino通信失败'})
    
    except Exception as e:
        latest_angles['status'] = f'错误: {str(e)}'
        print(f"处理角度数据时出错: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get_status')
def get_status():
    """获取当前状态"""
    return jsonify(latest_angles)

@app.route('/send_angles', methods=['POST'])
def send_angles():
    """网页手动发送角度"""
    try:
        angles = [
            int(request.form['angle1']),
            int(request.form['angle2']),
            int(request.form['angle3']),
            int(request.form['angle4'])
        ]
        
        # 验证角度范围
        for angle in angles:
            if not (0 <= angle <= 180):
                return f"错误：角度值必须在0-180之间"
        
        print(f"网页手动发送: {angles}")
        
        # 发送到Arduino
        success = arduino.send_angles(angles)
        
        if success:
            # 更新状态
            latest_angles['angles'] = angles
            latest_angles['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            latest_angles['status'] = '手动发送成功'
            return redirect('/')
        else:
            return "错误：Arduino通信失败"
    
    except Exception as e:
        return f"错误：{e}"

if __name__ == '__main__':
    print("启动Flask服务器...")
    print("队友可以发送POST请求到: http://你的IP:5000/api/receive_angles")
    print("数据格式: {\"angles\": [角度1, 角度2, 角度3, 角度4]}")
    app.run(host='0.0.0.0', port=5000, debug=True)
