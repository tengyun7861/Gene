"""
历史记录面板
显示和管理比对历史记录
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton,
    QGroupBox, QLineEdit, QComboBox, QMessageBox,
    QMenu, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from ..models.history_manager import HistoryManager
from .theme import COLORS, get_similarity_color


class HistoryPanel(QWidget):
    """历史记录面板"""

    # 自定义信号
    record_selected = pyqtSignal(str)
    record_deleted = pyqtSignal(str)

    def __init__(self, history_manager: HistoryManager, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self._init_ui()
        self.refresh_list()

    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # 标题
        title_label = QLabel("历史记录")
        title_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {COLORS['accent_cyan']};
        """)
        layout.addWidget(title_label)

        # 搜索区域
        search_group = QGroupBox("搜索")
        search_layout = QVBoxLayout(search_group)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索序列或备注...")
        self.search_input.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search_input)

        # 排序选项
        sort_layout = QHBoxLayout()
        sort_label = QLabel("排序:")
        sort_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["时间 (最新)", "时间 (最早)", "相似度 (高)", "相似度 (低)"])
        self.sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        sort_layout.addWidget(sort_label)
        sort_layout.addWidget(self.sort_combo)
        search_layout.addLayout(sort_layout)

        layout.addWidget(search_group)

        # 统计信息
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet(f"""
            background-color: {COLORS['bg_tertiary']};
            padding: 8px;
            border-radius: 6px;
            font-size: 12px;
            color: {COLORS['text_secondary']};
        """)
        layout.addWidget(self.stats_label)

        # 历史记录列表
        self.history_list = QListWidget()
        self.history_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self._show_context_menu)
        self.history_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.history_list)

        # 按钮区域
        button_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh_list)

        self.clear_btn = QPushButton("清空所有")
        self.clear_btn.setObjectName("danger_btn")
        self.clear_btn.clicked.connect(self._clear_all_history)

        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

    def refresh_list(self):
        """刷新历史记录列表"""
        self.history_list.clear()

        sort_index = self.sort_combo.currentIndex()
        if sort_index == 0:
            order_by, order_desc = 'timestamp', True
        elif sort_index == 1:
            order_by, order_desc = 'timestamp', False
        elif sort_index == 2:
            order_by, order_desc = 'similarity', True
        else:
            order_by, order_desc = 'similarity', False

        records = self.history_manager.get_all(
            limit=100, order_by=order_by, order_desc=order_desc
        )

        for record in records:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, record['id'])

            sim_color = get_similarity_color(record['similarity'])
            display_text = (
                f"相似度: {record['similarity']}%\n"
                f"标准: {record['ref_preview']}\n"
                f"待测: {record['query_preview']}\n"
                f"时间: {record['timestamp'][:16]}"
            )

            item.setText(display_text)
            item.setForeground(QColor(sim_color))

            self.history_list.addItem(item)

        self._update_statistics()

    def _update_statistics(self):
        """更新统计信息"""
        stats = self.history_manager.get_statistics()
        stats_text = (
            f"总记录: {stats['total_count']}  |  "
            f"平均相似度: {stats['avg_similarity']}%  |  "
            f"最高: {stats['max_similarity']}%"
        )
        self.stats_label.setText(stats_text)

    def _on_search(self, text: str):
        """搜索"""
        if not text.strip():
            self.refresh_list()
            return

        self.history_list.clear()

        records = self.history_manager.search(query=text, limit=100)

        if not records:
            item = QListWidgetItem("未找到匹配记录")
            item.setForeground(QColor(COLORS['text_secondary']))
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.history_list.addItem(item)
            return

        for record in records:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, record['id'])

            sim_color = get_similarity_color(record['similarity'])
            display_text = (
                f"相似度: {record['similarity']}%\n"
                f"标准: {record['ref_preview']}\n"
                f"待测: {record['query_preview']}\n"
                f"时间: {record['timestamp'][:16]}"
            )

            item.setText(display_text)
            item.setForeground(QColor(sim_color))

            self.history_list.addItem(item)

    def _on_sort_changed(self, index: int):
        """排序方式改变"""
        self.refresh_list()

    def _on_item_double_clicked(self, item: QListWidgetItem):
        """双击项目"""
        record_id = item.data(Qt.UserRole)
        if record_id:
            self.record_selected.emit(record_id)

    def _show_context_menu(self, position):
        """显示上下文菜单"""
        item = self.history_list.itemAt(position)
        if not item:
            return

        record_id = item.data(Qt.UserRole)
        if not record_id:
            return

        menu = QMenu()

        view_action = QAction("查看详情", self)
        view_action.triggered.connect(lambda: self.record_selected.emit(record_id))
        menu.addAction(view_action)

        menu.addSeparator()

        delete_action = QAction("删除记录", self)
        delete_action.triggered.connect(lambda: self._delete_record(record_id))
        menu.addAction(delete_action)

        menu.exec_(self.history_list.mapToGlobal(position))

    def _delete_record(self, record_id: str):
        """删除记录"""
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除这条记录吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.history_manager.delete(record_id)
            self.refresh_list()
            self.record_deleted.emit(record_id)

    def _clear_all_history(self):
        """清空所有历史记录"""
        reply = QMessageBox.question(
            self, "确认清空",
            "确定要清空所有历史记录吗？此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            count = self.history_manager.clear_all()
            self.refresh_list()
            QMessageBox.information(self, "完成", f"已清空 {count} 条记录")
