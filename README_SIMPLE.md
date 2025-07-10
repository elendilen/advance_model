# 角度控制系统

这是一个简洁的系统，用于接收队友的四个角度信息并自动传给Arduino板子。

## 文件结构

- `app.py` - 主Flask应用
- `arduino_controller.py` - Arduino串口通信模块
- `teammate_sender.py` - 队友使用的发送脚本
- `templates/index.html` - 网页界面

## 快速开始

### 1. 启动系统
```bash
cd /home/lenovo/advance_model
python app.py
```

### 2. 队友发送角度数据

**方法1: 使用Python脚本**
```python
# 队友修改 teammate_sender.py 中的IP地址，然后运行：
python teammate_sender.py
```

**方法2: 直接发送HTTP请求**
```bash
curl -X POST http://你的IP:5000/api/receive_angles \
     -H "Content-Type: application/json" \
     -d '{"angles": [90, 45, 135, 60]}'
```

## API接口

### 接收角度数据
- **URL**: `/api/receive_angles`
- **方法**: POST
- **数据格式**: `{"angles": [角度1, 角度2, 角度3, 角度4]}`
- **功能**: 接收角度数据并自动发送到Arduino

### 获取状态
- **URL**: `/api/get_status`
- **方法**: GET
- **功能**: 获取最新的角度数据和发送状态

## 系统流程

```
队友计算角度 → 发送HTTP请求 → Flask接收 → Arduino控制器 → 串口通信 → Arduino舵机
```

## 特性

✅ **自动Arduino连接** - 自动检测可用串口
✅ **实时状态显示** - 网页显示最新的角度数据和状态
✅ **简洁API** - 只有一个主要接口
✅ **错误处理** - 完善的数据验证和错误提示
✅ **模拟模式** - Arduino未连接时使用模拟模式

## 网页功能

访问 `http://你的IP:5000` 可以看到：
- 队友发送的最新角度数据
- 发送状态（成功/失败/等待）
- 手动发送角度的表单
- 队友使用说明
