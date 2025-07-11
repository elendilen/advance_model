#!/usr/bin/env python3
"""
相机控制器模块
负责拍照功能
"""

import cv2
import os
from datetime import datetime

class CameraController:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.photos_dir = "photos"
        self._ensure_photos_dir()
    
    def _ensure_photos_dir(self):
        """确保照片目录存在"""
        if not os.path.exists(self.photos_dir):
            os.makedirs(self.photos_dir)
            print(f"创建照片目录: {self.photos_dir}")
    
    def initialize_camera(self):
        """初始化摄像头"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                print(f"无法打开摄像头 {self.camera_index}")
                return False
            
            # 设置摄像头参数
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            print(f"摄像头 {self.camera_index} 初始化成功")
            return True
        except Exception as e:
            print(f"初始化摄像头失败: {e}")
            return False
    
    def take_photo(self, photo_name=None):
        """拍照并保存"""
        if not self.cap or not self.cap.isOpened():
            if not self.initialize_camera():
                return None
        
        try:
            # 读取几帧以确保摄像头稳定
            for _ in range(5):
                ret, frame = self.cap.read()
                if not ret:
                    print("无法从摄像头读取画面")
                    return None
            
            # 生成文件名
            if not photo_name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                photo_name = f"photo_{timestamp}.jpg"
            
            photo_path = os.path.join(self.photos_dir, photo_name)
            
            # 保存照片
            success = cv2.imwrite(photo_path, frame)
            if success:
                print(f"照片已保存: {photo_path}")
                return photo_path
            else:
                print("保存照片失败")
                return None
                
        except Exception as e:
            print(f"拍照时出错: {e}")
            return None
    
    def take_rotation_photo(self, rotation_number):
        """为特定旋转编号拍照"""
        photo_name = f"rotation_{rotation_number:03d}.jpg"
        return self.take_photo(photo_name)
    
    def release_camera(self):
        """释放摄像头资源"""
        if self.cap:
            self.cap.release()
            print("摄像头资源已释放")
    
    def __del__(self):
        """析构函数"""
        self.release_camera()
