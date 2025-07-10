#!/usr/bin/env python3
"""
Arduino控制器模块
负责与Arduino板子的串口通信
"""

import serial
import time
import os

class ArduinoController:
    def __init__(self):
        self.ser = None
        self.port = None
        self.baudrate = 9600
        self.timeout = 1
        
        # 自动查找并连接Arduino
        self._connect()
    
    def _find_arduino_port(self):
        """自动查找Arduino串口"""
        # Linux常见的串口设备
        possible_ports = [
            '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2',
            '/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2',
            '/dev/ttyS0', '/dev/ttyS1'
        ]
        
        for port in possible_ports:
            if os.path.exists(port):
                try:
                    # 尝试打开端口
                    test_ser = serial.Serial(port, self.baudrate, timeout=self.timeout)
                    test_ser.close()
                    print(f"找到可用串口: {port}")
                    return port
                except Exception as e:
                    print(f"端口 {port} 测试失败: {e}")
                    continue
        
        print("警告: 未找到可用的串口设备，将使用模拟模式")
        return None
    
    def _connect(self):
        """连接到Arduino"""
        self.port = self._find_arduino_port()
        
        if self.port:
            try:
                self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
                time.sleep(2)  # 等待Arduino启动
                print(f"Arduino已连接: {self.port}")
                return True
            except Exception as e:
                print(f"连接Arduino失败: {e}")
                self.ser = None
                return False
        else:
            print("Arduino未连接，将在模拟模式下运行")
            return False
    
    def is_connected(self):
        """检查是否已连接"""
        return self.ser is not None and self.ser.is_open
    
    def send_angles(self, angles):
        """发送角度数据到Arduino"""
        if not self.is_connected():
            print("Arduino未连接，使用模拟模式")
            print(f"模拟发送角度: {angles}")
            # 模拟发送过程
            for i, angle in enumerate(angles):
                print(f"  模拟发送角度{i+1}: {angle}°")
            print("模拟发送完成")
            return True
        
        try:
            print(f"发送角度到Arduino: {angles}")
            
            for i, angle in enumerate(angles):
                # 发送角度值
                command = f"{angle}\n"
                self.ser.write(command.encode('utf-8'))
                print(f"  发送角度{i+1}: {angle}°")
                time.sleep(1.5)  # 给Arduino时间处理
            
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
