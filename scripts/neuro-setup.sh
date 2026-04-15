#!/bin/bash
# GTM Engineering Command Center — Tribe v2 Neural Pre-Testing Setup
# Installs Meta's Tribe v2 brain prediction model for creative pre-testing

set -e

echo "═══════════════════════════════════════════════════════════"
echo "  GTM Command Center — Tribe v2 Neural Pre-Testing Setup"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>/dev/null | grep -oP '\d+\.\d+' | head -1)
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ -z "$PYTHON_VERSION" ]; then
    echo "❌ Python 3 not found. Install Python 3.11+ first."
    exit 1
fi

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    echo "❌ Python $PYTHON_VERSION found. Tribe v2 requires Python 3.11+."
    exit 1
fi
echo "✅ Python $PYTHON_VERSION detected"

# Check for GPU
if command -v nvidia-smi &>/dev/null; then
    GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo "")
    if [ -n "$GPU_INFO" ]; then
        echo "✅ GPU detected: $GPU_INFO"
        HAS_GPU=true
    else
        echo "⚠️  nvidia-smi found but no GPU detected. Using CPU mode (slower)."
        HAS_GPU=false
    fi
else
    echo "⚠️  No NVIDIA GPU detected. CPU mode will work but is ~10x slower."
    echo "   For faster inference, use Google Colab with a free T4 GPU."
    HAS_GPU=false
fi

# Create cache directory
CACHE_DIR=".gtm/models/tribev2"
mkdir -p "$CACHE_DIR"
echo "📁 Cache directory: $CACHE_DIR"

# Create virtualenv
VENV_DIR=".gtm/models/tribev2-env"
if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 Creating virtualenv at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# Activate and install
source "$VENV_DIR/bin/activate"
echo "🔧 Installing tribev2 and dependencies..."
pip install --quiet --upgrade pip
pip install --quiet tribev2

# Verify installation
echo ""
echo "🧪 Testing Tribe v2 installation..."
python3 -c "
from tribev2 import TribeModel
import torch
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'  PyTorch device: {device}')
print(f'  Loading model (first run downloads ~2-4GB weights)...')
model = TribeModel.from_pretrained('facebook/tribev2', cache_folder='$CACHE_DIR')
print(f'  Model loaded successfully!')
print(f'  Output mesh: fsaverage5 (~20K vertices)')
" 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "  ✅ Tribe v2 setup complete!"
    echo ""
    echo "  Mode: $([ "$HAS_GPU" = true ] && echo "GPU (fast)" || echo "CPU (slower)")"
    echo "  Cache: $CACHE_DIR"
    echo "  Venv: $VENV_DIR"
    echo ""
    echo "  Usage: /gtm-neurotest"
    echo "═══════════════════════════════════════════════════════════"
else
    echo ""
    echo "❌ Tribe v2 test failed. Check the error above."
    echo "   Common fixes:"
    echo "   - CUDA: Install matching CUDA toolkit for your GPU driver"
    echo "   - Memory: Ensure 4GB+ RAM available"
    echo "   - Network: Check HuggingFace access for model download"
    exit 1
fi
