"""
DNA序列比对工具主窗口
"""
import sys
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStatusBar, QAction, QSplitter, QMessageBox,
    QFileDialog, QApplication, QLabel, QMenuBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from .input_panel import InputPanel
from .result_panel import ResultPanel
from .history_panel import HistoryPanel

from ..core.aligner_factory import AlignerFactory
from ..models.history_manager import HistoryManager
from ..utils.file_io import FileIO


class MainWindow(QMainWindow):
    """DNA序列比对工具主窗口"""

    def __init__(self):
        super().__init__()

        self.history_manager = HistoryManager()
        self.aligner = AlignerFactory.create_aligner()

        self.current_result = None
        self.batch_results = []

        self._init_ui()
        self._create_menu_bar()
        self._create_status_bar()

        self.setWindowTitle("DNA序列比对工具")
        self.resize(1200, 800)

    def _init_ui(self):
        """初始化主界面布局"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        splitter = QSplitter(Qt.Horizontal)

        # 左侧历史记录面板
        self.history_panel = HistoryPanel(self.history_manager)
        self.history_panel.setMinimumWidth(200)

        # 右侧主工作区（上下分割）
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)

        # 输入面板和结果面板用垂直分割器
        v_splitter = QSplitter(Qt.Vertical)

        self.input_panel = InputPanel()
        self.result_panel = ResultPanel()

        v_splitter.addWidget(self.input_panel)
        v_splitter.addWidget(self.result_panel)
        v_splitter.setStretchFactor(0, 1)
        v_splitter.setStretchFactor(1, 2)

        right_layout.addWidget(v_splitter)

        splitter.addWidget(self.history_panel)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)

        self._connect_signals()

    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')

        open_action = QAction('打开序列文件(&O)...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self._open_sequence_file)
        file_menu.addAction(open_action)

        export_action = QAction('导出结果(&E)...', self)
        export_action.setShortcut('Ctrl+E')
        export_action.triggered.connect(self._export_results)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')

        about_action = QAction('关于(&A)', self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        device_info = self.aligner.get_device_info()
        self.gpu_label = QLabel(f"设备: {device_info}")
        self.status_bar.addWidget(self.gpu_label)

        self.progress_label = QLabel("就绪")
        self.status_bar.addPermanentWidget(self.progress_label)

        self.time_label = QLabel()
        self.status_bar.addPermanentWidget(self.time_label)

        self.timer = QTimer()
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000)
        self._update_time()

    def _connect_signals(self):
        """连接信号和槽"""
        self.input_panel.align_requested.connect(self._start_alignment)
        self.input_panel.batch_align_requested.connect(self._start_batch_alignment)
        self.input_panel.clear_requested.connect(self._clear_input)

        self.history_panel.record_selected.connect(self._load_history_record)
        self.history_panel.record_deleted.connect(self._delete_history_record)

    def _start_alignment(self):
        """开始单序列比对"""
        ref_seq = self.input_panel.get_ref_sequence()
        query_seq = self.input_panel.get_query_sequence()

        if not ref_seq or not query_seq:
            QMessageBox.warning(self, "警告", "请输入标准序列和待测序列！")
            return

        try:
            self.progress_label.setText("正在比对...")
            QApplication.processEvents()

            result = self.aligner.align(ref_seq, query_seq)
            self.current_result = result

            self.history_manager.save(result)

            self.result_panel.display_result(result)
            self.history_panel.refresh_list()

            self.progress_label.setText("比对完成")
            self.status_bar.showMessage(f"比对完成 - 相似度: {result.similarity}%", 5000)

        except ValueError as e:
            QMessageBox.warning(self, "输入错误", str(e))
            self.progress_label.setText("比对失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"比对过程中发生错误: {str(e)}")
            self.progress_label.setText("比对失败")

    def _start_batch_alignment(self):
        """开始批量比对"""
        sequences = self.input_panel.get_batch_sequences()

        if len(sequences) < 2:
            QMessageBox.warning(self, "警告", "批量比对需要至少2条序列！")
            return

        try:
            self.progress_label.setText("正在批量比对...")
            QApplication.processEvents()

            self.batch_results = []
            total = len(sequences)
            ref_seq = sequences[0]

            for i, query_seq in enumerate(sequences[1:], 1):
                self.progress_label.setText(f"正在比对 {i}/{total-1}...")
                QApplication.processEvents()

                result = self.aligner.align(ref_seq, query_seq)
                result.batch_index = i
                result.batch_total = total - 1
                self.batch_results.append(result)

                self.history_manager.save(result)

            self.result_panel.display_batch_results(self.batch_results)
            self.history_panel.refresh_list()

            self.progress_label.setText(f"批量比对完成 - 共{len(self.batch_results)}条结果")
            self.status_bar.showMessage("批量比对完成", 5000)

        except ValueError as e:
            QMessageBox.warning(self, "输入错误", str(e))
            self.progress_label.setText("批量比对失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"批量比对过程中发生错误: {str(e)}")
            self.progress_label.setText("批量比对失败")

    def _clear_input(self):
        """清空输入"""
        self.input_panel.clear()
        self.result_panel.clear()
        self.current_result = None
        self.batch_results = []
        self.progress_label.setText("就绪")

    def _load_history_record(self, record_id: str):
        """加载历史记录"""
        result = self.history_manager.load(record_id)
        if result:
            self.current_result = result
            self.result_panel.display_result(result)
            self.input_panel.set_sequences(result.ref_original, result.query_original)

    def _delete_history_record(self, record_id: str):
        """删除历史记录"""
        reply = QMessageBox.question(
            self, "确认删除", "确定要删除这条记录吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.history_manager.delete(record_id)
            self.history_panel.refresh_list()

    def _open_sequence_file(self):
        """打开序列文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开序列文件", "",
            "FASTA文件 (*.fasta *.fa *.fna);;CSV文件 (*.csv);;文本文件 (*.txt);;所有文件 (*)"
        )
        if file_path:
            try:
                sequences = FileIO.import_sequences(file_path)
                if sequences:
                    if len(sequences) >= 2:
                        self.input_panel.set_sequences(
                            sequences[0]['sequence'], sequences[1]['sequence']
                        )
                    else:
                        self.input_panel.set_ref_sequence(sequences[0]['sequence'])
                    self.status_bar.showMessage(f"已导入 {len(sequences)} 条序列", 3000)
            except Exception as e:
                QMessageBox.critical(self, "导入错误", f"导入序列文件失败: {str(e)}")

    def _export_results(self):
        """导出比对结果"""
        if not self.current_result and not self.batch_results:
            QMessageBox.warning(self, "警告", "没有可导出的比对结果！")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出比对结果",
            f"alignment_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "CSV文件 (*.csv);;JSON文件 (*.json);;文本文件 (*.txt)"
        )
        if file_path:
            try:
                results = self.batch_results if self.batch_results else [self.current_result]
                FileIO.export_results(results, file_path)
                self.status_bar.showMessage(f"结果已导出到: {file_path}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "导出错误", f"导出结果失败: {str(e)}")

    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, "关于",
            "DNA序列比对工具 v2.0.0\n\n"
            "基于Smith-Waterman算法的DNA序列局部比对工具\n"
            "支持GPU加速和批量比对功能\n\n"
            "技术栈: Python + PyQt5 + PyTorch"
        )

    def _update_time(self):
        """更新状态栏时间"""
        self.time_label.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def closeEvent(self, event):
        """关闭窗口事件"""
        reply = QMessageBox.question(
            self, "确认退出", "确定要退出程序吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
