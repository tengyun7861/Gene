"""
比对结果数据类
存储DNA序列比对的所有结果信息
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class AlignmentResult:
    """DNA序列比对结果"""

    # 比对后的序列
    ref_alignment: str  # 比对后的标准序列
    query_alignment: str  # 比对后的待测序列

    # 原始序列
    ref_original: str  # 原始标准序列
    query_original: str  # 原始待测序列

    # 比对位置信息
    start_pos: int  # 比对起始位置
    end_pos: int  # 比对结束位置

    # 比对统计信息
    similarity: float  # 相似度百分比
    score: int  # 比对得分
    match_mark: str  # 匹配标记字符串

    # 元数据
    device_info: str = ""  # 使用的设备信息
    timestamp: datetime = field(default_factory=datetime.now)  # 比对时间
    alignment_id: Optional[str] = None  # 比对ID（用于历史记录）

    # 批量比对相关
    batch_index: Optional[int] = None  # 批量比对中的索引
    batch_total: Optional[int] = None  # 批量比对总数

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            dict: 包含所有结果信息的字典
        """
        return {
            'alignment_id': self.alignment_id,
            'timestamp': self.timestamp.isoformat(),
            'ref_original': self.ref_original,
            'query_original': self.query_original,
            'ref_alignment': self.ref_alignment,
            'query_alignment': self.query_alignment,
            'match_mark': self.match_mark,
            'start_pos': self.start_pos,
            'end_pos': self.end_pos,
            'similarity': self.similarity,
            'score': self.score,
            'device_info': self.device_info,
            'batch_index': self.batch_index,
            'batch_total': self.batch_total
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AlignmentResult':
        """
        从字典创建实例

        Args:
            data: 包含结果信息的字典

        Returns:
            AlignmentResult: 比对结果实例
        """
        timestamp = datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else datetime.now()
        return cls(
            alignment_id=data.get('alignment_id'),
            timestamp=timestamp,
            ref_original=data['ref_original'],
            query_original=data['query_original'],
            ref_alignment=data['ref_alignment'],
            query_alignment=data['query_alignment'],
            match_mark=data['match_mark'],
            start_pos=data['start_pos'],
            end_pos=data['end_pos'],
            similarity=data['similarity'],
            score=data['score'],
            device_info=data.get('device_info', ''),
            batch_index=data.get('batch_index'),
            batch_total=data.get('batch_total')
        )

    def get_alignment_length(self) -> int:
        """获取比对长度"""
        return len(self.ref_alignment)

    def get_match_count(self) -> int:
        """获取匹配数量"""
        return self.match_mark.count('√')

    def get_mismatch_count(self) -> int:
        """获取不匹配数量"""
        return self.match_mark.count('×')

    def get_gap_count(self) -> int:
        """获取空位数量"""
        return self.ref_alignment.count('-') + self.query_alignment.count('-')

    def get_summary(self) -> str:
        """
        获取比对结果摘要

        Returns:
            str: 结果摘要字符串
        """
        return (
            f"比对结果摘要:\n"
            f"  序列长度: 标准={len(self.ref_original)}, 待测={len(self.query_original)}\n"
            f"  比对范围: {self.start_pos}-{self.end_pos}\n"
            f"  比对长度: {self.get_alignment_length()}\n"
            f"  匹配数: {self.get_match_count()}\n"
            f"  不匹配数: {self.get_mismatch_count()}\n"
            f"  空位数: {self.get_gap_count()}\n"
            f"  相似度: {self.similarity}%\n"
            f"  得分: {self.score}\n"
            f"  设备: {self.device_info}\n"
            f"  时间: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def __str__(self) -> str:
        """字符串表示"""
        return (
            f"AlignmentResult(similarity={self.similarity}%, "
            f"score={self.score}, "
            f"length={self.get_alignment_length()})"
        )

    def __repr__(self) -> str:
        """开发者友好的字符串表示"""
        return self.__str__()
