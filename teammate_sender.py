#!/usr/bin/env python3
"""
队友使用脚本 - 发送角度数据到树莓派
"""

import requests
import json

# 配置树莓派IP地址 - 请修改为实际IP
RASPBERRY_PI_IP = "192.168.217.170"  # 修改为你的树莓派IP
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
