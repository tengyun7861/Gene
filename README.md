# DNA序列比对工具

基于Smith-Waterman算法的DNA序列局部比对桌面应用程序，支持GPU加速和批量比对功能。

## 功能特性

- **GPU/CPU双模式**: 自动检测GPU，有则用CUDA加速（行级向量化 + 批量3D张量），无则用CPU
- **生物信息风格界面**: 深色主题 + 绿色/青色主色调，碱基彩色显示
- **单序列比对**: 标准序列 vs 待测序列的局部比对
- **批量比对**: 多条待测序列与同一条标准序列批量比对
- **历史记录**: SQLite数据库存储比对历史，支持搜索和排序
- **文件导入导出**: 支持FASTA、CSV、TXT格式
- **序列验证**: 自动验证DNA序列格式（仅允许A/T/C/G）

## 安装说明

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. GPU支持（可选）

如果需要GPU加速，请安装CUDA版本的PyTorch：

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

如果没有GPU，程序会自动使用CPU版本。

## 使用方法

### 启动程序

```bash
python main.py
```

### 基本操作

1. **单序列比对**:
   - 在"标准DNA序列"输入框中输入参考序列
   - 在"待测DNA序列"输入框中输入待测序列
   - 点击"开始比对"按钮

2. **批量比对**:
   - 切换到"批量比对"标签页
   - 每行输入一条序列，第一条作为标准序列
   - 点击"批量比对"按钮

3. **导入序列文件**:
   - 支持FASTA、CSV、TXT格式
   - 点击"从文件导入"按钮选择文件

4. **查看历史记录**:
   - 左侧面板显示所有比对历史
   - 支持搜索和排序功能
   - 双击记录可查看详情

5. **导出结果**:
   - 点击"导出"按钮
   - 选择导出格式（CSV、JSON、TXT）

## 文件结构

```
基因序列检测/
├── dna_aligner/           # 主程序包
│   ├── core/              # 核心比对引擎
│   │   ├── base_aligner.py    # 抽象基类
│   │   ├── cuda_aligner.py    # GPU版本（行级向量化 + 批量比对）
│   │   ├── cpu_aligner.py     # CPU版本（NumPy优化）
│   │   └── aligner_factory.py # 工厂模式
│   ├── models/            # 数据模型
│   │   ├── alignment_result.py  # 比对结果
│   │   └── history_manager.py   # 历史管理
│   ├── utils/             # 工具模块
│   │   ├── file_io.py         # 文件IO
│   │   └── validators.py      # 序列验证
│   └── gui/               # GUI模块
│       ├── theme.py           # 生物信息风格主题
│       ├── sequence_display.py # 彩色碱基显示组件
│       ├── main_window.py     # 主窗口
│       ├── input_panel.py     # 输入面板
│       ├── result_panel.py    # 结果面板
│       └── history_panel.py   # 历史面板
├── main.py               # 程序入口
├── requirements.txt      # 依赖包
└── README.md             # 说明文档
```

## 技术栈

- **Python 3.8+**
- **PyQt5**: GUI框架
- **PyTorch**: GPU加速计算
- **NumPy**: 数值计算
- **SQLite**: 数据存储

## 算法说明

本工具使用Smith-Waterman算法进行DNA序列局部比对：

- **匹配得分**: 5
- **不匹配罚分**: -3
- **空位罚分**: -4

GPU加速策略：
- 单序列比对：行级向量化（diag/up批量计算，left逐列扫描）
- 批量比对：3D张量处理，所有序列对同时填充同一行

## 注意事项

1. DNA序列仅支持A、T、C、G四个字符
2. 批量比对时第一条序列作为标准序列
3. 历史记录存储在本地SQLite数据库中
4. GPU加速需要NVIDIA显卡和CUDA环境
