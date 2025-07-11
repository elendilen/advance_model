#!/usr/bin/env python3
"""
相机控制器模块
负责拍照功能
"""

from picamera2 import Picamera2
import os
from datetime import datetime
import time

class CameraController:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.picam2 = None
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
            self.picam2 = Picamera2()
            
            # 配置相机
            config = self.picam2.create_still_configuration(
                main={"size": (1920, 1080)},  # 高分辨率拍照
                lores={"size": (640, 480)},   # 低分辨率预览
                display="lores"
            )
            self.picam2.configure(config)
            
            # 启动相机
            self.picam2.start()
            time.sleep(2)  # 等待相机稳定
            
            print(f"PiCamera2 初始化成功")
            return True
        except Exception as e:
            print(f"初始化相机失败: {e}")
            return False
    
    def take_photo(self, photo_name=None):
        """拍照并保存"""
        if not self.picam2:
            if not self.initialize_camera():
                return None
        
        try:
            # 生成文件名
            if not photo_name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                photo_name = f"photo_{timestamp}.jpg"
            
            photo_path = os.path.join(self.photos_dir, photo_name)
            
            # 拍照并保存
            self.picam2.capture_file(photo_path)
            print(f"照片已保存: {photo_path}")
            return photo_path
                
        except Exception as e:
            print(f"拍照时出错: {e}")
            return None
    
    def take_rotation_photo(self, rotation_number):
        """为特定旋转编号拍照"""
        photo_name = f"rotation_{rotation_number:03d}.jpg"
        return self.take_photo(photo_name)
    
    def release_camera(self):
        """释放摄像头资源"""
        if self.picam2:
            try:
                self.picam2.stop()
                self.picam2.close()
                print("相机资源已释放")
            except Exception as e:
                print(f"释放相机资源时出错: {e}")
            finally:
                self.picam2 = None
    
    def __del__(self):
        """析构函数"""
        self.release_camera()
