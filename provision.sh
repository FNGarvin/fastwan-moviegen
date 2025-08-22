#!/usr/bin/bash

#download aria2c so we can multithread downloads
apt update && apt install -y aria2
#download model, text encoder, vae, and fastwan lora
cd /workspace/madapps/ComfyUI/models
aria2c -x 16 -s 16 -o diffusion_models/wan2.2_ti2v_5B_fp16.safetensors "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors?download=true"
aria2c -x 16 -s 16 -o text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors?download=true"
aria2c -x 16 -s 16 -o vae/wan2.2_vae.safetensors "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan2.2_vae.safetensors?download=true"
aria2c -x 16 -s 16 -o loras/Wan2_2_5B_FastWanFullAttn_lora_rank_128_bf16.safetensors "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/FastWan/Wan2_2_5B_FastWanFullAttn_lora_rank_128_bf16.safetensors?download=true"
#download a custom node for convenience/gui
cd /workspace/madapps/ComfyUI/custom_nodes
git clone https://github.com/FNGarvin/fastwan-moviegen.git
#activate venv and install xformers
source /workspace/madapps/ComfyUI/.venv/bin/activate
# Get the CUDA version from nvidia-smi
cuda_version=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | awk -F'.' '{print $1"."$2}')
# Check for CUDA 12.9 or other versions and install accordingly
if [ "$cuda_version" = "12.9" ]; then
    pip3 install -U xformers --index-url https://download.pytorch.org/whl/cu129
elif [ "$cuda_version" = "12.8" ]; then
    pip3 install -U xformers --index-url https://download.pytorch.org/whl/cu128
fi
#restart ComfyUI so it uses xformers
pkill -f "python.*main.py" || true
cd /workspace/madapps/ComfyUI/
nohup python main.py --listen 0.0.0.0 --port 8188 >/dev/null 2>&1 &
