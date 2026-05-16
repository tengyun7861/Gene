"""
结果面板
显示DNA序列比对结果
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QGroupBox, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QProgressBar, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from ..models.alignment_result import AlignmentResult
from ..utils.validators import SequenceValidator
from .sequence_display import SequenceDisplayWidget
from .theme import COLORS, get_similarity_color


class ResultPanel(QWidget):
    """结果面板"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # 结果标题
        self.title_label = QLabel("比对结果")
        self.title_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {COLORS['accent_cyan']};
        """)
        layout.addWidget(self.title_label)

        # 创建标签页
        self.tab_widget = QTabWidget()

        # ===== 详细结果标签页 =====
        detail_tab = QWidget()
        detail_layout = QVBoxLayout(detail_tab)
        detail_layout.setSpacing(8)

        # 统计信息卡片
        stats_frame = QFrame()
        stats_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(20)

        # 得分
        self.score_label = self._create_stat_card("SCORE", "0")
        stats_layout.addWidget(self.score_label)

        # 分隔线
        stats_layout.addWidget(self._create_separator())

        # 相似度
        self.similarity_label = self._create_stat_card("SIMILARITY", "0%")
        stats_layout.addWidget(self.similarity_label)

        stats_layout.addWidget(self._create_separator())

        # 匹配数
        self.match_label = self._create_stat_card("MATCHES", "0")
        stats_layout.addWidget(self.match_label)

        stats_layout.addWidget(self._create_separator())

        # 空位数
        self.gap_label = self._create_stat_card("GAPS", "0")
        stats_layout.addWidget(self.gap_label)

        stats_layout.addWidget(self._create_separator())

        # 设备
        self.device_label = self._create_stat_card("DEVICE", "-")
        stats_layout.addWidget(self.device_label)

        detail_layout.addWidget(stats_frame)

        # 相似度进度条
        bar_layout = QHBoxLayout()
        bar_title = QLabel("相似度")
        bar_title.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: bold;")
        self.similarity_bar = QProgressBar()
        self.similarity_bar.setRange(0, 100)
        self.similarity_bar.setTextVisible(True)
        self.similarity_bar.setFormat("%v%")
        bar_layout.addWidget(bar_title)
        bar_layout.addWidget(self.similarity_bar, 1)
        detail_layout.addLayout(bar_layout)

        # 序列比对显示（彩色碱基）
        alignment_group = QGroupBox("序列比对")
        alignment_layout = QVBoxLayout(alignment_group)
        self.sequence_display = SequenceDisplayWidget()
        alignment_layout.addWidget(self.sequence_display)
        detail_layout.addWidget(alignment_group)

        # 详细统计文本
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(120)
        self.stats_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px;
                color: {COLORS['text_secondary']};
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }}
        """)
        detail_layout.addWidget(self.stats_text)

        detail_layout.addStretch()
        self.tab_widget.addTab(detail_tab, "详细结果")

        # ===== 批量结果标签页 =====
        batch_tab = QWidget()
        batch_layout = QVBoxLayout(batch_tab)

        self.batch_table = QTableWidget()
        self.batch_table.setColumnCount(6)
        self.batch_table.setHorizontalHeaderLabels([
            "序号", "待测序列预览", "相似度", "得分", "匹配数", "设备"
        ])
        self.batch_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.batch_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.batch_table.setEditTriggers(QTableWidget.NoEditTriggers)
        batch_layout.addWidget(self.batch_table)

        # 批量统计
        self.batch_stats_label = QLabel()
        self.batch_stats_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            padding: 8px;
            font-size: 13px;
        """)
        batch_layout.addWidget(self.batch_stats_label)

        self.tab_widget.addTab(batch_tab, "批量结果")

        layout.addWidget(self.tab_widget)

    def _create_stat_card(self, title: str, value: str) -> QFrame:
        """创建统计信息卡片"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border: none;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 11px;
            font-weight: bold;
        """)
        title_label.setAlignment(Qt.AlignCenter)

        value_label = QLabel(value)
        value_label.setObjectName("stat_value")
        value_label.setStyleSheet(f"""
            color: {COLORS['accent_green']};
            font-size: 20px;
            font-weight: bold;
            font-family: 'Consolas', 'Courier New', monospace;
        """)
        value_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        frame._value_label = value_label
        return frame

    def _create_separator(self) -> QFrame:
        """创建垂直分隔线"""
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet(f"color: {COLORS['border']};")
        return sep

    def _update_stat_value(self, frame: QFrame, value: str, color: str = None):
        """更新统计卡片的值"""
        label = frame._value_label
        label.setText(value)
        if color:
            label.setStyleSheet(f"""
                color: {color};
                font-size: 20px;
                font-weight: bold;
                font-family: 'Consolas', 'Courier New', monospace;
            """)

    def display_result(self, result: AlignmentResult):
        """显示单个比对结果"""
        # 更新统计卡片
        sim_color = get_similarity_color(result.similarity)
        self._update_stat_value(self.score_label, str(result.score), COLORS['accent_green'])
        self._update_stat_value(self.similarity_label, f"{result.similarity}%", sim_color)

        ref = result.ref_alignment
        match_count = result.match_mark.count('√')
        gap_count = ref.count('-') + result.query_alignment.count('-')
        self._update_stat_value(self.match_label, str(match_count), COLORS['accent_green'])
        self._update_stat_value(self.gap_label, str(gap_count), COLORS['text_secondary'])
        self._update_stat_value(self.device_label, result.device_info, COLORS['accent_cyan'])

        # 更新进度条
        self.similarity_bar.setValue(int(result.similarity))
        self.similarity_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                text-align: center;
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                height: 22px;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {sim_color};
                border-radius: 5px;
            }}
        """)

        # 更新彩色序列显示
        self.sequence_display.set_alignment(
            result.ref_alignment, result.query_alignment, result.match_mark
        )

        # 更新详细统计
        mismatch_count = result.match_mark.count('×')
        identity = round(match_count / len(ref) * 100, 2) if len(ref) > 0 else 0

        stats_text = (
            f"比对长度: {len(ref)}  |  "
            f"匹配: {match_count}  |  "
            f"不匹配: {mismatch_count}  |  "
            f"空位: {gap_count}  |  "
            f"身份度: {identity}%\n"
            f"GC含量(标准): {SequenceValidator.calculate_gc_content(result.ref_original)}%  |  "
            f"GC含量(待测): {SequenceValidator.calculate_gc_content(result.query_original)}%\n"
            f"比对时间: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self.stats_text.setPlainText(stats_text)

        # 更新标题
        self.title_label.setText(f"比对结果 - 相似度: {result.similarity}%")

        # 切换到详细结果标签页
        self.tab_widget.setCurrentIndex(0)

    def display_batch_results(self, results: list):
        """显示批量比对结果"""
        self.batch_table.setRowCount(len(results))

        for i, result in enumerate(results):
            self.batch_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))

            query_preview = result.query_original[:20] + "..." if len(result.query_original) > 20 else result.query_original
            self.batch_table.setItem(i, 1, QTableWidgetItem(query_preview))

            sim_color = get_similarity_color(result.similarity)
            similarity_item = QTableWidgetItem(f"{result.similarity}%")
            similarity_item.setForeground(QColor(sim_color))
            self.batch_table.setItem(i, 2, similarity_item)

            self.batch_table.setItem(i, 3, QTableWidgetItem(str(result.score)))

            match_count = result.match_mark.count('√')
            self.batch_table.setItem(i, 4, QTableWidgetItem(str(match_count)))

            self.batch_table.setItem(i, 5, QTableWidgetItem(result.device_info))

        # 更新批量统计
        if results:
            avg_similarity = sum(r.similarity for r in results) / len(results)
            max_similarity = max(r.similarity for r in results)
            min_similarity = min(r.similarity for r in results)

            stats_text = (
                f"共 {len(results)} 条结果  |  "
                f"平均相似度: {avg_similarity:.1f}%  |  "
                f"最高: {max_similarity}%  |  "
                f"最低: {min_similarity}%"
            )
            self.batch_stats_label.setText(stats_text)

        self.title_label.setText(f"批量比对结果 - 共 {len(results)} 条")
        self.tab_widget.setCurrentIndex(1)

    def clear(self):
        """清空结果"""
        self._update_stat_value(self.score_label, "0", COLORS['accent_green'])
        self._update_stat_value(self.similarity_label, "0%", COLORS['text_secondary'])
        self._update_stat_value(self.match_label, "0", COLORS['accent_green'])
        self._update_stat_value(self.gap_label, "0", COLORS['text_secondary'])
        self._update_stat_value(self.device_label, "-", COLORS['text_secondary'])
        self.similarity_bar.setValue(0)
        self.similarity_bar.setStyleSheet("")
        self.sequence_display.clear()
        self.stats_text.clear()
        self.batch_table.setRowCount(0)
        self.batch_stats_label.clear()
        self.title_label.setText("比对结果")
