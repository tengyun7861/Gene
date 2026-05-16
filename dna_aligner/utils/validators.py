"""
序列验证工具
提供DNA序列的验证和标准化功能
"""
from typing import Set, Tuple, Optional


class SequenceValidator:
    """DNA序列验证器"""

    VALID_DNA: Set[str] = {'A', 'T', 'C', 'G'}

    @classmethod
    def validate_dna(cls, sequence: str) -> Tuple[bool, Optional[str]]:
        """
        验证DNA序列

        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        if not sequence:
            return False, "序列不能为空"

        seq = sequence.upper().strip()
        invalid_chars = set(seq) - cls.VALID_DNA

        if invalid_chars:
            return False, f"序列包含非法字符: {invalid_chars}，仅允许 A/T/C/G"

        return True, None

    @classmethod
    def normalize_sequence(cls, sequence: str) -> str:
        """标准化DNA序列（转大写，去除空白）"""
        return sequence.upper().strip()

    @classmethod
    def calculate_gc_content(cls, sequence: str) -> float:
        """计算GC含量百分比"""
        seq = sequence.upper()
        gc_count = seq.count('G') + seq.count('C')
        return round(gc_count / len(seq) * 100, 2) if len(seq) > 0 else 0.0

    @classmethod
    def validate_batch(cls, sequences: list) -> Tuple[bool, list]:
        """
        批量验证序列

        Returns:
            Tuple[bool, list]: (是否全部有效, 错误信息列表)
        """
        errors = []
        for i, seq in enumerate(sequences):
            is_valid, error = cls.validate_dna(seq)
            if not is_valid:
                errors.append(f"序列 {i+1}: {error}")

        return len(errors) == 0, errors
