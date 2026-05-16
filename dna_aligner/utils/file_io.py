"""
文件导入导出工具
支持FASTA、CSV等格式的序列导入，以及多种格式的结果导出
"""
import csv
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from ..models.alignment_result import AlignmentResult


class FileIO:
    """文件导入导出工具类"""

    @staticmethod
    def import_fasta(file_path: str) -> List[Dict[str, str]]:
        """
        从FASTA格式文件导入序列

        Args:
            file_path: FASTA文件路径

        Returns:
            List[Dict]: 序列列表，每个元素包含name和sequence
        """
        sequences = []
        current_name = ""
        current_seq = []

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                if line.startswith('>'):
                    # 保存之前的序列
                    if current_name and current_seq:
                        sequences.append({
                            'name': current_name,
                            'sequence': ''.join(current_seq)
                        })
                    # 开始新序列
                    current_name = line[1:].strip()
                    current_seq = []
                else:
                    current_seq.append(line.upper())

            # 保存最后一个序列
            if current_name and current_seq:
                sequences.append({
                    'name': current_name,
                    'sequence': ''.join(current_seq)
                })

        return sequences

    @staticmethod
    def import_csv(file_path: str, sequence_column: int = 0, name_column: Optional[int] = None) -> List[Dict[str, str]]:
        """
        从CSV文件导入序列

        Args:
            file_path: CSV文件路径
            sequence_column: 序列所在列的索引
            name_column: 名称所在列的索引（可选）

        Returns:
            List[Dict]: 序列列表
        """
        sequences = []

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)  # 跳过表头

            for i, row in enumerate(reader):
                if len(row) > sequence_column:
                    seq = row[sequence_column].strip().upper()
                    name = row[name_column].strip() if name_column is not None and len(row) > name_column else f"Sequence_{i+1}"
                    sequences.append({
                        'name': name,
                        'sequence': seq
                    })

        return sequences

    @staticmethod
    def import_txt(file_path: str, delimiter: str = '\n') -> List[Dict[str, str]]:
        """
        从纯文本文件导入序列（每行一个序列）

        Args:
            file_path: 文本文件路径
            delimiter: 分隔符

        Returns:
            List[Dict]: 序列列表
        """
        sequences = []

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split(delimiter)

            for i, line in enumerate(lines):
                seq = line.strip().upper()
                if seq:
                    sequences.append({
                        'name': f"Sequence_{i+1}",
                        'sequence': seq
                    })

        return sequences

    @staticmethod
    def import_sequences(file_path: str) -> List[Dict[str, str]]:
        """
        根据文件扩展名自动选择导入方式

        Args:
            file_path: 文件路径

        Returns:
            List[Dict]: 序列列表
        """
        ext = Path(file_path).suffix.lower()

        if ext in ('.fasta', '.fa', '.fna'):
            return FileIO.import_fasta(file_path)
        elif ext == '.csv':
            return FileIO.import_csv(file_path)
        elif ext in ('.txt', '.text'):
            return FileIO.import_txt(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {ext}")

    @staticmethod
    def export_csv(results: List[AlignmentResult], file_path: str):
        """
        导出比对结果为CSV格式

        Args:
            results: 比对结果列表
            file_path: 输出文件路径
        """
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # 写入表头
            writer.writerow([
                'ID', '时间', '标准序列', '待测序列',
                '比对后标准序列', '比对后待测序列', '匹配标记',
                '起始位置', '结束位置', '相似度(%)', '得分', '设备'
            ])

            # 写入数据
            for result in results:
                writer.writerow([
                    result.alignment_id or '',
                    result.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    result.ref_original,
                    result.query_original,
                    result.ref_alignment,
                    result.query_alignment,
                    result.match_mark,
                    result.start_pos,
                    result.end_pos,
                    result.similarity,
                    result.score,
                    result.device_info
                ])

    @staticmethod
    def export_json(results: List[AlignmentResult], file_path: str):
        """
        导出比对结果为JSON格式

        Args:
            results: 比对结果列表
            file_path: 输出文件路径
        """
        data = {
            'export_time': datetime.now().isoformat(),
            'total_results': len(results),
            'results': [result.to_dict() for result in results]
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def export_text(results: List[AlignmentResult], file_path: str):
        """
        导出比对结果为文本格式

        Args:
            results: 比对结果列表
            file_path: 输出文件路径
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("DNA序列比对结果报告\n")
            f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总记录数: {len(results)}\n")
            f.write("=" * 60 + "\n\n")

            for i, result in enumerate(results, 1):
                f.write(f"--- 记录 {i} ---\n")
                f.write(f"ID: {result.alignment_id or 'N/A'}\n")
                f.write(f"时间: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"标准序列: {result.ref_original}\n")
                f.write(f"待测序列: {result.query_original}\n")
                f.write(f"比对结果:\n")
                f.write(f"  标准: {result.ref_alignment}\n")
                f.write(f"  待测: {result.query_alignment}\n")
                f.write(f"  标记: {result.match_mark}\n")
                f.write(f"位置: {result.start_pos}-{result.end_pos}\n")
                f.write(f"相似度: {result.similarity}%\n")
                f.write(f"得分: {result.score}\n")
                f.write(f"设备: {result.device_info}\n\n")

    @staticmethod
    def export_results(results: List[AlignmentResult], file_path: str, format: str = 'auto'):
        """
        导出比对结果（自动检测格式）

        Args:
            results: 比对结果列表
            file_path: 输出文件路径
            format: 输出格式（'csv', 'json', 'txt', 'auto'）
        """
        if format == 'auto':
            ext = Path(file_path).suffix.lower()
            if ext == '.csv':
                format = 'csv'
            elif ext == '.json':
                format = 'json'
            else:
                format = 'txt'

        if format == 'csv':
            FileIO.export_csv(results, file_path)
        elif format == 'json':
            FileIO.export_json(results, file_path)
        else:
            FileIO.export_text(results, file_path)
