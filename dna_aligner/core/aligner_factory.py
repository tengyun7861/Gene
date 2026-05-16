"""
比对引擎工厂
自动检测GPU并选择合适的比对引擎实现
"""
from typing import Optional
from .base_aligner import DNAAligner
from .cpu_aligner import CPUDNAAligner


class AlignerFactory:
    """比对引擎工厂类"""

    @staticmethod
    def create_aligner(
        force_cpu: bool = False,
        match: int = 5,
        mismatch: int = -3,
        gap: int = -4
    ) -> DNAAligner:
        """
        创建比对引擎实例

        Args:
            force_cpu: 强制使用CPU（忽略GPU可用性）
            match: 匹配得分
            mismatch: 不匹配罚分
            gap: 空位罚分

        Returns:
            DNAAligner: 比对引擎实例
        """
        if force_cpu:
            return CPUDNAAligner(match, mismatch, gap)

        try:
            import torch
            if torch.cuda.is_available():
                from .cuda_aligner import CUDADNAAligner
                return CUDADNAAligner(match, mismatch, gap)
        except (OSError, ImportError, RuntimeError):
            pass

        return CPUDNAAligner(match, mismatch, gap)

    @staticmethod
    def get_available_devices() -> dict:
        """
        获取可用设备信息

        Returns:
            dict: 包含设备信息的字典
        """
        devices = {
            'cpu': True,
            'cpu_info': 'CPU (NumPy优化)',
            'cuda_available': False,
            'cuda_devices': []
        }

        try:
            import torch
            if torch.cuda.is_available():
                devices['cuda_available'] = True
                for i in range(torch.cuda.device_count()):
                    devices['cuda_devices'].append({
                        'index': i,
                        'name': torch.cuda.get_device_name(i),
                        'memory': torch.cuda.get_device_properties(i).total_mem
                    })
        except (OSError, ImportError):
            pass

        return devices

    @staticmethod
    def is_gpu_available() -> bool:
        """检查GPU是否可用"""
        try:
            import torch
            return torch.cuda.is_available()
        except (OSError, ImportError):
            return False

    @staticmethod
    def supports_batch(aligner: DNAAligner) -> bool:
        """检查比对引擎是否支持批量比对"""
        return hasattr(aligner, 'align_batch')