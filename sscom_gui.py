#!/usr/bin/env python3
# SSCOM模拟器 - 科技感GUI版本
# 支持TCP客户端模式、HEX显示和发送、传感器数据解析

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import socket
import time
from datetime import datetime
import threading
import re

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
        
        # 创建UI
        self.create_widgets()
        
        # 设置关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
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
            foreground="#2980b9",
            font=("Microsoft YaHei", 10),
            padding=[10, 5]
        )
        
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", "#3498db")],
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
        
        # IP地址
        ttk.Label(connect_frame, text="服务器IP:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.ip_entry = ttk.Entry(connect_frame, width=20)
        self.ip_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        self.ip_entry.insert(0, "192.168.0.80")
        
        # 端口
        ttk.Label(connect_frame, text="端口:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)
        self.port_entry = ttk.Entry(connect_frame, width=10)
        self.port_entry.grid(row=0, column=3, sticky=tk.W, pady=5, padx=5)
        self.port_entry.insert(0, "10125")
        
        # 连接按钮
        self.connect_btn = ttk.Button(connect_frame, text="连接", command=self.connect)
        self.connect_btn.grid(row=0, column=4, sticky=tk.W, pady=5, padx=5)
        
        # 断开按钮
        self.disconnect_btn = ttk.Button(connect_frame, text="断开", command=self.disconnect, state=tk.DISABLED)
        self.disconnect_btn.grid(row=0, column=5, sticky=tk.W, pady=5, padx=5)
        
        # 连接状态
        self.status_var = tk.StringVar()
        self.status_var.set("状态: 未连接")
        ttk.Label(connect_frame, textvariable=self.status_var).grid(row=0, column=6, sticky=tk.W, pady=5, padx=10)
        
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
        
        # 创建笔记本
        self.parse_notebook = ttk.Notebook(parse_frame)
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
        """连接到服务器"""
        try:
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
                
                if self.sock:
                    self.sock.close()
                    self.sock = None
                
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
        while self.connected and not self.stop_event.is_set():
            try:
                # 设置超时，以便能够及时响应停止事件
                self.sock.settimeout(0.5)
                data = self.sock.recv(1024)
                if data:
                    # 显示接收到的数据
                    hex_data = self.bytes_to_hex(data)
                    self.log_message(f"[接收] HEX: {hex_data}")
                    self.log_message(f"[接收] 长度: {len(data)}字节")
                    
                    # 更新原始数据标签页
                    self.root.after(0, self.update_raw_data, data)
                    
                    # 尝试解析传感器数据
                    self.root.after(0, self.parse_sensor_data, data)
                    
            except socket.timeout:
                continue
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
            
            if data and self.connected and self.sock:
                self.sock.sendall(data)
                hex_data = self.bytes_to_hex(data)
                self.log_message(f"[发送] HEX: {hex_data}")
                self.log_message(f"[发送] 长度: {len(data)}字节")
            
        except Exception as e:
            self.log_message(f"错误: 发送数据失败 - {e}")
    
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
        # 检查数据长度是否符合光照模块的应答帧格式
        if len(data) >= 21:
            # 检查是否包含LoRa目标地址前缀
            if len(data) == 23 and data[:2] == b'\x56\x78':
                # 包含LoRa目标地址前缀，跳过前2字节
                modbus_data = data[2:]
                self.log_message("检测到LoRa目标地址前缀: 56 78")
            else:
                # 不包含LoRa目标地址前缀
                modbus_data = data
            
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
    
    def on_closing(self):
        """关闭窗口时的处理"""
        self.disconnect()
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = SSCOM_GUI(root)
    root.mainloop()
