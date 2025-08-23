#!/usr/bin/env bash
#
# Title:    comfyui-provisioner.sh
# Author:   FNGarvin
# License:  MIT
#
#END OF HEADER

# --- Configuration ---
# Define base paths to avoid using 'cd'. This makes the script more robust.
readonly COMFYUI_DIR="/workspace/madapps/ComfyUI"
readonly VENV_PATH="${COMFYUI_DIR}/.venv/bin/activate"

# --- Dependencies ---
echo "INFO: Updating package list and installing aria2..."
apt-get update && apt-get install -y --no-install-recommends aria2

# --- Model & Node Downloads ---
echo "INFO: Downloading models and custom nodes..."
# Use the --dir option for aria2c to specify output location directly.
# Models
aria2c -x 16 -s 16 --dir="${COMFYUI_DIR}/models/diffusion_models" -o wan2.2_ti2v_5B_fp16.safetensors "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors?download=true"
aria2c -x 16 -s 16 --dir="${COMFYUI_DIR}/models/text_encoders" -o umt5_xxl_fp8_e4m3fn_scaled.safetensors "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors?download=true"
aria2c -x 16 -s 16 --dir="${COMFYUI_DIR}/models/vae" -o wan2.2_vae.safetensors "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan2.2_vae.safetensors?download=true"
aria2c -x 16 -s 16 --dir="${COMFYUI_DIR}/models/loras" -o Wan2_2_5B_FastWanFullAttn_lora_rank_128_bf16.safetensors "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/FastWan/Wan2_2_5B_FastWanFullAttn_lora_rank_128_bf16.safetensors?download=true"

# Custom Node
# Specify the target directory directly in the git clone command.
git clone https://github.com/FNGarvin/fastwan-moviegen.git "${COMFYUI_DIR}/custom_nodes/fastwan-moviegen"

# --- Python Environment & Xformers Installation ---
echo "INFO: Activating Python venv and installing xformers..."
# Activate the virtual environment
# shellcheck source=/dev/null
source "${VENV_PATH}"

# Dynamically detect the CUDA version PyTorch was built against.
# It gets the version (e.g., "12.1"), removes the dot ("121"), and creates the wheel name ("cu121").
readonly CUDA_VERSION_STR=$(python -c 'import torch; print(torch.version.cuda)')
readonly CU_WHL_VERSION="cu$(echo "${CUDA_VERSION_STR}" | tr -d '.')"
echo "INFO: Detected PyTorch CUDA version ${CUDA_VERSION_STR}. Installing xformers for ${CU_WHL_VERSION}."

pip3 install --no-cache-dir -U xformers --index-url "https://download.pytorch.org/whl/${CU_WHL_VERSION}"

# --- Restart ComfyUI Service ---
echo "INFO: Restarting ComfyUI service..."
# Use the full path to make the process identification more specific and less likely to kill unrelated processes.
pkill -f "main.py" || true

# Start the server using its full path and redirect output.
nohup python "${COMFYUI_DIR}/main.py" --listen 0.0.0.0 --port 8188 > "${COMFYUI_DIR}/comfyui.log" 2>&1 &

echo "INFO: Provisioning complete. ComfyUI is starting."

#END OF comfyui-provisioner.sh
