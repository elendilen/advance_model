#!/usr/bin/env python3
"""
Arduino控制器模块
负责与Arduino板子的串口通信
"""

import serial
import time

class ArduinoController:
    def __init__(self):
        self.ser = None
        self.port = None
        self.baudrate = 9600
        self.timeout = 1
        self._connect()
    
    
    def _connect(self):
        """连接到Arduino"""
        self.port = "/dev/ttyS0"     
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            print(f"成功连接到Arduino: {self.port} (波特率: {self.baudrate})")
            time.sleep(2)  # 等待Arduino初始化
    
    def is_connected(self):
        """检查是否已连接"""
        return self.ser is not None and self.ser.is_open
    
    def send_angles(self, angles):
        """发送角度数据到Arduino"""       
        try:
            print(f"发送角度到Arduino: {angles}")
            
            for i, angle in enumerate(angles):
                # 发送角度值
                command = f"{angle}"
                self.ser.write(command.encode('utf-8'))
                print(f"  发送角度{i+1}: {angle}°")
                time.sleep(10)  # 给Arduino时间处理
            
            print("所有角度发送完成")
            return True
            
        except Exception as e:
            print(f"发送数据到Arduino时出错: {e}")
            return False
    
    def close(self):
        """关闭串口连接"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Arduino连接已关闭")
    
    def __del__(self):
        """析构函数，确保串口正确关闭"""
        self.close()
