import os
import sys
#qt_platforms_path = r"C:\Users\毕拉力\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages\PyQt5\Qt5\plugins\platforms"
#os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = qt_platforms_path
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGroupBox, QLabel, QLineEdit, QPushButton, QCheckBox, 
                             QTextEdit, QMessageBox, QFileDialog, QProgressBar, 
                             QSplitter, QComboBox, QStatusBar)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QFont, QPalette, QColor

# 导入原有数据处理函数（确保路径正确）
from 扫频绘图工具 import process_csv_to_html


class WorkerSignals(QObject):
    """用于线程间通信的信号类"""
    log = pyqtSignal(str)  # 日志信号
    progress = pyqtSignal(int)  # 整体进度信号(0-100)
    step_progress = pyqtSignal(str)  # 步骤进度描述信号
    chart_progress = pyqtSignal(float)  # 图表生成进度信号(0-100)
    finished = pyqtSignal()  # 完成信号


class ProcessingWorker(QThread):
    """后台处理线程，避免阻塞UI"""
    def __init__(self, input_path, output_path, params, files):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.params = params
        self.files = files
        self.signals = WorkerSignals()
        self.running = True  # 用于控制线程取消
        # 每个文件的处理步骤数 - 根据日志调整
        self.steps_before_chart = 8  # 日志中显示的图表生成前的步骤数
        self.chart_step_weight = 70  # 图表生成在总进度中的占比(百分比)
        self.other_steps_weight = 30  # 其他步骤在总进度中的占比(百分比)

    def run(self):
        total_files = len(self.files)
        total_steps = total_files
        
        for i, file_path in enumerate(self.files, 1):
            if not self.running:  # 检查是否需要取消
                self.signals.log.emit("处理已取消")
                return
            
            filename = os.path.basename(file_path)
            self.signals.log.emit(f"\n开始处理第 {i}/{total_files} 个文件: {filename}")
            
            # 计算当前文件在总进度中的基础占比
            file_base_progress = (i - 1) / total_steps * 100
            file_progress_range = 100 / total_steps  # 当前文件的进度范围
            
            # 步骤1: 开始处理文件
            step = 1
            self.signals.step_progress.emit(f"开始处理文件: {file_path}")
            progress = file_base_progress + (step / self.steps_before_chart) * self.other_steps_weight / total_steps * 100
            self.signals.progress.emit(int(progress))
            if not self.running:
                return

            # 步骤2: 尝试读取CSV文件
            step += 1
            self.signals.step_progress.emit(f"尝试读取CSV文件...")
            progress = file_base_progress + (step / self.steps_before_chart) * self.other_steps_weight / total_steps * 100
            self.signals.progress.emit(int(progress))
            if not self.running:
                return

            # 步骤3: 检查必要列
            step += 1
            self.signals.step_progress.emit(f"检查必要列...")
            progress = file_base_progress + (step / self.steps_before_chart) * self.other_steps_weight / total_steps * 100
            self.signals.progress.emit(int(progress))
            if not self.running:
                return

            # 步骤4: 合并日期时间列
            step += 1
            self.signals.step_progress.emit(f"合并日期时间列...")
            progress = file_base_progress + (step / self.steps_before_chart) * self.other_steps_weight / total_steps * 100
            self.signals.progress.emit(int(progress))
            if not self.running:
                return

            # 步骤5: 转换数值列
            step += 1
            self.signals.step_progress.emit(f"转换数值列...")
            progress = file_base_progress + (step / self.steps_before_chart) * self.other_steps_weight / total_steps * 100
            self.signals.progress.emit(int(progress))
            if not self.running:
                return

            # 步骤6: 过滤无效数据
            step += 1
            self.signals.step_progress.emit(f"过滤无效数据...")
            progress = file_base_progress + (step / self.steps_before_chart) * self.other_steps_weight / total_steps * 100
            self.signals.progress.emit(int(progress))
            if not self.running:
                return

            # 步骤7: 核心计算
            step += 1
            self.signals.step_progress.emit(f"核心计算...")
            progress = file_base_progress + (step / self.steps_before_chart) * self.other_steps_weight / total_steps * 100
            self.signals.progress.emit(int(progress))
            if not self.running:
                return

            # 步骤8: 准备生成图表
            step += 1
            self.signals.step_progress.emit(f"准备生成图表...")
            progress = file_base_progress + (step / self.steps_before_chart) * self.other_steps_weight / total_steps * 100 + (self.other_steps_weight / total_steps)
            self.signals.progress.emit(int(progress))
            if not self.running:
                return

            # 步骤9: 生成图表（包含子进度）
            try:
                self.signals.step_progress.emit(f"生成图表...")
                
                # 定义接收图表进度的回调函数
                def chart_progress_callback(percent):
                    if not self.running:
                        return
                    # 计算总进度：文件基础进度 + 其他步骤占比 + 图表进度占比
                    total_progress = file_base_progress + (self.other_steps_weight / total_steps) + (percent / 100) * (self.chart_step_weight / total_steps)
                    self.signals.chart_progress.emit(percent)
                    self.signals.progress.emit(int(total_progress))

                html_path = process_csv_to_html(
                    file_path=file_path,
                    output_dir=self.output_path,
                    y_range=self.params["y_range"],
                    time_threshold=self.params["time_threshold"],
                    use_markers=self.params["use_markers"],
                    log_callback=lambda msg: self.signals.log.emit(msg),
                    progress_callback=chart_progress_callback  # 传递进度回调
                )
                self.signals.log.emit(f"成功生成图表: {html_path}")
            except Exception as e:
                self.signals.log.emit(f"处理失败: {str(e)}")
            
            if not self.running:
                return
        
        self.signals.step_progress.emit("所有文件处理完成")
        self.signals.log.emit("\n===== 所有文件处理完成 =====")
        self.signals.progress.emit(100)  # 确保进度条显示100%
        self.signals.finished.emit()

    def cancel(self):
        """取消处理"""
        self.running = False


class SSBDataConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_signals()
        self.current_style = "light"  # 默认亮色主题

    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle("扫频绘图工具")
        self.setGeometry(100, 100, 1000, 700)  # 更大的初始窗口

        # 状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪")

        # 主部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 1. 路径设置区域
        path_group = QGroupBox("输入输出设置")
        path_layout = QVBoxLayout()
        
        # 输入路径
        input_layout = QHBoxLayout()
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("请选择CSV文件或目录")
        self.browse_input_btn = QPushButton("浏览...")
        input_layout.addWidget(QLabel("输入路径:"))
        input_layout.addWidget(self.input_edit, 1)
        input_layout.addWidget(self.browse_input_btn)
        
        # 输出路径
        output_layout = QHBoxLayout()
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("请选择输出目录")
        self.browse_output_btn = QPushButton("浏览...")
        output_layout.addWidget(QLabel("输出路径:"))
        output_layout.addWidget(self.output_edit, 1)
        output_layout.addWidget(self.browse_output_btn)
        
        path_layout.addLayout(input_layout)
        path_layout.addLayout(output_layout)
        path_group.setLayout(path_layout)
        main_layout.addWidget(path_group)

        # 2. 参数设置区域
        params_group = QGroupBox("图表参数设置")
        params_layout = QVBoxLayout()
        
        # Y轴范围设置
        y_range_layout = QHBoxLayout()
        self.auto_y_check = QCheckBox("自动计算Y轴范围")
        self.auto_y_check.setChecked(True)
        self.y_min_edit = QLineEdit("0")
        self.y_max_edit = QLineEdit("100")
        self.y_min_edit.setEnabled(False)
        self.y_max_edit.setEnabled(False)
        y_range_layout.addWidget(self.auto_y_check)
        y_range_layout.addSpacing(20)
        y_range_layout.addWidget(QLabel("Y轴最小值:"))
        y_range_layout.addWidget(self.y_min_edit)
        y_range_layout.addWidget(QLabel("Y轴最大值:"))
        y_range_layout.addWidget(self.y_max_edit)
        y_range_layout.addStretch()
        
        # 其他参数
        other_params_layout = QHBoxLayout()
        self.threshold_edit = QLineEdit("0.5")
        self.markers_check = QCheckBox("显示数据点标记")
        self.markers_check.setChecked(False)
        other_params_layout.addWidget(QLabel("时间间隔阈值(秒):"))
        other_params_layout.addWidget(self.threshold_edit)
        other_params_layout.addSpacing(20)
        other_params_layout.addWidget(self.markers_check)
        other_params_layout.addStretch()
        
        params_layout.addLayout(y_range_layout)
        params_layout.addLayout(other_params_layout)
        params_group.setLayout(params_layout)
        main_layout.addWidget(params_group)

        # 3. 处理控制区域
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始处理")
        self.cancel_btn = QPushButton("取消处理")
        self.cancel_btn.setEnabled(False)
        self.theme_btn = QPushButton("切换主题")
        self.open_output_btn = QPushButton("打开输出目录")
        self.open_output_btn.setEnabled(False)
        
        # 进度显示
        progress_info_layout = QVBoxLayout()
        self.progress_label = QLabel("准备就绪")  # 显示当前步骤
        self.sub_progress_label = QLabel("")  # 显示图表生成的详细进度
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_info_layout.addWidget(self.progress_label)
        progress_info_layout.addWidget(self.sub_progress_label)
        progress_info_layout.addWidget(self.progress_bar)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.cancel_btn)
        control_layout.addWidget(self.theme_btn)
        control_layout.addWidget(self.open_output_btn)
        control_layout.addLayout(progress_info_layout, 1)
        main_layout.addLayout(control_layout)

        # 4. 日志显示区域（带分割器）
        log_group = QGroupBox("处理日志")
        log_layout = QVBoxLayout()
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setFont(QFont("SimHei", 9))  # 支持中文
        log_layout.addWidget(self.log_edit)
        log_group.setLayout(log_layout)
        
        # 添加分割器增强布局灵活性
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(params_group)
        splitter.addWidget(log_group)
        splitter.setSizes([200, 400])  # 初始大小比例
        main_layout.addWidget(splitter, 1)

    def init_signals(self):
        """初始化信号连接"""
        # 按钮信号
        self.browse_input_btn.clicked.connect(self.browse_input)
        self.browse_output_btn.clicked.connect(self.browse_output)
        self.auto_y_check.toggled.connect(self.toggle_y_input)
        self.start_btn.clicked.connect(self.start_processing)
        self.cancel_btn.clicked.connect(self.cancel_processing)
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.open_output_btn.clicked.connect(self.open_output_dir)
        
        # 输入验证（实时检查数值有效性）
        self.threshold_edit.textChanged.connect(lambda: self.validate_number(self.threshold_edit, min_val=0))
        self.y_min_edit.textChanged.connect(lambda: self.validate_number(self.y_min_edit))
        self.y_max_edit.textChanged.connect(lambda: self.validate_number(self.y_max_edit))

    def toggle_y_input(self, checked):
        """切换Y轴输入框启用状态"""
        self.y_min_edit.setEnabled(not checked)
        self.y_max_edit.setEnabled(not checked)

    def validate_number(self, edit, min_val=None, max_val=None):
        """验证输入是否为有效数字"""
        text = edit.text()
        try:
            if text:
                num = float(text)
                if (min_val is not None and num <= min_val) or (max_val is not None and num >= max_val):
                    edit.setStyleSheet("border: 1px solid red;")
                    return False
            edit.setStyleSheet("")
            return True
        except:
            edit.setStyleSheet("border: 1px solid red;")
            return False

    def browse_input(self):
        """浏览选择输入文件或目录"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择CSV文件", "", "CSV文件 (*.csv);;所有文件 (*)"
        )
        if not file_path:
            file_path = QFileDialog.getExistingDirectory(self, "选择目录")
        
        if file_path:
            self.input_edit.setText(file_path)
            # 自动填充输出目录
            if not self.output_edit.text():
                if os.path.isfile(file_path):
                    default_output = os.path.join(os.path.dirname(file_path), "html_output")
                else:
                    default_output = os.path.join(file_path, "html_output")
                self.output_edit.setText(default_output)

    def browse_output(self):
        """浏览选择输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_edit.setText(dir_path)
            self.open_output_btn.setEnabled(True)

    def log(self, message):
        """添加日志信息"""
        self.log_edit.append(message)
        self.log_edit.moveCursor(self.log_edit.textCursor().End)  # 滚动到底部
        self.statusBar.showMessage(message[:50])  # 状态栏显示简短信息
        
        # 从日志中提取图表生成进度信息并更新子进度标签
        if "处理进度：" in message:
            self.sub_progress_label.setText(message)

    def collect_files(self, input_path):
        """收集需要处理的CSV文件"""
        if not os.path.exists(input_path):
            self.log(f"错误: 输入路径不存在 - {input_path}")
            return []

        files_to_process = []
        if os.path.isfile(input_path):
            if input_path.lower().endswith('.csv'):
                files_to_process.append(input_path)
            else:
                self.log(f"警告: 仅支持CSV文件，跳过 - {input_path}")
        else:
            for root, _, files in os.walk(input_path):  # 递归遍历子目录
                for file in files:
                    if file.lower().endswith('.csv'):
                        files_to_process.append(os.path.join(root, file))
            self.log(f"在目录中找到 {len(files_to_process)} 个CSV文件（包括子目录）")

        return files_to_process

    def start_processing(self):
        """开始处理文件（使用线程避免阻塞）"""
        input_path = self.input_edit.text().strip()
        output_path = self.output_edit.text().strip()

        # 验证路径
        if not input_path:
            QMessageBox.warning(self, "警告", "请选择输入路径")
            return
        if not output_path:
            QMessageBox.warning(self, "警告", "请选择输出目录")
            return

        # 验证参数
        params = self.validate_params()
        if not params:
            return

        # 确保输出目录存在
        try:
            os.makedirs(output_path, exist_ok=True)
            self.log(f"输出目录已准备: {output_path}")
        except Exception as e:
            self.log(f"创建输出目录失败: {str(e)}")
            return

        # 收集文件
        self.log("开始收集CSV文件...")
        files_to_process = self.collect_files(input_path)
        if not files_to_process:
            self.log("没有找到可处理的CSV文件")
            return

        # 初始化线程
        self.worker = ProcessingWorker(input_path, output_path, params, files_to_process)
        self.worker.signals.log.connect(self.log)
        self.worker.signals.progress.connect(self.progress_bar.setValue)
        self.worker.signals.step_progress.connect(self.update_step_progress)
        self.worker.signals.chart_progress.connect(self.update_chart_progress)
        self.worker.signals.finished.connect(self.processing_finished)
        
        # 更新UI状态
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.browse_input_btn.setEnabled(False)
        self.browse_output_btn.setEnabled(False)
        self.theme_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.sub_progress_label.setText("")
        self.log(f"开始处理 {len(files_to_process)} 个CSV文件...")
        
        # 启动线程
        self.worker.start()

    def update_step_progress(self, step_description):
        """更新当前处理步骤的显示"""
        self.progress_label.setText(step_description)
        self.statusBar.showMessage(step_description)

    def update_chart_progress(self, percent):
        """更新图表生成的进度显示"""
        self.sub_progress_label.setText(f"图表生成中: {percent:.2f}%")

    def cancel_processing(self):
        """取消处理"""
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.cancel()
            self.log("正在取消处理...")
            self.cancel_btn.setEnabled(False)

    def processing_finished(self):
        """处理完成后更新UI"""
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.browse_input_btn.setEnabled(True)
        self.browse_output_btn.setEnabled(True)
        self.theme_btn.setEnabled(True)
        self.open_output_btn.setEnabled(True)
        self.sub_progress_label.setText("")
        QMessageBox.information(self, "完成", "所有文件处理已完成")

    def validate_params(self):
        """验证参数有效性"""
        try:
            # Y轴范围
            y_range = None
            if not self.auto_y_check.isChecked():
                if not self.validate_number(self.y_min_edit) or not self.validate_number(self.y_max_edit):
                    raise ValueError("Y轴范围输入无效")
                
                y_min = float(self.y_min_edit.text())
                y_max = float(self.y_max_edit.text())
                if y_min >= y_max:
                    raise ValueError("Y轴最小值必须小于最大值")
                y_range = [y_min, y_max]

            # 时间阈值
            if not self.validate_number(self.threshold_edit, min_val=0):
                raise ValueError("时间间隔阈值必须为正数")
            threshold = float(self.threshold_edit.text())

            return {
                "y_range": y_range,
                "time_threshold": threshold,
                "use_markers": self.markers_check.isChecked()
            }

        except ValueError as e:
            self.log(f"参数错误: {str(e)}")
            QMessageBox.warning(self, "参数错误", str(e))
            return None

    def toggle_theme(self):
        """切换明暗主题"""
        if self.current_style == "light":
            # 暗色主题
            self.setStyleSheet("""
                QWidget {
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QGroupBox {
                    border: 1px solid #555555;
                    border-radius: 4px;
                    margin-top: 10px;
                }
                QLineEdit, QTextEdit {
                    background-color: #3d3d3d;
                    border: 1px solid #555555;
                    color: #ffffff;
                }
                QProgressBar {
                    border: 1px solid #555555;
                    background-color: #3d3d3d;
                }
                QProgressBar::chunk {
                    background-color: #4a90d9;
                }
            """)
            self.current_style = "dark"
        else:
            # 亮色主题
            self.setStyleSheet("")
            self.current_style = "light"

    def open_output_dir(self):
        """打开输出目录"""
        output_path = self.output_edit.text().strip()
        if os.path.exists(output_path):
            os.startfile(output_path)  # Windows系统
        else:
            QMessageBox.warning(self, "警告", "输出目录不存在")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # 使用跨平台风格
    window = SSBDataConverter()
    window.show()
    sys.exit(app.exec_())