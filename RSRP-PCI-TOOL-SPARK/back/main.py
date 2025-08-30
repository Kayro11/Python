import os
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext
from tkinter import messagebox
from Spark_excel数据转html import process_file_to_html  # 导入处理函数

class ExcelToHtmlConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel/CSV 转 HTML 图表工具")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("微软雅黑", 10))
        self.style.configure("TButton", font=("微软雅黑", 10))
        self.style.configure("TEntry", font=("微软雅黑", 10))

        # 创建界面组件
        self.create_widgets()

    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. 输入文件/目录选择区域
        input_frame = ttk.LabelFrame(main_frame, text="输入设置", padding="10")
        input_frame.pack(fill=tk.X, pady=5)

        ttk.Label(input_frame, text="输入文件/目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_path = tk.StringVar()
        input_entry = ttk.Entry(input_frame, textvariable=self.input_path, width=50)
        input_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=5)
        ttk.Button(
            input_frame, 
            text="浏览...", 
            command=self.browse_input
        ).grid(row=0, column=2, padx=5, pady=5)

        input_frame.columnconfigure(1, weight=1)

        # 2. 输出目录选择区域
        output_frame = ttk.LabelFrame(main_frame, text="输出设置", padding="10")
        output_frame.pack(fill=tk.X, pady=5)

        ttk.Label(output_frame, text="输出目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.output_path = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path, width=50)
        output_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=5)
        ttk.Button(
            output_frame, 
            text="浏览...", 
            command=self.browse_output
        ).grid(row=0, column=2, padx=5, pady=5)

        output_frame.columnconfigure(1, weight=1)

        # 3. 参数设置区域
        params_frame = ttk.LabelFrame(main_frame, text="图表参数", padding="10")
        params_frame.pack(fill=tk.X, pady=5)

        # 参数网格布局
        # 行0: Y轴最小值
        ttk.Label(params_frame, text="Y轴最小值:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.y_min = tk.StringVar(value="-110")
        ttk.Entry(params_frame, textvariable=self.y_min, width=10).grid(row=0, column=1, sticky=tk.W, pady=5)

        # 行0: Y轴最大值
        ttk.Label(params_frame, text="Y轴最大值:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)
        self.y_max = tk.StringVar(value="-75")
        ttk.Entry(params_frame, textvariable=self.y_max, width=10).grid(row=0, column=3, sticky=tk.W, pady=5)

        # 行1: 平滑窗口大小
        ttk.Label(params_frame, text="平滑窗口大小:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.rolling = tk.StringVar(value="4")
        ttk.Entry(params_frame, textvariable=self.rolling, width=10).grid(row=1, column=1, sticky=tk.W, pady=5)

        # 行1: 时间间隔阈值
        ttk.Label(params_frame, text="时间间隔阈值(秒):").grid(row=1, column=2, sticky=tk.W, pady=5, padx=5)
        self.threshold = tk.StringVar(value="0.5")
        ttk.Entry(params_frame, textvariable=self.threshold, width=10).grid(row=1, column=3, sticky=tk.W, pady=5)

        # 4. 处理按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(
            btn_frame, 
            text="开始处理", 
            command=self.start_processing,
            style="Accent.TButton"
        ).pack(side=tk.RIGHT)

        # 5. 日志显示区域
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            wrap=tk.WORD, 
            state=tk.DISABLED,
            font=("微软雅黑", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def browse_input(self):
        """浏览选择输入文件或目录"""
        path = filedialog.askopenfilename(
            title="选择输入文件或目录",
            filetypes=[("Excel/CSV文件", "*.xlsx *.csv"), ("所有文件", "*.*")]
        )
        if not path:
            # 尝试选择目录
            path = filedialog.askdirectory(title="选择输入目录")
        if path:
            self.input_path.set(path)

    def browse_output(self):
        """浏览选择输出目录"""
        path = filedialog.askdirectory(title="选择输出目录")
        if path:
            self.output_path.set(path)

    def log(self, message):
        """在日志区域显示消息"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # 滚动到最后一行
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()  # 刷新界面

    def validate_params(self):
        """验证输入参数的有效性"""
        try:
            # 验证Y轴范围
            y_min = int(self.y_min.get())
            y_max = int(self.y_max.get())
            if y_min >= y_max:
                raise ValueError("Y轴最小值必须小于最大值")

            # 验证平滑窗口
            rolling = int(self.rolling.get())
            if rolling <= 0:
                raise ValueError("平滑窗口大小必须为正整数")

            # 验证时间阈值
            threshold = float(self.threshold.get())
            if threshold <= 0:
                raise ValueError("时间间隔阈值必须为正数")

            return {
                "y_min": y_min,
                "y_max": y_max,
                "rolling": rolling,
                "threshold": threshold
            }

        except ValueError as e:
            self.log(f"参数错误: {str(e)}")
            return None

    def collect_files(self, input_path):
        """收集需要处理的文件列表"""
        if not os.path.exists(input_path):
            self.log(f"错误: 输入路径不存在 - {input_path}")
            return []

        files_to_process = []
        if os.path.isfile(input_path):
            # 单个文件
            ext = os.path.splitext(input_path)[1].lower()
            if ext in ('.xlsx', '.csv'):
                files_to_process.append(input_path)
            else:
                self.log(f"警告: 不支持的文件格式 - {input_path}")
        else:
            # 目录
            for filename in os.listdir(input_path):
                file_path = os.path.join(input_path, filename)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in ('.xlsx', '.csv'):
                        files_to_process.append(file_path)
            self.log(f"在目录中找到 {len(files_to_process)} 个文件")

        return files_to_process

    def start_processing(self):
        """开始处理文件"""
        # 获取输入输出路径
        input_path = self.input_path.get().strip()
        output_path = self.output_path.get().strip()

        # 验证路径
        if not input_path:
            messagebox.showwarning("警告", "请选择输入文件或目录")
            return
        if not output_path:
            messagebox.showwarning("警告", "请选择输出目录")
            return

        # 验证参数
        params = self.validate_params()
        if not params:
            return

        # 确保输出目录存在
        try:
            os.makedirs(output_path, exist_ok=True)
        except Exception as e:
            self.log(f"创建输出目录失败: {str(e)}")
            return

        # 收集文件
        self.log("开始收集文件...")
        files_to_process = self.collect_files(input_path)
        if not files_to_process:
            self.log("没有找到可处理的文件")
            return

        # 开始处理
        self.log(f"开始处理 {len(files_to_process)} 个文件...")
        y_range = [params["y_min"], params["y_max"]]

        for i, file_path in enumerate(files_to_process, 1):
            self.log(f"\n处理第 {i}/{len(files_to_process)} 个文件: {os.path.basename(file_path)}")
            try:
                html_path = process_file_to_html(
                    file_path=file_path,
                    output_dir=output_path,
                    y_range=y_range,
                    rolling_window=params["rolling"],
                    time_threshold=params["threshold"]
                )
                self.log(f"成功生成: {html_path}")
            except Exception as e:
                self.log(f"处理失败: {str(e)}")

        self.log("\n===== 处理完成 =====")
        messagebox.showinfo("完成", "所有文件处理已完成")

if __name__ == "__main__":
    root = tk.Tk()
    # 增加按钮样式
    root.style = ttk.Style()
    root.style.configure("Accent.TButton", font=("微软雅黑", 10, "bold"))
    app = ExcelToHtmlConverter(root)
    root.mainloop()