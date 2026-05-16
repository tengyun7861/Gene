"""
CUDA加速的DNA序列比对引擎
使用PyTorch GPU加速Smith-Waterman算法
行级向量化：diag和up批量计算，仅left依赖逐列扫描
"""
from typing import Tuple, List
from .base_aligner import DNAAligner
from ..models.alignment_result import AlignmentResult


class CUDADNAAligner(DNAAligner):
    """CUDA加速的DNA序列比对引擎"""

    # 碱基到整数的映射
    BASE_TO_INT = {'A': 0, 'T': 1, 'C': 2, 'G': 3}

    def __init__(self, match: int = 5, mismatch: int = -3, gap: int = -4):
        super().__init__(match, mismatch, gap)
        
        # 延迟导入torch，避免模块加载时触发CUDA DLL初始化
        import torch
        
        # 先保存torch引用
        self._torch = torch

        if not self._torch.cuda.is_available():
            raise RuntimeError("CUDA不可用，无法初始化GPU比对引擎")

        self.device = self._torch.device('cuda')
        self._device_name = self._torch.cuda.get_device_name(0)

    def get_device_info(self) -> str:
        return f"GPU: {self._device_name}"

    def _seq_to_tensor(self, seq: str):
        """将DNA序列转换为整数张量"""
        return self._torch.tensor(
            [self.BASE_TO_INT[c] for c in seq],
            dtype=self._torch.int32, device=self.device
        )

    def _compute_match_matrix(self, ref_tensor, query_tensor):
        """向量化计算匹配/不匹配矩阵"""
        return self._torch.where(
            query_tensor.unsqueeze(1) == ref_tensor.unsqueeze(0),
            self.MATCH, self.MISMATCH
        )

    def align(self, ref_seq: str, query_seq: str) -> AlignmentResult:
        """
        执行CUDA加速的Smith-Waterman局部比对
        行级向量化：diag和up用GPU批量计算，left依赖逐列扫描
        """
        ref = self.validate_sequence(ref_seq)
        query = self.validate_sequence(query_seq)

        len_ref = len(ref)
        len_query = len(query)

        # 预计算匹配矩阵（向量化，一次GPU操作）
        ref_tensor = self._seq_to_tensor(ref)
        query_tensor = self._seq_to_tensor(query)
        match_matrix = self._compute_match_matrix(ref_tensor, query_tensor)

        # 初始化矩阵
        score = self._torch.zeros(len_query + 1, len_ref + 1, dtype=self._torch.int32, device=self.device)
        trace = self._torch.zeros(len_query + 1, len_ref + 1, dtype=self._torch.int8, device=self.device)

        max_score = 0
        max_i, max_j = 0, 0

        gap = self.GAP

        # 逐行填充（行级向量化）
        for i in range(1, len_query + 1):
            # diag 和 up 向量化计算（一次GPU操作处理整行）
            diag = score[i - 1, :-1] + match_matrix[i - 1]
            up = score[i - 1, 1:] + gap
            row_max = self._torch.max(diag, up).clamp(min=0)

            # left 依赖逐列扫描（无法并行化）
            for j in range(1, len_ref + 1):
                left = score[i, j - 1] + gap
                val = max(row_max[j - 1].item(), left)
                score[i, j] = val

                # 记录回溯方向
                if val == 0:
                    trace[i, j] = 0
                elif val == row_max[j - 1].item() and diag[j - 1].item() >= up[j - 1].item():
                    trace[i, j] = 1  # 对角线
                elif val == row_max[j - 1].item():
                    trace[i, j] = 2  # 上方
                else:
                    trace[i, j] = 3  # 左方

                if val > max_score:
                    max_score = val
                    max_i, max_j = i, j

        # 回溯
        align_ref, align_query = [], []
        i, j = max_i, max_j

        while i > 0 and j > 0 and trace[i, j].item() != 0:
            t = trace[i, j].item()
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

    def align_batch(self, ref_seq: str, query_seqs: List[str]) -> List[AlignmentResult]:
        """
        批量比对：多条待测序列与同一条标准序列比对
        使用3D张量批量处理，所有序列对同时填充同一行

        Args:
            ref_seq: 标准DNA序列
            query_seqs: 待测DNA序列列表

        Returns:
            List[AlignmentResult]: 比对结果列表
        """
        ref = self.validate_sequence(ref_seq)
        queries = [self.validate_sequence(q) for q in query_seqs]

        batch_size = len(queries)
        len_ref = len(ref)
        max_query_len = max(len(q) for q in queries)

        # 预计算参考序列张量
        ref_tensor = self._seq_to_tensor(ref)

        # 填充待测序列到相同长度，创建3D张量
        padded_queries = self._torch.zeros(batch_size, max_query_len, dtype=self._torch.int32, device=self.device)
        query_masks = self._torch.zeros(batch_size, max_query_len, dtype=self._torch.bool, device=self.device)
        query_lengths = []

        for idx, q in enumerate(queries):
            q_tensor = self._seq_to_tensor(q)
            q_len = len(q)
            padded_queries[idx, :q_len] = q_tensor
            query_masks[idx, :q_len] = True
            query_lengths.append(q_len)

        # 批量计算匹配矩阵 [batch_size, max_query_len, len_ref]
        match_matrix = self._torch.where(
            padded_queries.unsqueeze(2) == ref_tensor.unsqueeze(0).unsqueeze(0),
            self.MATCH, self.MISMATCH
        )

        # 初始化3D得分矩阵和回溯矩阵
        score = self._torch.zeros(batch_size, max_query_len + 1, len_ref + 1, dtype=self._torch.int32, device=self.device)
        trace = self._torch.zeros(batch_size, max_query_len + 1, len_ref + 1, dtype=self._torch.int8, device=self.device)

        max_scores = self._torch.zeros(batch_size, dtype=self._torch.int32, device=self.device)
        max_is = self._torch.zeros(batch_size, dtype=self._torch.int64, device=self.device)
        max_js = self._torch.zeros(batch_size, dtype=self._torch.int64, device=self.device)

        gap = self.GAP

        # 逐行批量填充
        for i in range(1, max_query_len + 1):
            # 检查哪些序列在当前行有效
            valid_mask = (i - 1) < query_lengths

            # diag 和 up 批量向量化 [batch_size, len_ref]
            diag = score[:, i - 1, :-1] + match_matrix[:, i - 1, :]
            up = score[:, i - 1, 1:] + gap
            row_max = self._torch.max(diag, up).clamp(min=0)

            # left 逐列扫描（但同时处理整个batch）
            for j in range(1, len_ref + 1):
                left = score[:, i, j - 1] + gap
                vals = self._torch.max(row_max[:, j - 1], left)

                # 只更新有效序列
                vals = vals * valid_mask
                score[:, i, j] = vals

                # 记录回溯方向
                is_zero = (vals == 0)
                is_diag = (~is_zero) & (diag[:, j - 1] >= up[:, j - 1]) & (vals == row_max[:, j - 1])
                is_up = (~is_zero) & (~is_diag) & (vals == row_max[:, j - 1])
                is_left = (~is_zero) & (~is_diag) & (~is_up)

                trace[:, i, j] = self._torch.where(is_zero, 0,
                                   self._torch.where(is_diag, 1,
                                   self._torch.where(is_up, 2, 3))).to(self._torch.int8)

                # 更新最大得分
                new_max = vals > max_scores
                max_scores = self._torch.where(new_max, vals, max_scores)
                max_is = self._torch.where(new_max, self._torch.tensor(i, device=self.device), max_is)
                max_js = self._torch.where(new_max, self._torch.tensor(j, device=self.device), max_js)

        # 逐条回溯
        results = []
        for idx in range(batch_size):
            q = queries[idx]
            mi, mj = max_is[idx].item(), max_js[idx].item()

            align_ref, align_query = [], []
            i, j = mi, mj

            while i > 0 and j > 0 and trace[idx, i, j].item() != 0:
                t = trace[idx, i, j].item()
                if t == 1:
                    align_ref.append(ref[j - 1])
                    align_query.append(q[i - 1])
                    i -= 1
                    j -= 1
                elif t == 2:
                    align_ref.append('-')
                    align_query.append(q[i - 1])
                    i -= 1
                elif t == 3:
                    align_ref.append(ref[j - 1])
                    align_query.append('-')
                    j -= 1

            align_ref = ''.join(reversed(align_ref))
            align_query = ''.join(reversed(align_query))

            similarity = self.calculate_similarity(align_ref, align_query)
            match_mark = self.generate_match_mark(align_ref, align_query)

            results.append(AlignmentResult(
                ref_alignment=align_ref,
                query_alignment=align_query,
                ref_original=ref,
                query_original=q,
                start_pos=j,
                end_pos=mj - 1,
                similarity=similarity,
                score=max_scores[idx].item(),
                match_mark=match_mark,
                device_info=self.get_device_info()
            ))

        return results
