"""
生物信息风格主题
深色背景 + 绿色/青色主色调
"""

# 颜色常量
COLORS = {
    # 背景色
    'bg_primary': '#0d1117',
    'bg_secondary': '#161b22',
    'bg_tertiary': '#21262d',
    'bg_hover': '#30363d',

    # 强调色
    'accent_green': '#00ff88',
    'accent_cyan': '#00d4aa',
    'accent_teal': '#0ea5e9',

    # 文本色
    'text_primary': '#e6edf3',
    'text_secondary': '#8b949e',
    'text_accent': '#00ff88',

    # 状态色
    'success': '#00ff88',
    'warning': '#ffd93d',
    'error': '#ff6b6b',

    # 边框
    'border': '#30363d',
    'border_focus': '#00ff88',
}

# 碱基颜色映射
BASE_COLORS = {
    'A': '#ff6b6b',   # 红色 - 腺嘌呤
    'T': '#ffd93d',   # 黄色 - 胸腺嘧啶
    'C': '#6bcb77',   # 绿色 - 胞嘧啶
    'G': '#4d96ff',   # 蓝色 - 鸟嘌呤
    '-': '#555555',   # 灰色 - 空位
}


def get_base_color(base: str) -> str:
    """获取碱基对应的颜色"""
    return BASE_COLORS.get(base.upper(), '#8b949e')


def get_similarity_color(similarity: float) -> str:
    """根据相似度返回颜色"""
    if similarity >= 80:
        return COLORS['success']
    elif similarity >= 60:
        return COLORS['warning']
    return COLORS['error']


# 全局 QSS 样式表
STYLESHEET = """
/* ===== 主窗口 ===== */
QMainWindow {
    background-color: #0d1117;
}

QWidget {
    background-color: #0d1117;
    color: #e6edf3;
}

/* ===== 菜单栏 ===== */
QMenuBar {
    background-color: #161b22;
    border-bottom: 1px solid #30363d;
    color: #e6edf3;
}

QMenuBar::item {
    padding: 6px 12px;
    background: transparent;
}

QMenuBar::item:selected {
    background-color: #30363d;
}

QMenu {
    background-color: #161b22;
    border: 1px solid #30363d;
    color: #e6edf3;
}

QMenu::item {
    padding: 6px 20px;
}

QMenu::item:selected {
    background-color: #00ff88;
    color: #0d1117;
}

/* ===== 工具栏 ===== */
QToolBar {
    background-color: #161b22;
    border-bottom: 1px solid #30363d;
    spacing: 5px;
    padding: 5px;
}

QToolBar QToolButton {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 6px 12px;
    color: #e6edf3;
}

QToolBar QToolButton:hover {
    background-color: #30363d;
    border-color: #00d4aa;
}

/* ===== 状态栏 ===== */
QStatusBar {
    background-color: #161b22;
    border-top: 1px solid #30363d;
    color: #8b949e;
}

QStatusBar QLabel {
    color: #8b949e;
    padding: 0 5px;
}

/* ===== 分组框 ===== */
QGroupBox {
    font-weight: bold;
    border: 1px solid #30363d;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 18px;
    background-color: #161b22;
    color: #00d4aa;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #00d4aa;
}

/* ===== 按钮 ===== */
QPushButton {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 16px;
    color: #e6edf3;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #30363d;
    border-color: #00d4aa;
}

QPushButton:pressed {
    background-color: #0d1117;
}

QPushButton#primary_btn {
    background-color: #00ff88;
    color: #0d1117;
    border: none;
    font-weight: bold;
}

QPushButton#primary_btn:hover {
    background-color: #33ffaa;
}

QPushButton#primary_btn:pressed {
    background-color: #00cc6a;
}

QPushButton#danger_btn {
    background-color: #ff6b6b;
    color: #0d1117;
    border: none;
}

QPushButton#danger_btn:hover {
    background-color: #ff8888;
}

/* ===== 输入框 ===== */
QLineEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px;
    color: #e6edf3;
    selection-background-color: #00ff88;
    selection-color: #0d1117;
}

QLineEdit:focus {
    border: 2px solid #00ff88;
}

QTextEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px;
    color: #e6edf3;
    font-family: 'Consolas', 'Courier New', monospace;
    selection-background-color: #00ff88;
    selection-color: #0d1117;
}

QTextEdit:focus {
    border: 2px solid #00ff88;
}

/* ===== 标签页 ===== */
QTabWidget::pane {
    border: 1px solid #30363d;
    border-radius: 6px;
    background-color: #161b22;
}

QTabBar::tab {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    color: #8b949e;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #161b22;
    color: #00ff88;
    border-bottom: 2px solid #00ff88;
}

QTabBar::tab:hover:!selected {
    background-color: #30363d;
    color: #e6edf3;
}

/* ===== 进度条 ===== */
QProgressBar {
    border: 1px solid #30363d;
    border-radius: 6px;
    text-align: center;
    background-color: #21262d;
    color: #e6edf3;
    height: 20px;
}

QProgressBar::chunk {
    background-color: #00ff88;
    border-radius: 5px;
}

/* ===== 表格 ===== */
QTableWidget {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    gridline-color: #21262d;
    color: #e6edf3;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:selected {
    background-color: #00ff88;
    color: #0d1117;
}

QTableWidget::item:hover {
    background-color: #21262d;
}

QHeaderView::section {
    background-color: #161b22;
    color: #00d4aa;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #30363d;
    font-weight: bold;
}

/* ===== 列表 ===== */
QListWidget {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #e6edf3;
    outline: none;
}

QListWidget::item {
    padding: 10px;
    border-bottom: 1px solid #21262d;
}

QListWidget::item:selected {
    background-color: #00ff88;
    color: #0d1117;
}

QListWidget::item:hover {
    background-color: #21262d;
}

/* ===== 下拉框 ===== */
QComboBox {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 12px;
    color: #e6edf3;
}

QComboBox:hover {
    border-color: #00d4aa;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #161b22;
    border: 1px solid #30363d;
    color: #e6edf3;
    selection-background-color: #00ff88;
    selection-color: #0d1117;
}

/* ===== 滚动条 ===== */
QScrollBar:vertical {
    background-color: #0d1117;
    width: 10px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #30363d;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #00d4aa;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #0d1117;
    height: 10px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #30363d;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #00d4aa;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* ===== 分割器 ===== */
QSplitter::handle {
    background-color: #30363d;
    width: 2px;
}

QSplitter::handle:hover {
    background-color: #00ff88;
}

/* ===== 消息框 ===== */
QMessageBox {
    background-color: #161b22;
}

QMessageBox QLabel {
    color: #e6edf3;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* ===== 工具提示 ===== */
QToolTip {
    background-color: #161b22;
    color: #e6edf3;
    border: 1px solid #00d4aa;
    padding: 4px;
    border-radius: 4px;
}
"""
