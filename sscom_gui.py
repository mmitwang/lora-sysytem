#!/usr/bin/env python3
# SSCOM模拟器 - 科技感GUI版本
# 支持TCP客户端模式、串口模式、HEX显示和发送、传感器数据解析

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import socket
import time
from datetime import datetime
import threading
import re
import serial
import serial.tools.list_ports

class SSCOM_GUI:
    def __init__(self, root):
        """初始化GUI"""
        self.root = root
        self.root.title("SSCOM模拟器 - TCP客户端")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # 设置科技感主题
        self.setup_theme()
        
        # 初始化变量
        self.sock = None
        self.connected = False
        self.stop_event = threading.Event()
        self.receive_thread = None
        self.receive_buffer = b""  # 接收缓冲区，用于缓存分次接收的数据
        self.serial_port = None  # 串口对象
        
        # 创建UI
        self.create_widgets()
        
        # 设置关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def get_available_serial_ports(self):
        """获取可用串口列表"""
        try:
            ports = []
            for port in serial.tools.list_ports.comports():
                ports.append(port.device)
            return ports
        except:
            return []
    
    def on_mode_change(self):
        """模式更改处理"""
        mode = self.mode_var.get()
        if mode == "TCP":
            self.log_message("切换到TCP模式")
        else:
            self.log_message("切换到串口模式")
            # 重新扫描可用串口
            self.serial_port_combobox['values'] = self.get_available_serial_ports()
    
    def setup_theme(self):
        """设置蓝色商务主题"""
        # 主窗口背景
        self.root.configure(bg="#f8f9fa")
        
        # 创建样式
        self.style = ttk.Style()
        
        # 配置全局样式
        self.style.configure(
            "TLabel",
            background="#f8f9fa",
            foreground="#2c3e50",
            font=("Microsoft YaHei", 10)
        )
        
        self.style.configure(
            "TButton",
            background="#e3f2fd",
            foreground="#000000",
            font=("Microsoft YaHei", 10, "bold"),
            borderwidth=1,
            relief="solid"
        )
        
        self.style.map(
            "TButton",
            background=[("active", "#bbdefb")],
            foreground=[("active", "#000000")]
        )
        
        self.style.configure(
            "TEntry",
            background="#ffffff",
            foreground="#2c3e50",
            font=("Microsoft YaHei", 10),
            borderwidth=1,
            relief="solid"
        )
        
        self.style.configure(
            "TNotebook",
            background="#f8f9fa",
            foreground="#3498db"
        )
        
        self.style.configure(
            "TNotebook.Tab",
            background="#e3f2fd",
            foreground="#1a5276",
            font=("Microsoft YaHei", 10, "bold"),
            padding=[10, 5]
        )
        
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", "#21618c")],
            foreground=[("selected", "#ffffff")]
        )
        
        # 配置标签框架样式
        self.style.configure(
            "TLabelframe",
            background="#f8f9fa",
            foreground="#2c3e50",
            font=("Microsoft YaHei", 10, "bold")
        )
        
        self.style.configure(
            "TLabelframe.Label",
            background="#f8f9fa",
            foreground="#2c3e50",
            font=("Microsoft YaHei", 10, "bold")
        )
    
    def create_widgets(self):
        """创建UI组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部连接设置区域
        connect_frame = ttk.LabelFrame(main_frame, text="连接设置", padding="10")
        connect_frame.pack(fill=tk.X, pady=5)
        
        # 传感器选择
        ttk.Label(connect_frame, text="传感器模块:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.sensor_var = tk.StringVar()
        self.sensor_combobox = ttk.Combobox(connect_frame, textvariable=self.sensor_var, width=15, values=["光照模块", "温湿度模块", "温振模块"])
        self.sensor_combobox.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        self.sensor_combobox.current(0)
        self.sensor_combobox.bind("<<ComboboxSelected>>", self.on_sensor_select)
        
        # 模式选择
        ttk.Label(connect_frame, text="连接模式:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.mode_var = tk.StringVar(value="TCP")
        ttk.Radiobutton(connect_frame, text="TCP", variable=self.mode_var, value="TCP", command=self.on_mode_change).grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Radiobutton(connect_frame, text="串口", variable=self.mode_var, value="Serial", command=self.on_mode_change).grid(row=1, column=2, sticky=tk.W, pady=5, padx=5)
        
        # TCP设置
        ttk.Label(connect_frame, text="服务器IP:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.ip_entry = ttk.Entry(connect_frame, width=20)
        self.ip_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        self.ip_entry.insert(0, "192.168.0.80")
        
        # 端口
        ttk.Label(connect_frame, text="端口:").grid(row=2, column=2, sticky=tk.W, pady=5, padx=5)
        self.port_entry = ttk.Entry(connect_frame, width=10)
        self.port_entry.grid(row=2, column=3, sticky=tk.W, pady=5, padx=5)
        self.port_entry.insert(0, "10125")
        
        # 串口设置
        ttk.Label(connect_frame, text="串口:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        self.serial_port_var = tk.StringVar()
        self.serial_port_combobox = ttk.Combobox(connect_frame, textvariable=self.serial_port_var, width=15)
        self.serial_port_combobox.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        self.serial_port_combobox['values'] = self.get_available_serial_ports()
        
        # 波特率
        ttk.Label(connect_frame, text="波特率:").grid(row=3, column=2, sticky=tk.W, pady=5, padx=5)
        self.baudrate_var = tk.StringVar(value="9600")
        self.baudrate_combobox = ttk.Combobox(connect_frame, textvariable=self.baudrate_var, width=10, values=["9600", "115200"])
        self.baudrate_combobox.grid(row=3, column=3, sticky=tk.W, pady=5, padx=5)
        
        # 连接按钮
        self.connect_btn = ttk.Button(connect_frame, text="连接", command=self.connect)
        self.connect_btn.grid(row=2, column=4, sticky=tk.W, pady=5, padx=5)
        
        # 断开按钮
        self.disconnect_btn = ttk.Button(connect_frame, text="断开", command=self.disconnect, state=tk.DISABLED)
        self.disconnect_btn.grid(row=2, column=5, sticky=tk.W, pady=5, padx=5)
        
        # 连接状态
        self.status_var = tk.StringVar()
        self.status_var.set("状态: 未连接")
        ttk.Label(connect_frame, textvariable=self.status_var).grid(row=3, column=4, columnspan=2, sticky=tk.W, pady=5, padx=10)
        
        # 传感器配置
        self.sensor_configs = {
            "光照模块": {
                "port": "10125",
                "query_frame": "56 78 01 03 00 00 00 08 44 0C"
            },
            "温湿度模块": {
                "port": "10125",
                "query_frame": "00 02 01 03 00 00 00 02 C4 0B"
            },
            "温振模块": {
                "port": "10125",
                "query_frame": "00 03 01 03 00 00 00 26 C4 10"
            }
        }
        
        # 中间数据区域
        data_frame = ttk.LabelFrame(main_frame, text="数据交换", padding="10")
        data_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 数据发送区域
        send_frame = ttk.LabelFrame(data_frame, text="发送数据", padding="10")
        send_frame.pack(fill=tk.X, pady=5)
        
        # HEX输入
        ttk.Label(send_frame, text="HEX数据:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.send_entry = ttk.Entry(send_frame, width=60)
        self.send_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        self.send_entry.insert(0, "56 78 01 03 00 00 00 08 44 0C")
        
        # 发送按钮
        self.send_btn = ttk.Button(send_frame, text="发送", command=self.send_data, state=tk.DISABLED)
        self.send_btn.grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)
        
        # 数据接收区域
        receive_frame = ttk.LabelFrame(data_frame, text="接收数据", padding="10")
        receive_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 接收数据工具栏
        receive_toolbar = ttk.Frame(receive_frame)
        receive_toolbar.pack(fill=tk.X, pady=5)
        
        # 清空按钮
        self.clear_btn = ttk.Button(receive_toolbar, text="清空", command=self.clear_receive_data)
        self.clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # 接收数据显示
        self.receive_text = scrolledtext.ScrolledText(
            receive_frame,
            width=80,
            height=15,
            font=("Consolas", 10),
            bg="#ffffff",
            fg="#2c3e50",
            insertbackground="#2c3e50",
            relief="solid",
            borderwidth=1
        )
        self.receive_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 底部传感器数据解析区域
        parse_frame = ttk.LabelFrame(main_frame, text="传感器数据解析", padding="10")
        parse_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建滚动条
        parse_canvas = tk.Canvas(parse_frame)
        parse_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        parse_scrollbar = ttk.Scrollbar(parse_frame, orient=tk.VERTICAL, command=parse_canvas.yview)
        parse_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        parse_canvas.configure(yscrollcommand=parse_scrollbar.set)
        parse_canvas.bind('<Configure>', lambda e: parse_canvas.configure(scrollregion=parse_canvas.bbox('all')))
        
        # 创建笔记本框架
        notebook_frame = ttk.Frame(parse_canvas)
        parse_canvas.create_window((0, 0), window=notebook_frame, anchor='nw')
        
        # 创建笔记本
        self.parse_notebook = ttk.Notebook(notebook_frame)
        self.parse_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 光照模块解析标签页
        light_tab = ttk.Frame(self.parse_notebook)
        self.parse_notebook.add(light_tab, text="光照模块")
        
        # 光照模块解析内容
        light_grid = ttk.Frame(light_tab, padding="10")
        light_grid.pack(fill=tk.BOTH, expand=True)
        
        # 状态
        ttk.Label(light_grid, text="状态: ").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.light_status_var = tk.StringVar()
        self.light_status_var.set("- - -")
        ttk.Label(light_grid, textvariable=self.light_status_var).grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 温度
        ttk.Label(light_grid, text="温度: ").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.light_temp_var = tk.StringVar()
        self.light_temp_var.set("- - - °C")
        ttk.Label(light_grid, textvariable=self.light_temp_var).grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 湿度
        ttk.Label(light_grid, text="湿度: ").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.light_humidity_var = tk.StringVar()
        self.light_humidity_var.set("- - - %")
        ttk.Label(light_grid, textvariable=self.light_humidity_var).grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # CO2浓度
        ttk.Label(light_grid, text="CO2浓度: ").grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        self.light_co2_var = tk.StringVar()
        self.light_co2_var.set("- - - ppm")
        ttk.Label(light_grid, textvariable=self.light_co2_var).grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 气压
        ttk.Label(light_grid, text="气压: ").grid(row=4, column=0, sticky=tk.W, pady=5, padx=5)
        self.light_pressure_var = tk.StringVar()
        self.light_pressure_var.set("- - - hPa")
        ttk.Label(light_grid, textvariable=self.light_pressure_var).grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 光照强度
        ttk.Label(light_grid, text="光照强度: ").grid(row=5, column=0, sticky=tk.W, pady=5, padx=5)
        self.light_light_var = tk.StringVar()
        self.light_light_var.set("- - - Lux")
        ttk.Label(light_grid, textvariable=self.light_light_var).grid(row=5, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 温湿度模块解析标签页
        temp_hum_tab = ttk.Frame(self.parse_notebook)
        self.parse_notebook.add(temp_hum_tab, text="温湿度模块")
        
        # 温湿度模块解析内容
        temp_hum_grid = ttk.Frame(temp_hum_tab, padding="10")
        temp_hum_grid.pack(fill=tk.BOTH, expand=True)
        
        # 状态
        ttk.Label(temp_hum_grid, text="状态: ").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.temp_hum_status_var = tk.StringVar()
        self.temp_hum_status_var.set("- - -")
        ttk.Label(temp_hum_grid, textvariable=self.temp_hum_status_var).grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 温度
        ttk.Label(temp_hum_grid, text="温度: ").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.temp_hum_temp_var = tk.StringVar()
        self.temp_hum_temp_var.set("- - - °C")
        ttk.Label(temp_hum_grid, textvariable=self.temp_hum_temp_var).grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 湿度
        ttk.Label(temp_hum_grid, text="湿度: ").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.temp_hum_humidity_var = tk.StringVar()
        self.temp_hum_humidity_var.set("- - - %")
        ttk.Label(temp_hum_grid, textvariable=self.temp_hum_humidity_var).grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 温振模块解析标签页
        temp_vib_tab = ttk.Frame(self.parse_notebook)
        self.parse_notebook.add(temp_vib_tab, text="温振模块")
        
        # 温振模块解析内容
        temp_vib_grid = ttk.Frame(temp_vib_tab, padding="10")
        temp_vib_grid.pack(fill=tk.BOTH, expand=True)
        
        # 状态
        ttk.Label(temp_vib_grid, text="状态: ").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.temp_vib_status_var = tk.StringVar()
        self.temp_vib_status_var.set("- - -")
        ttk.Label(temp_vib_grid, textvariable=self.temp_vib_status_var).grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 温度
        ttk.Label(temp_vib_grid, text="温度: ").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.temp_vib_temp_var = tk.StringVar()
        self.temp_vib_temp_var.set("- - - °C")
        ttk.Label(temp_vib_grid, textvariable=self.temp_vib_temp_var).grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 振动
        ttk.Label(temp_vib_grid, text="振动: ").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.temp_vib_vibration_var = tk.StringVar()
        self.temp_vib_vibration_var.set("- - - ")
        ttk.Label(temp_vib_grid, textvariable=self.temp_vib_vibration_var).grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 振动速度X轴
        ttk.Label(temp_vib_grid, text="振动速度X轴: ").grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        self.temp_vib_velocity_x_var = tk.StringVar()
        self.temp_vib_velocity_x_var.set("- - - mm/s")
        ttk.Label(temp_vib_grid, textvariable=self.temp_vib_velocity_x_var).grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 振动速度Y轴
        ttk.Label(temp_vib_grid, text="振动速度Y轴: ").grid(row=4, column=0, sticky=tk.W, pady=5, padx=5)
        self.temp_vib_velocity_y_var = tk.StringVar()
        self.temp_vib_velocity_y_var.set("- - - mm/s")
        ttk.Label(temp_vib_grid, textvariable=self.temp_vib_velocity_y_var).grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 振动速度Z轴
        ttk.Label(temp_vib_grid, text="振动速度Z轴: ").grid(row=5, column=0, sticky=tk.W, pady=5, padx=5)
        self.temp_vib_velocity_z_var = tk.StringVar()
        self.temp_vib_velocity_z_var.set("- - - mm/s")
        ttk.Label(temp_vib_grid, textvariable=self.temp_vib_velocity_z_var).grid(row=5, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 振动位移X轴
        ttk.Label(temp_vib_grid, text="振动位移X轴: ").grid(row=6, column=0, sticky=tk.W, pady=5, padx=5)
        self.temp_vib_displacement_x_var = tk.StringVar()
        self.temp_vib_displacement_x_var.set("- - - μm")
        ttk.Label(temp_vib_grid, textvariable=self.temp_vib_displacement_x_var).grid(row=6, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 振动位移Y轴
        ttk.Label(temp_vib_grid, text="振动位移Y轴: ").grid(row=7, column=0, sticky=tk.W, pady=5, padx=5)
        self.temp_vib_displacement_y_var = tk.StringVar()
        self.temp_vib_displacement_y_var.set("- - - μm")
        ttk.Label(temp_vib_grid, textvariable=self.temp_vib_displacement_y_var).grid(row=7, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 振动位移Z轴
        ttk.Label(temp_vib_grid, text="振动位移Z轴: ").grid(row=8, column=0, sticky=tk.W, pady=5, padx=5)
        self.temp_vib_displacement_z_var = tk.StringVar()
        self.temp_vib_displacement_z_var.set("- - - μm")
        ttk.Label(temp_vib_grid, textvariable=self.temp_vib_displacement_z_var).grid(row=8, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 振动加速度X轴
        ttk.Label(temp_vib_grid, text="振动加速度X轴: ").grid(row=9, column=0, sticky=tk.W, pady=5, padx=5)
        self.temp_vib_acceleration_x_var = tk.StringVar()
        self.temp_vib_acceleration_x_var.set("- - - m/s²")
        ttk.Label(temp_vib_grid, textvariable=self.temp_vib_acceleration_x_var).grid(row=9, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 振动加速度Y轴
        ttk.Label(temp_vib_grid, text="振动加速度Y轴: ").grid(row=10, column=0, sticky=tk.W, pady=5, padx=5)
        self.temp_vib_acceleration_y_var = tk.StringVar()
        self.temp_vib_acceleration_y_var.set("- - - m/s²")
        ttk.Label(temp_vib_grid, textvariable=self.temp_vib_acceleration_y_var).grid(row=10, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 振动加速度Z轴
        ttk.Label(temp_vib_grid, text="振动加速度Z轴: ").grid(row=11, column=0, sticky=tk.W, pady=5, padx=5)
        self.temp_vib_acceleration_z_var = tk.StringVar()
        self.temp_vib_acceleration_z_var.set("- - - m/s²")
        ttk.Label(temp_vib_grid, textvariable=self.temp_vib_acceleration_z_var).grid(row=11, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 原始数据标签页
        raw_tab = ttk.Frame(self.parse_notebook)
        self.parse_notebook.add(raw_tab, text="原始数据")
        
        # 原始数据内容
        self.raw_text = scrolledtext.ScrolledText(
            raw_tab,
            width=80,
            height=15,
            font=("Consolas", 10),
            bg="#ffffff",
            fg="#2c3e50",
            insertbackground="#2c3e50",
            relief="solid",
            borderwidth=1
        )
        self.raw_text.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def get_timestamp(self):
        """获取当前时间戳"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    
    def hex_to_bytes(self, hex_str):
        """将十六进制字符串转换为字节流"""
        try:
            # 移除空格
            hex_str = hex_str.replace(' ', '')
            # 检查长度是否为偶数
            if len(hex_str) % 2 != 0:
                hex_str = '0' + hex_str
            # 转换为字节流
            return bytes.fromhex(hex_str)
        except ValueError as e:
            self.log_message(f"错误: 无效的十六进制字符串 - {e}")
            return None
    
    def bytes_to_hex(self, data):
        """将字节流转换为十六进制字符串"""
        return ' '.join([f'{b:02X}' for b in data])
    
    def log_message(self, message):
        """在接收区域记录消息"""
        timestamp = self.get_timestamp()
        self.receive_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.receive_text.see(tk.END)
    
    def connect(self):
        """连接TCP服务器或串口"""
        try:
            mode = self.mode_var.get()
            
            if mode == "TCP":
                # TCP模式
                server_ip = self.ip_entry.get().strip()
                server_port = int(self.port_entry.get().strip())
                
                if not server_ip:
                    messagebox.showerror("错误", "请输入服务器IP地址")
                    return
                
                if server_port < 0 or server_port > 65535:
                    messagebox.showerror("错误", "端口号必须在0-65535之间")
                    return
                
                # 创建TCP套接字
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                self.log_message(f"正在连接到 {server_ip}:{server_port}...")
                
                # 连接服务器
                self.sock.connect((server_ip, server_port))
                
                self.connected = True
                self.stop_event.clear()
                
                # 更新UI状态
                self.status_var.set(f"状态: 已连接到 {server_ip}:{server_port}")
                self.connect_btn.config(state=tk.DISABLED)
                self.disconnect_btn.config(state=tk.NORMAL)
                self.send_btn.config(state=tk.NORMAL)
                
                self.log_message(f"连接成功！本地地址: {self.sock.getsockname()}")
                
                # 启动接收数据线程
                self.receive_thread = threading.Thread(target=self.receive_data)
                self.receive_thread.daemon = True
                self.receive_thread.start()
            else:
                # 串口模式
                port = self.serial_port_var.get().strip()
                baudrate = int(self.baudrate_var.get())
                
                if not port:
                    messagebox.showerror("错误", "请选择串口")
                    return
                
                # 打开串口
                self.serial_port = serial.Serial(
                    port=port,
                    baudrate=baudrate,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=0.5,
                    xonxoff=False,
                    rtscts=False,
                    dsrdtr=False
                )
                
                self.connected = True
                self.stop_event.clear()
                
                # 更新UI状态
                self.status_var.set(f"状态: 已打开串口 {port}")
                self.connect_btn.config(state=tk.DISABLED)
                self.disconnect_btn.config(state=tk.NORMAL)
                self.send_btn.config(state=tk.NORMAL)
                
                self.log_message(f"串口已打开: {port}")
                self.log_message(f"串口配置: 波特率={baudrate}, 数据位=8, 停止位=1, 校验=无")
                
                # 启动接收数据线程
                self.receive_thread = threading.Thread(target=self.receive_data)
                self.receive_thread.daemon = True
                self.receive_thread.start()
                
        except ConnectionRefusedError:
            self.log_message("错误: 连接被拒绝，请检查服务器是否运行")
            messagebox.showerror("错误", "连接被拒绝，请检查服务器是否运行")
        except Exception as e:
            self.log_message(f"错误: {e}")
            messagebox.showerror("错误", str(e))
    
    def disconnect(self):
        """断开连接"""
        try:
            if self.connected:
                self.connected = False
                self.stop_event.set()
                
                # 关闭socket或串口
                if self.sock:
                    self.sock.close()
                    self.sock = None
                
                if self.serial_port:
                    self.serial_port.close()
                    self.serial_port = None
                
                # 清空接收缓冲区
                self.receive_buffer = b""
                
                # 更新UI状态
                self.status_var.set("状态: 未连接")
                self.connect_btn.config(state=tk.NORMAL)
                self.disconnect_btn.config(state=tk.DISABLED)
                self.send_btn.config(state=tk.DISABLED)
                
                self.log_message("连接已断开")
                
        except Exception as e:
            self.log_message(f"错误: {e}")
    
    def receive_data(self):
        """接收数据线程"""
        last_receive_time = time.time()
        zero_count = 0  # 连续接收0字节的计数
        
        while self.connected and not self.stop_event.is_set():
            try:
                mode = self.mode_var.get()
                
                if mode == "TCP":
                    # TCP模式
                    if not self.sock:
                        break
                    
                    # 设置超时，以便能够及时响应停止事件
                    self.sock.settimeout(0.5)
                    data = self.sock.recv(1024)
                    if data:
                        # 检查是否是全0数据
                        if all(b == 0 for b in data):
                            zero_count += 1
                            if zero_count >= 3:
                                # 连续3次接收到全0数据，清空缓冲区
                                if len(self.receive_buffer) > 0:
                                    self.log_message(f"[检测] 连续接收到全0数据，清空缓冲区")
                                    self.receive_buffer = b""
                                zero_count = 0
                            last_receive_time = time.time()
                            continue
                        
                        zero_count = 0  # 重置0字节计数
                        
                        # 将接收到的数据添加到缓冲区
                        self.receive_buffer += data
                        last_receive_time = time.time()
                        
                        # 显示接收到的数据
                        hex_data = self.bytes_to_hex(data)
                        self.log_message(f"[接收] HEX: {hex_data}")
                        self.log_message(f"[接收] 长度: {len(data)}字节，缓冲区总计: {len(self.receive_buffer)}字节")
                        
                        # 更新原始数据标签页
                        self.root.after(0, self.update_raw_data, data)
                        
                        # 尝试解析传感器数据（使用缓冲区中的所有数据）
                        self.root.after(0, self.parse_sensor_data, self.receive_buffer)
                    else:
                        # 检查是否超时（超过2秒没有接收到新数据）
                        if time.time() - last_receive_time > 2:
                            # 超时，清空缓冲区
                            if len(self.receive_buffer) > 0:
                                self.log_message(f"[超时] 超过2秒未接收到新数据，清空缓冲区")
                                self.receive_buffer = b""
                            last_receive_time = time.time()
                else:
                    # 串口模式
                    if not self.serial_port:
                        break
                    
                    # 读取串口数据
                    data = self.serial_port.read(1024)
                    if data:
                        # 检查是否是全0数据
                        if all(b == 0 for b in data):
                            zero_count += 1
                            if zero_count >= 3:
                                # 连续3次接收到全0数据，清空缓冲区
                                if len(self.receive_buffer) > 0:
                                    self.log_message(f"[检测] 连续接收到全0数据，清空缓冲区")
                                    self.receive_buffer = b""
                                zero_count = 0
                            last_receive_time = time.time()
                            continue
                        
                        zero_count = 0  # 重置0字节计数
                        
                        # 将接收到的数据添加到缓冲区
                        self.receive_buffer += data
                        last_receive_time = time.time()
                        
                        # 显示接收到的数据
                        hex_data = self.bytes_to_hex(data)
                        self.log_message(f"[接收] HEX: {hex_data}")
                        self.log_message(f"[接收] 长度: {len(data)}字节，缓冲区总计: {len(self.receive_buffer)}字节")
                        
                        # 更新原始数据标签页
                        self.root.after(0, self.update_raw_data, data)
                        
                        # 尝试解析传感器数据（使用缓冲区中的所有数据）
                        self.root.after(0, self.parse_sensor_data, self.receive_buffer)
                    else:
                        # 检查是否超时（超过2秒没有接收到新数据）
                        if time.time() - last_receive_time > 2:
                            # 超时，清空缓冲区
                            if len(self.receive_buffer) > 0:
                                self.log_message(f"[超时] 超过2秒未接收到新数据，清空缓冲区")
                                self.receive_buffer = b""
                            last_receive_time = time.time()
                    
            except socket.timeout:
                # 检查是否超时（超过2秒没有接收到新数据）
                if time.time() - last_receive_time > 2:
                    # 超时，清空缓冲区
                    if len(self.receive_buffer) > 0:
                        self.log_message(f"[超时] 超过2秒未接收到新数据，清空缓冲区")
                        self.receive_buffer = b""
                    last_receive_time = time.time()
                continue
            except serial.SerialException:
                self.log_message("错误: 串口读取失败")
                self.root.after(0, self.disconnect)
                break
            except ConnectionResetError:
                self.log_message("错误: 连接被重置")
                self.root.after(0, self.disconnect)
                break
            except Exception as e:
                if self.connected:
                    self.log_message(f"错误: 接收数据失败 - {e}")
                break
    
    def send_data(self):
        """发送数据"""
        try:
            hex_str = self.send_entry.get().strip()
            data = self.hex_to_bytes(hex_str)
            
            if data and self.connected:
                mode = self.mode_var.get()
                
                if mode == "TCP":
                    # TCP模式
                    if self.sock:
                        self.sock.sendall(data)
                        self.log_message(f"[发送] 通过TCP发送成功")
                else:
                    # 串口模式
                    if self.serial_port:
                        bytes_sent = self.serial_port.write(data)
                        self.log_message(f"[发送] 通过串口发送成功，发送了 {bytes_sent} 字节")
                
                hex_data = self.bytes_to_hex(data)
                self.log_message(f"[发送] HEX: {hex_data}")
                self.log_message(f"[发送] 长度: {len(data)}字节")
            
        except Exception as e:
            self.log_message(f"错误: 发送数据失败 - {e}")
            import traceback
            traceback.print_exc()
    
    def update_raw_data(self, data):
        """更新原始数据标签页"""
        hex_data = self.bytes_to_hex(data)
        ascii_data = data.decode('utf-8', errors='replace')
        
        self.raw_text.insert(tk.END, f"HEX: {hex_data}\n")
        self.raw_text.insert(tk.END, f"ASCII: {ascii_data}\n")
        self.raw_text.insert(tk.END, "-" * 80 + "\n")
        self.raw_text.see(tk.END)
    
    def parse_sensor_data(self, data):
        """解析传感器数据"""
        # 检查数据长度是否符合模块的应答帧格式
        if len(data) >= 5:  # 最小长度：地址码(1) + 功能码(1) + 数据长度(1) + 数据(2)
            # 检查是否包含LoRa目标地址前缀
            if data[:2] == b'\x56\x78':
                # 包含LoRa目标地址前缀 5678（光照模块）
                modbus_data = data[2:]
                self.log_message("检测到LoRa目标地址前缀: 56 78")
            elif data[:2] == b'\x00\x02':
                # 包含LoRa目标地址前缀 0002（温湿度模块）
                modbus_data = data[2:]
                self.log_message("检测到LoRa目标地址前缀: 00 02")
            elif data[:2] == b'\x00\x03':
                # 包含LoRa目标地址前缀 0003（温振模块）
                modbus_data = data[2:]
                self.log_message("检测到LoRa目标地址前缀: 00 03")
            else:
                # 不包含LoRa目标地址前缀（可能是串口直接连接）
                modbus_data = data
                self.log_message("未检测到LoRa目标地址前缀，直接解析")
            
            # 检查是否是光照模块的应答帧
            if len(modbus_data) == 21 and modbus_data[0] == 0x01 and modbus_data[1] == 0x03 and modbus_data[2] == 0x10:
                self.log_message("识别为光照模块的应答帧")
                
                # 解析数据
                try:
                    # 状态（2字节）
                    status = (modbus_data[3] << 8) | modbus_data[4]
                    status_text = "正常" if status == 0 else "异常"
                    
                    # 温度（2字节，0.1°C单位）
                    temperature = (modbus_data[5] << 8) | modbus_data[6]
                    if temperature > 32767:
                        temperature = (temperature - 65536) / 10.0
                    else:
                        temperature = temperature / 10.0
                    
                    # 湿度（2字节，%单位）
                    humidity = (modbus_data[7] << 8) | modbus_data[8]
                    
                    # CO2浓度（2字节，ppm单位）
                    co2 = (modbus_data[9] << 8) | modbus_data[10]
                    
                    # 气压（4字节，hPa单位）
                    pressure = (modbus_data[11] << 24) | (modbus_data[12] << 16) | (modbus_data[13] << 8) | modbus_data[14]
                    
                    # 光照强度（4字节，Lux单位）
                    light = (modbus_data[15] << 24) | (modbus_data[16] << 16) | (modbus_data[17] << 8) | modbus_data[18]
                    
                    # 更新UI
                    self.light_status_var.set(f"{status:04X}H ({status_text})")
                    self.light_temp_var.set(f"{temperature:.1f} °C")
                    self.light_humidity_var.set(f"{humidity} %")
                    self.light_co2_var.set(f"{co2} ppm")
                    self.light_pressure_var.set(f"{pressure} hPa")
                    self.light_light_var.set(f"{light} Lux")
                    
                    self.log_message(f"解析成功: 温度={temperature:.1f}°C, 湿度={humidity}%, CO2={co2}ppm, 气压={pressure}hPa, 光照={light}Lux")
                    
                except Exception as e:
                    self.log_message(f"错误: 解析传感器数据失败 - {e}")
            
            # 检查是否是温湿度模块的应答帧
            elif len(modbus_data) == 9 and modbus_data[0] == 0x01 and modbus_data[1] == 0x03 and modbus_data[2] == 0x04:
                self.log_message("识别为温湿度模块的应答帧")
                
                # 解析数据
                try:
                    # 湿度（2字节，%单位）
                    humidity = (modbus_data[3] << 8) | modbus_data[4]
                    
                    # 温度（2字节，0.1°C单位）
                    temperature = (modbus_data[5] << 8) | modbus_data[6]
                    if temperature > 32767:
                        temperature = (temperature - 65536) / 10.0
                    else:
                        temperature = temperature / 10.0
                    
                    # 更新UI
                    self.temp_hum_status_var.set("正常")
                    self.temp_hum_temp_var.set(f"{temperature:.1f} °C")
                    self.temp_hum_humidity_var.set(f"{humidity} %")
                    
                    self.log_message(f"解析成功: 温度={temperature:.1f}°C, 湿度={humidity}%")
                    
                except Exception as e:
                    self.log_message(f"错误: 解析温湿度模块数据失败 - {e}")
            
            # 检查是否是温振模块的应答帧（38个寄存器）
            elif len(modbus_data) >= 81 and modbus_data[0] == 0x01 and modbus_data[1] == 0x03 and modbus_data[2] == 0x4C:
                self.log_message("识别为温振模块的应答帧（38个寄存器）")
                
                # 解析数据
                try:
                    # 数据区从偏移3开始
                    data_area = modbus_data[3:3+0x4C]
                    
                    # 温度（2字节，0.1°C单位，有符号16位）
                    temperature_raw = (data_area[0] << 8) | data_area[1]
                    if temperature_raw > 32767:
                        temperature = (temperature_raw - 65536) / 10.0
                    else:
                        temperature = temperature_raw / 10.0
                    
                    # 振动速度X轴（2字节，mm/s单位，扩大10倍）
                    velocity_x = (data_area[2] << 8) | data_area[3]
                    velocity_x = velocity_x / 10.0
                    
                    # 振动速度Y轴（2字节，mm/s单位，扩大10倍）
                    velocity_y = (data_area[4] << 8) | data_area[5]
                    velocity_y = velocity_y / 10.0
                    
                    # 振动速度Z轴（2字节，mm/s单位，扩大10倍）
                    velocity_z = (data_area[6] << 8) | data_area[7]
                    velocity_z = velocity_z / 10.0
                    
                    # 振动位移X轴（2字节，μm单位，扩大10倍）
                    displacement_x = (data_area[8] << 8) | data_area[9]
                    displacement_x = displacement_x / 10.0
                    
                    # 振动位移Y轴（2字节，μm单位，扩大10倍）
                    displacement_y = (data_area[10] << 8) | data_area[11]
                    displacement_y = displacement_y / 10.0
                    
                    # 振动位移Z轴（2字节，μm单位，扩大10倍）
                    displacement_z = (data_area[12] << 8) | data_area[13]
                    displacement_z = displacement_z / 10.0
                    
                    # 版本号（2字节）
                    version = (data_area[18] << 8) | data_area[19]
                    
                    # 振动加速度X轴（2字节，m/s²单位，扩大10倍）
                    acceleration_x = (data_area[20] << 8) | data_area[21]
                    acceleration_x = acceleration_x / 10.0
                    
                    # 振动加速度Y轴（2字节，m/s²单位，扩大10倍）
                    acceleration_y = (data_area[22] << 8) | data_area[23]
                    acceleration_y = acceleration_y / 10.0
                    
                    # 振动加速度Z轴（2字节，m/s²单位，扩大10倍）
                    acceleration_z = (data_area[24] << 8) | data_area[25]
                    acceleration_z = acceleration_z / 10.0
                    
                    # 计算合成振动速度
                    import math
                    vibration = math.sqrt(velocity_x**2 + velocity_y**2 + velocity_z**2)
                    
                    # 更新UI
                    self.temp_vib_status_var.set("正常")
                    self.temp_vib_temp_var.set(f"{temperature:.1f} °C")
                    self.temp_vib_vibration_var.set(f"{vibration:.3f} mm/s")
                    self.temp_vib_velocity_x_var.set(f"{velocity_x:.3f} mm/s")
                    self.temp_vib_velocity_y_var.set(f"{velocity_y:.3f} mm/s")
                    self.temp_vib_velocity_z_var.set(f"{velocity_z:.3f} mm/s")
                    self.temp_vib_displacement_x_var.set(f"{displacement_x:.3f} μm")
                    self.temp_vib_displacement_y_var.set(f"{displacement_y:.3f} μm")
                    self.temp_vib_displacement_z_var.set(f"{displacement_z:.3f} μm")
                    self.temp_vib_acceleration_x_var.set(f"{acceleration_x:.3f} m/s²")
                    self.temp_vib_acceleration_y_var.set(f"{acceleration_y:.3f} m/s²")
                    self.temp_vib_acceleration_z_var.set(f"{acceleration_z:.3f} m/s²")
                    
                    self.log_message(f"解析成功: 温度={temperature:.1f}°C, 合成振动={vibration:.3f}mm/s")
                    self.log_message(f"  速度X={velocity_x:.3f}mm/s, 速度Y={velocity_y:.3f}mm/s, 速度Z={velocity_z:.3f}mm/s")
                    self.log_message(f"  位移X={displacement_x:.3f}μm, 位移Y={displacement_y:.3f}μm, 位移Z={displacement_z:.3f}μm")
                    self.log_message(f"  加速度X={acceleration_x:.3f}m/s², 加速度Y={acceleration_y:.3f}m/s², 加速度Z={acceleration_z:.3f}m/s²")
                    self.log_message(f"  版本号={version}")
                    
                except Exception as e:
                    self.log_message(f"错误: 解析温振模块数据失败 - {e}")
    
    def on_sensor_select(self, event):
        """传感器模块选择事件处理"""
        sensor = self.sensor_var.get()
        if sensor in self.sensor_configs:
            config = self.sensor_configs[sensor]
            # 更新问询帧
            self.send_entry.delete(0, tk.END)
            self.send_entry.insert(0, config["query_frame"])
            self.log_message(f"已切换到{sensor}，问询帧: {config['query_frame']}")
    
    def clear_receive_data(self):
        """清空接收数据窗口"""
        self.receive_text.delete(1.0, tk.END)
        self.log_message("已清空接收数据窗口")
    
    def on_closing(self):
        """关闭窗口时的处理"""
        self.disconnect()
        self.root.destroy()

if __name__ == '__main__':
    print("正在启动SSCOM GUI...")
    root = tk.Tk()
    print("Tk root created")
    app = SSCOM_GUI(root)
    print("SSCOM_GUI initialized")
    print("Starting mainloop...")
    root.mainloop()
    print("Mainloop ended")
