"""
CPU版本的DNA序列比对引擎
使用NumPy优化的Smith-Waterman算法
"""
import numpy as np
from typing import Tuple
from .base_aligner import DNAAligner
from ..models.alignment_result import AlignmentResult


class CPUDNAAligner(DNAAligner):
    """CPU版本的DNA序列比对引擎"""

    def __init__(self, match: int = 5, mismatch: int = -3, gap: int = -4):
        super().__init__(match, mismatch, gap)
        self._device_name = "CPU (NumPy)"

    def get_device_info(self) -> str:
        return self._device_name

    def align(self, ref_seq: str, query_seq: str) -> AlignmentResult:
        """执行CPU版本的Smith-Waterman局部比对"""
        ref = self.validate_sequence(ref_seq)
        query = self.validate_sequence(query_seq)

        len_ref = len(ref)
        len_query = len(query)

        # 预计算匹配/不匹配矩阵（向量化，消除逐字符比较）
        ref_arr = np.array(list(ref), dtype='U1')
        query_arr = np.array(list(query), dtype='U1')
        match_matrix = np.where(
            query_arr[:, None] == ref_arr[None, :],
            self.MATCH, self.MISMATCH
        ).astype(np.int32)

        # 初始化得分矩阵和回溯矩阵
        score = np.zeros((len_query + 1, len_ref + 1), dtype=np.int32)
        trace = np.zeros((len_query + 1, len_ref + 1), dtype=np.int8)

        max_score = 0
        max_i, max_j = 0, 0

        # 填充得分矩阵
        for i in range(1, len_query + 1):
            for j in range(1, len_ref + 1):
                diag = score[i - 1, j - 1] + match_matrix[i - 1, j - 1]
                up = score[i - 1, j] + self.GAP
                left = score[i, j - 1] + self.GAP

                current = max(diag, up, left, 0)
                score[i, j] = current

                if current == 0:
                    trace[i, j] = 0
                elif current == diag:
                    trace[i, j] = 1
                elif current == up:
                    trace[i, j] = 2
                else:
                    trace[i, j] = 3

                if current > max_score:
                    max_score = current
                    max_i, max_j = i, j

        # 回溯
        align_ref, align_query = [], []
        i, j = max_i, max_j

        while i > 0 and j > 0 and trace[i, j] != 0:
            t = trace[i, j]
            if t == 1:
                align_ref.append(ref[j - 1])
                align_query.append(query[i - 1])
                i -= 1
                j -= 1
            elif t == 2:
                align_ref.append('-')
                align_query.append(query[i - 1])
                i -= 1
            elif t == 3:
                align_ref.append(ref[j - 1])
                align_query.append('-')
                j -= 1

        align_ref = ''.join(reversed(align_ref))
        align_query = ''.join(reversed(align_query))

        similarity = self.calculate_similarity(align_ref, align_query)
        match_mark = self.generate_match_mark(align_ref, align_query)

        return AlignmentResult(
            ref_alignment=align_ref,
            query_alignment=align_query,
            ref_original=ref,
            query_original=query,
            start_pos=j,
            end_pos=max_j - 1,
            similarity=similarity,
            score=max_score,
            match_mark=match_mark,
            device_info=self.get_device_info()
        )
