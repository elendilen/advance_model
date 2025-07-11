#!/usr/bin/env python3
"""
队友使用脚本 - 发送角度数据到树莓派
增加照片发送功能
"""

import requests
import json
import base64
import os
from datetime import datetime

# 配置树莓派IP地址 - 请修改为实际IP
RASPBERRY_PI_IP = "192.168.235.170"  # 修改为你的树莓派IP
API_URL = f"http://{RASPBERRY_PI_IP}:5000/api/receive_angles"

class TeammateSender:
    def __init__(self, teammate_url=None):
        self.teammate_url = teammate_url or "http://192.168.235.41:5000"  # 队友的IP地址，需要根据实际情况修改
        self.timeout = 10
    
    def set_teammate_url(self, url):
        """设置队友的URL"""
        self.teammate_url = url
        print(f"队友URL设置为: {self.teammate_url}")
    
    def encode_image_to_base64(self, image_path):
        """将图片编码为base64字符串"""
        try:
            with open(image_path, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
        except Exception as e:
            print(f"编码图片失败: {e}")
            return None
    
    def send_photo(self, photo_path, rotation_number=None, additional_data=None):
        """发送照片给队友"""
        if not os.path.exists(photo_path):
            print(f"照片文件不存在: {photo_path}")
            return False
        
        try:
            # 编码图片
            image_base64 = self.encode_image_to_base64(photo_path)
            if not image_base64:
                return False
            
            # 准备发送的数据
            data = {
                'image': image_base64,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'filename': os.path.basename(photo_path),
                'rotation_number': rotation_number,
                'sender': 'advance_model_camera'
            }
            
            # 添加额外数据
            if additional_data:
                data.update(additional_data)
            
            # 发送POST请求
            response = requests.post(
                f"{self.teammate_url}/api/receive_photo",
                json=data,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', False):
                    print(f"照片发送成功: {photo_path} -> {self.teammate_url}")
                    return True
                else:
                    print(f"队友处理照片失败: {result.get('error', '未知错误')}")
                    return False
            else:
                print(f"发送照片失败，状态码: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"网络请求失败: {e}")
            return False
        except Exception as e:
            print(f"发送照片时出错: {e}")
            return False
    
    def send_rotation_status(self, rotation_number, status, photo_path=None):
        """发送旋转状态信息"""
        try:
            data = {
                'rotation_number': rotation_number,
                'status': status,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'sender': 'advance_model_camera'
            }
            
            if photo_path and os.path.exists(photo_path):
                # 如果有照片，一起发送
                return self.send_photo(photo_path, rotation_number, {
                    'rotation_status': status
                })
            else:
                # 只发送状态信息
                response = requests.post(
                    f"{self.teammate_url}/api/receive_status",
                    json=data,
                    timeout=self.timeout,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    print(f"状态发送成功: 旋转{rotation_number} - {status}")
                    return True
                else:
                    print(f"发送状态失败，状态码: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"发送状态时出错: {e}")
            return False
    
    def test_connection(self):
        """测试与队友的连接"""
        try:
            response = requests.get(
                f"{self.teammate_url}/api/ping",
                timeout=5
            )
            if response.status_code == 200:
                print(f"与队友连接正常: {self.teammate_url}")
                return True
            else:
                print(f"队友连接异常，状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"连接测试失败: {e}")
            return False

# 配置树莓派IP地址 - 请修改为实际IP
RASPBERRY_PI_IP = "192.168.235.170"  # 修改为你的树莓派IP
API_URL = f"http://{RASPBERRY_PI_IP}:5000/api/receive_angles"

def send_angles(angle1, angle2, angle3, angle4):
    """
    发送4个角度到树莓派Arduino系统
    
    参数:
        angle1-angle4: 四个角度值，范围0-180度
    
    返回:
        bool: 发送是否成功
    """
    angles = [angle1, angle2, angle3, angle4]
    
    # 验证角度范围
    for i, angle in enumerate(angles):
        if not (0 <= angle <= 180):
            print(f"错误: 角度{i+1}超出范围(0-180): {angle}")
            return False
    
    try:
        print(f"发送角度到树莓派: {angles}")
        
        # 发送POST请求
        response = requests.post(
            API_URL,
            json={"angles": angles},
            timeout=10
        )
        
        # 解析响应
        result = response.json()
        
        if result.get('success'):
            print(f"✅ 发送成功: {result.get('message')}")
            return True
        else:
            print(f"❌ 发送失败: {result.get('error')}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接失败: 无法连接到 {API_URL}")
        print("请检查:")
        print("1. 树莓派IP地址是否正确")
        print("2. 树莓派Flask服务是否运行")
        print("3. 网络连接是否正常")
        return False
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False

def test_connection():
    """测试连接"""
    try:
        response = requests.get(f"http://{RASPBERRY_PI_IP}:5000/api/get_status", timeout=5)
        if response.status_code == 200:
            print(f"✅ 连接成功: {API_URL}")
            return True
        else:
            print(f"❌ 连接失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False

# 使用示例
if __name__ == "__main__":
    print("队友角度发送脚本")
    print("=" * 30)
    
    # 测试连接
    if not test_connection():
        print("\n请修改脚本中的 RASPBERRY_PI_IP 为正确的树莓派IP地址")
        exit(1)
    
    print("\n连接正常，可以发送角度数据")
    
    # 示例：发送角度数据
    # 你可以在这里调用 send_angles() 函数
    
    # 示例1: 直接发送固定角度
    send_angles(90, 45, 135, 60)
    
    # 示例2: 从你的计算结果发送
    # my_calculated_angles = your_calculation_function()
    # send_angles(my_calculated_angles[0], my_calculated_angles[1], 
    #            my_calculated_angles[2], my_calculated_angles[3])
    
    print("\n完成！")
    print(f"你可以在浏览器中查看: http://{RASPBERRY_PI_IP}:5000")
