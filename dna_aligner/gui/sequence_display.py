"""
彩色碱基序列显示组件
使用 QTextEdit + QTextCursor 渲染带颜色的碱基序列
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QFont, QColor
from PyQt5.QtCore import Qt

from .theme import BASE_COLORS, COLORS


class SequenceDisplayWidget(QWidget):
    """彩色碱基序列显示组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Consolas", 12))
        self.text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px;
                color: {COLORS['text_primary']};
            }}
        """)
        layout.addWidget(self.text_edit)

    def set_alignment(self, ref: str, query: str, mark: str):
        """设置比对结果显示（三行：标准序列、匹配标记、待测序列）"""
        self.text_edit.clear()
        cursor = self.text_edit.textCursor()

        # 标准序列行
        self._insert_label(cursor, "标准: ")
        for i, base in enumerate(ref):
            self._insert_base(cursor, base, BASE_COLORS.get(base, '#8b949e'))
            if i < len(ref) - 1:
                self._insert_text(cursor, " ", '#555555')
        cursor.insertText("\n")

        # 位置标记行（每10个碱基显示位置）
        self._insert_label(cursor, "      ")
        for i in range(len(ref)):
            if (i + 1) % 10 == 0:
                pos_str = str(i + 1)
                self._insert_text(cursor, pos_str, COLORS['text_secondary'])
                # 补齐空格
                spaces = 2 * (10 - len(pos_str)) - 1
                self._insert_text(cursor, " " * max(spaces, 0), '#555555')
                continue
            self._insert_text(cursor, " ", '#555555')
        cursor.insertText("\n")

        # 匹配标记行
        self._insert_label(cursor, "      ")
        for i, m in enumerate(mark):
            if m == '√':
                self._insert_base(cursor, m, COLORS['success'])
            else:
                self._insert_base(cursor, m, COLORS['error'])
            if i < len(mark) - 1:
                self._insert_text(cursor, " ", '#555555')
        cursor.insertText("\n")

        # 待测序列行
        self._insert_label(cursor, "待测: ")
        for i, base in enumerate(query):
            self._insert_base(cursor, base, BASE_COLORS.get(base, '#8b949e'))
            if i < len(query) - 1:
                self._insert_text(cursor, " ", '#555555')
        cursor.insertText("\n")

    def clear(self):
        """清空显示"""
        self.text_edit.clear()

    def _insert_text(self, cursor: QTextCursor, text: str, color: str):
        """插入带颜色的文本"""
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor.insertText(text, fmt)

    def _insert_base(self, cursor: QTextCursor, base: str, color: str):
        """插入单个碱基（带颜色和粗体）"""
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        fmt.setFontWeight(QFont.Bold)
        cursor.insertText(base, fmt)

    def _insert_label(self, cursor: QTextCursor, text: str):
        """插入标签文本"""
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(COLORS['text_secondary']))
        fmt.setFontWeight(QFont.Bold)
        cursor.insertText(text, fmt)
