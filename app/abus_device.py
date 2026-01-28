import torch
import gc
import structlog

logger = structlog.get_logger()

class AbusDevice:
    @staticmethod
    def get_device():
        """
        根据当前系统环境返回最佳的设备 (cuda, mps, 或 cpu)
        """
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            # macOS 硬件加速
            return "mps"
        else:
            return "cpu"

    @staticmethod
    def release_device_memory():
        """
        释放当前设备的内存，支持 CUDA 和 MPS
        """
        gc.collect()
        device = AbusDevice.get_device()
        
        if device == "cuda":
            torch.cuda.empty_cache()
            torch.cuda.reset_max_memory_allocated()
            logger.debug('[abus_device.py] release_device_memory - CUDA memory released')
        elif device == "mps":
            # MPS 内存释放 (目前 PyTorch 并没有像 empty_cache 这样直接的 MPS 接口，
            # 但 gc.collect() 和确保没有引用是关键)
            # 在某些版本的 PyTorch 中，可能会有类似的方法，但在常规情况下
            # 这里的 gc 已经起到了一定作用。
            logger.debug('[abus_device.py] release_device_memory - MPS memory release triggered (gc)')
        else:
            logger.debug('[abus_device.py] release_device_memory - CPU memory release (gc only)')
