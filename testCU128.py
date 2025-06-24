import torch
import time

print(f"Torch version: {torch.__version__}")
print(f"CUDA version: {torch.version.cuda}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"Current device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No CUDA device'}")

# Test trên CPU
x_cpu = torch.randn(10000, 10000)
start_cpu = time.time()
y_cpu = torch.matmul(x_cpu, x_cpu)
print(f"CPU matmul time: {time.time() - start_cpu:.4f} seconds")

# Test trên GPU
x_gpu = torch.randn(10000, 10000, device='cuda')
start_gpu = time.time()
y_gpu = torch.matmul(x_gpu, x_gpu)
torch.cuda.synchronize()  # Đồng bộ GPU
print(f"GPU matmul time: {time.time() - start_gpu:.4f} seconds")
