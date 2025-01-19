import subprocess
import tkinter as tk
from tkinter import ttk
import os
import threading

class IperfGUI:
    def __init__(self):
        # 初始化运行状态和进程变量
        self.running = False
        self.process = None
        self.create_gui()

    def create_gui(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("iPerf3 Client")
        
        # 创建主框架，添加内边距
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=0, pady=5, sticky=tk.W)
        
        # 创建开始按钮
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_test)
        self.start_button.grid(row=0, column=0, padx=5)
        
        # 创建停止按钮（初始状态为禁用）
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_test)
        self.stop_button.grid(row=0, column=1, padx=5)
        self.stop_button.config(state=tk.DISABLED)
        
        # 创建文本输出区域
        self.output_area = tk.Text(main_frame, height=20, width=80)
        self.output_area.grid(row=1, column=0, pady=5)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.output_area.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.output_area.configure(yscrollcommand=scrollbar.set)

    def run_iperf(self):
        def read_output(pipe):
            while self.running:
                output = pipe.readline()
                if output == '' and self.process.poll() is not None:
                    break
                if output:
                    self.output_area.insert(tk.END, output)
                    self.output_area.see(tk.END)
                    self.root.update()

        try:
            # 设置iperf3程序路径
            iperf_path = os.path.join(os.path.dirname(__file__), 'iperf3.exe')
            # 启动iperf3进程，连接到指定服务器
            self.process = subprocess.Popen(
                [iperf_path, "-c", "192.168.1.5", "-t", "5", "-i", "1"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # 创建线程读取输出
            output_thread = threading.Thread(target=read_output, args=(self.process.stdout,))
            output_thread.start()
            output_thread.join()

            # 读取剩余输出
            remaining_output = self.process.stdout.read()
            if remaining_output:
                self.output_area.insert(tk.END, remaining_output)
                self.output_area.see(tk.END)

        except Exception as e:
            # 显示错误信息
            self.output_area.insert(tk.END, f"Error: {str(e)}\n")
        finally:
            # 重置按钮状态
            self.running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def start_test(self):
        # 开始测试，更新按钮状态
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        threading.Thread(target=self.run_iperf).start()

    def stop_test(self):
        # 停止测试，终止进程
        self.running = False
        if self.process:
            self.process.terminate()

    def run(self):
        # 运行主循环
        self.root.mainloop()

if __name__ == "__main__":
    app = IperfGUI()
    app.run()