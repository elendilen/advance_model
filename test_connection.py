#!/usr/bin/env python3
"""
网络连接测试工具
"""

import requests
import json
import base64
import os
from datetime import datetime

def test_basic_connection(url):
    """测试基本连接"""
    print(f"测试连接到: {url}")
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ 连接成功，状态码: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def test_photo_api(teammate_url):
    """测试照片发送API"""
    print(f"\n测试照片API: {teammate_url}/api/receive_photo")
    
    # 创建一个小测试图片
    test_image_data = b"fake_image_data_for_testing"
    test_image_base64 = base64.b64encode(test_image_data).decode('utf-8')
    
    data = {
        'image': test_image_base64,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'filename': 'test_photo.jpg',
        'rotation_number': 1,
        'sender': 'connection_test'
    }
    
    try:
        response = requests.post(
            f"{teammate_url}/api/receive_photo",
            json=data,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success', False):
                print("✅ 照片API测试成功")
                return True
            else:
                print(f"❌ API返回错误: {result.get('error', '未知错误')}")
        else:
            print(f"❌ HTTP错误，状态码: {response.status_code}")
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    return False

def test_real_photo(teammate_url, photo_path):
    """测试发送真实照片"""
    if not os.path.exists(photo_path):
        print(f"❌ 照片文件不存在: {photo_path}")
        return False
    
    print(f"\n测试发送真实照片: {photo_path}")
    
    try:
        # 编码图片
        with open(photo_path, 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        data = {
            'image': image_base64,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'filename': os.path.basename(photo_path),
            'rotation_number': 999,
            'sender': 'connection_test',
            'rotation_type': 'test'
        }
        
        file_size = len(image_base64)
        print(f"照片大小: {file_size} 字符 ({file_size/1024/1024:.2f} MB base64)")
        
        response = requests.post(
            f"{teammate_url}/api/receive_photo",
            json=data,
            timeout=30,  # 增加超时时间
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success', False):
                print("✅ 真实照片发送成功")
                return True
            else:
                print(f"❌ API返回错误: {result.get('error', '未知错误')}")
        
    except Exception as e:
        print(f"❌ 发送真实照片失败: {e}")
    
    return False

if __name__ == "__main__":
    teammate_url = "http://192.168.235.41:5000"
    
    print("🔍 开始网络连接诊断...")
    
    # 测试基本连接
    if test_basic_connection(teammate_url):
        # 测试照片API
        if test_photo_api(teammate_url):
            # 查找一张真实照片进行测试
            photo_dir = "photos"
            if os.path.exists(photo_dir):
                photos = [f for f in os.listdir(photo_dir) if f.endswith('.jpg')]
                if photos:
                    test_photo_path = os.path.join(photo_dir, photos[0])
                    test_real_photo(teammate_url, test_photo_path)
                else:
                    print("📝 photos目录中没有找到jpg照片")
            else:
                print("📝 photos目录不存在")
    
    print("\n🏁 诊断完成")
