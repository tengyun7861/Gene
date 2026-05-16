"""
DNA序列比对引擎抽象基类
定义比对算法的标准接口
"""
from abc import ABC, abstractmethod
from ..models.alignment_result import AlignmentResult
from ..utils.validators import SequenceValidator


class DNAAligner(ABC):
    """DNA序列比对引擎抽象基类"""

    def __init__(self, match: int = 5, mismatch: int = -3, gap: int = -4):
        self.MATCH = match
        self.MISMATCH = mismatch
        self.GAP = gap

    def validate_sequence(self, sequence: str) -> str:
        """验证并标准化DNA序列"""
        is_valid, error = SequenceValidator.validate_dna(sequence)
        if not is_valid:
            raise ValueError(error)
        return SequenceValidator.normalize_sequence(sequence)

    @abstractmethod
    def align(self, ref_seq: str, query_seq: str) -> AlignmentResult:
        """执行DNA序列比对（子类必须实现）"""
        pass

    @abstractmethod
    def get_device_info(self) -> str:
        """获取计算设备信息（子类必须实现）"""
        pass

    def calculate_similarity(self, align_ref: str, align_query: str) -> float:
        """计算序列相似度百分比"""
        total = 0
        for r, q in zip(align_ref, align_query):
            if r == q:
                total += self.MATCH
            elif r == '-' or q == '-':
                total += self.GAP
            else:
                total += self.MISMATCH

        max_possible = len(align_ref) * self.MATCH
        similarity = round(total / max_possible * 100, 1) if max_possible > 0 else 0.0
        return similarity

    def generate_match_mark(self, align_ref: str, align_query: str) -> str:
        """生成匹配标记字符串（√匹配，×不匹配）"""
        return ''.join('√' if r == q else '×' for r, q in zip(align_ref, align_query))
