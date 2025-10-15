#!/bin/bash

echo "🧹 Очистка установки PyTorch с CUDA..."

# Удаляем PyTorch и связанные пакеты
echo "🗑️ Удаляем PyTorch и CUDA пакеты..."
pip uninstall torch torchvision torchaudio -y
pip uninstall nvidia-cuda-runtime-cu12 nvidia-cudnn-cu12 nvidia-cufft-cu12 -y
pip uninstall nvidia-cufile-cu12 nvidia-curand-cu12 nvidia-cusolver-cu12 -y
pip uninstall nvidia-cusparse-cu12 nvidia-cusparselt-cu12 -y

# Очищаем кэш pip
echo "🧽 Очищаем кэш pip..."
pip cache purge

# Устанавливаем CPU версию PyTorch
echo "📦 Устанавливаем PyTorch CPU версию..."
pip install torch==1.13.1+cpu torchvision==0.14.1+cpu torchaudio==0.13.1+cpu --index-url https://download.pytorch.org/whl/cpu

echo "✅ Очистка завершена! Теперь установлен PyTorch CPU версия."
echo "💡 Размер установки уменьшен с ~2GB до ~200MB"
