"""
输入面板
提供DNA序列输入和批量导入功能
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QGroupBox, QFileDialog,
    QMessageBox, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from ..utils.validators import SequenceValidator
from .theme import COLORS


class InputPanel(QWidget):
    """输入面板"""

    # 自定义信号
    align_requested = pyqtSignal()
    batch_align_requested = pyqtSignal()
    clear_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # 创建标签页
        tab_widget = QTabWidget()

        # ===== 单序列比对标签页 =====
        single_tab = QWidget()
        single_layout = QVBoxLayout(single_tab)

        # 标准序列输入
        ref_group = QGroupBox("标准DNA序列")
        ref_layout = QVBoxLayout(ref_group)

        self.ref_input = QTextEdit()
        self.ref_input.setPlaceholderText("请输入标准DNA序列（仅支持 A/T/C/G）...")
        self.ref_input.setMaximumHeight(80)
        self.ref_input.textChanged.connect(self._validate_ref_input)
        ref_layout.addWidget(self.ref_input)

        self.ref_info_label = QLabel("长度: 0")
        self.ref_info_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        ref_layout.addWidget(self.ref_info_label)

        single_layout.addWidget(ref_group)

        # 待测序列输入
        query_group = QGroupBox("待测DNA序列")
        query_layout = QVBoxLayout(query_group)

        self.query_input = QTextEdit()
        self.query_input.setPlaceholderText("请输入待测DNA序列（仅支持 A/T/C/G）...")
        self.query_input.setMaximumHeight(80)
        self.query_input.textChanged.connect(self._validate_query_input)
        query_layout.addWidget(self.query_input)

        self.query_info_label = QLabel("长度: 0")
        self.query_info_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        query_layout.addWidget(self.query_info_label)

        single_layout.addWidget(query_group)

        # 按钮区域
        button_layout = QHBoxLayout()

        self.align_btn = QPushButton("开始比对")
        self.align_btn.setObjectName("primary_btn")
        self.align_btn.clicked.connect(self._on_align_clicked)

        self.clear_btn = QPushButton("清空")
        self.clear_btn.setObjectName("danger_btn")
        self.clear_btn.clicked.connect(self._on_clear_clicked)

        button_layout.addWidget(self.align_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()

        single_layout.addLayout(button_layout)
        single_layout.addStretch()

        tab_widget.addTab(single_tab, "单序列比对")

        # ===== 批量比对标签页 =====
        batch_tab = QWidget()
        batch_layout = QVBoxLayout(batch_tab)

        batch_info = QLabel("请输入多条DNA序列，每行一条。第一条将作为标准序列，其余作为待测序列。")
        batch_info.setWordWrap(True)
        batch_info.setStyleSheet(f"color: {COLORS['text_secondary']};")
        batch_layout.addWidget(batch_info)

        self.batch_input = QTextEdit()
        self.batch_input.setPlaceholderText("ATCGATCGATCG\nATCGATCGATCG\nATCGATCGATCG\n...")
        self.batch_input.textChanged.connect(self._validate_batch_input)
        batch_layout.addWidget(self.batch_input)

        self.batch_info_label = QLabel("序列数量: 0")
        self.batch_info_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        batch_layout.addWidget(self.batch_info_label)

        # 批量按钮
        batch_button_layout = QHBoxLayout()

        self.batch_align_btn = QPushButton("批量比对")
        self.batch_align_btn.setObjectName("primary_btn")
        self.batch_align_btn.clicked.connect(self._on_batch_align_clicked)

        self.import_btn = QPushButton("从文件导入")
        self.import_btn.clicked.connect(self._on_import_clicked)

        batch_button_layout.addWidget(self.batch_align_btn)
        batch_button_layout.addWidget(self.import_btn)
        batch_button_layout.addStretch()

        batch_layout.addLayout(batch_button_layout)

        tab_widget.addTab(batch_tab, "批量比对")

        layout.addWidget(tab_widget)

    def _validate_ref_input(self):
        """验证标准序列输入"""
        text = self.ref_input.toPlainText().upper().strip()
        self.ref_info_label.setText(f"长度: {len(text)}")

        if text and not SequenceValidator.validate_dna(text)[0]:
            self.ref_info_label.setStyleSheet(f"color: {COLORS['error']};")
            self.ref_input.setStyleSheet(f"QTextEdit {{ border: 2px solid {COLORS['error']}; }}")
        else:
            self.ref_info_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
            self.ref_input.setStyleSheet("")

    def _validate_query_input(self):
        """验证待测序列输入"""
        text = self.query_input.toPlainText().upper().strip()
        self.query_info_label.setText(f"长度: {len(text)}")

        if text and not SequenceValidator.validate_dna(text)[0]:
            self.query_info_label.setStyleSheet(f"color: {COLORS['error']};")
            self.query_input.setStyleSheet(f"QTextEdit {{ border: 2px solid {COLORS['error']}; }}")
        else:
            self.query_info_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
            self.query_input.setStyleSheet("")

    def _validate_batch_input(self):
        """验证批量输入"""
        text = self.batch_input.toPlainText().strip()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        self.batch_info_label.setText(f"序列数量: {len(lines)}")

    def _on_align_clicked(self):
        """比对按钮点击"""
        ref_seq = self.get_ref_sequence()
        query_seq = self.get_query_sequence()

        if not ref_seq:
            QMessageBox.warning(self, "警告", "请输入标准DNA序列！")
            return

        if not query_seq:
            QMessageBox.warning(self, "警告", "请输入待测DNA序列！")
            return

        is_valid, error = SequenceValidator.validate_dna(ref_seq)
        if not is_valid:
            QMessageBox.warning(self, "输入错误", f"标准序列: {error}")
            return

        is_valid, error = SequenceValidator.validate_dna(query_seq)
        if not is_valid:
            QMessageBox.warning(self, "输入错误", f"待测序列: {error}")
            return

        self.align_requested.emit()

    def _on_batch_align_clicked(self):
        """批量比对按钮点击"""
        sequences = self.get_batch_sequences()

        if len(sequences) < 2:
            QMessageBox.warning(self, "警告", "批量比对需要至少2条序列！")
            return

        is_valid, errors = SequenceValidator.validate_batch(sequences)
        if not is_valid:
            error_msg = "\n".join(errors[:5])
            if len(errors) > 5:
                error_msg += f"\n... 还有 {len(errors) - 5} 个错误"
            QMessageBox.warning(self, "输入错误", f"序列验证失败:\n{error_msg}")
            return

        self.batch_align_requested.emit()

    def _on_clear_clicked(self):
        """清空按钮点击"""
        self.clear_requested.emit()

    def _on_import_clicked(self):
        """导入按钮点击"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入序列文件",
            "",
            "FASTA文件 (*.fasta *.fa *.fna);;CSV文件 (*.csv);;文本文件 (*.txt);;所有文件 (*)"
        )

        if file_path:
            try:
                from ..utils.file_io import FileIO
                sequences = FileIO.import_sequences(file_path)

                if sequences:
                    seq_text = "\n".join([s['sequence'] for s in sequences])
                    self.batch_input.setPlainText(seq_text)
                    QMessageBox.information(self, "导入成功", f"成功导入 {len(sequences)} 条序列")
            except Exception as e:
                QMessageBox.critical(self, "导入错误", f"导入序列文件失败: {str(e)}")

    def get_ref_sequence(self) -> str:
        """获取标准序列"""
        return self.ref_input.toPlainText().upper().strip()

    def get_query_sequence(self) -> str:
        """获取待测序列"""
        return self.query_input.toPlainText().upper().strip()

    def get_batch_sequences(self) -> list:
        """获取批量序列列表"""
        text = self.batch_input.toPlainText().strip()
        lines = [line.strip().upper() for line in text.split('\n') if line.strip()]
        return lines

    def set_sequences(self, ref_seq: str, query_seq: str):
        """设置序列"""
        self.ref_input.setPlainText(ref_seq)
        self.query_input.setPlainText(query_seq)

    def set_ref_sequence(self, ref_seq: str):
        """设置标准序列"""
        self.ref_input.setPlainText(ref_seq)

    def clear(self):
        """清空所有输入"""
        self.ref_input.clear()
        self.query_input.clear()
        self.batch_input.clear()
        self.ref_info_label.setText("长度: 0")
        self.query_info_label.setText("长度: 0")
        self.batch_info_label.setText("序列数量: 0")
