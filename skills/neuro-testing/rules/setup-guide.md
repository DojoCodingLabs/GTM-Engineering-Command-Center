# Tribe v2 Setup Guide

## Local Installation (Recommended)

### Requirements

- **Python**: 3.11 or higher
- **GPU**: NVIDIA CUDA GPU recommended (RTX 3060+ or equivalent)
  - CPU works but is ~10x slower (2-5 min per creative vs 10-30 sec)
- **Disk**: ~4GB for model weights (cached after first download)
- **RAM**: 8GB minimum, 16GB recommended

### Quick Install

```bash
# Option 1: Install from PyPI
pip install tribev2

# Option 2: Install from source
git clone https://github.com/facebookresearch/tribev2.git
cd tribev2
pip install -e .

# Option 3: Use the plugin's setup script
bash ${CLAUDE_PLUGIN_ROOT}/scripts/neuro-setup.sh
```

### First Run (Downloads Model Weights)

```python
from tribev2 import TribeModel

# This downloads ~2-4GB weights on first run
model = TribeModel.from_pretrained(
    "facebook/tribev2",
    cache_folder=".gtm/models/tribev2/"
)

# Test with a sample
df = model.get_events_dataframe(video_path="path/to/test.mp4")
preds, segments = model.predict(events=df)
print(f"Prediction shape: {preds.shape}")  # (n_timesteps, ~20484)
```

### Using the Plugin Setup Script

The plugin includes `scripts/neuro-setup.sh` which automates the full setup:

```bash
bash scripts/neuro-setup.sh
```

This script:
1. Checks Python version (requires 3.11+)
2. Checks for GPU (nvidia-smi)
3. Creates a virtualenv at `.gtm/models/tribev2-env/`
4. Installs tribev2 + dependencies
5. Downloads model weights to `.gtm/models/tribev2/`
6. Runs a test inference
7. Reports readiness

## Google Colab Fallback (No Local GPU)

If you don't have a local GPU, use Google Colab:

1. The neuro-analyst agent generates a Colab notebook at `.gtm/neuro-tests/colab-{date}.ipynb`
2. Upload the notebook to Google Colab (colab.research.google.com)
3. Set runtime type to GPU (Runtime → Change runtime type → T4 GPU)
4. Upload your creative files to the Colab runtime
5. Run all cells
6. Copy the JSON output from the last cell
7. Paste it when the agent asks for results

The notebook includes:
- tribev2 installation
- Model loading
- Creative processing (image-to-video conversion)
- ROI extraction
- Score computation
- JSON output for pasting back

## Meta AI Demo (Quick Preview)

For a fast qualitative check without any installation:

1. Navigate to `aidemos.atmeta.com/tribev2`
2. Upload your creative image or video
3. The demo shows a brain activation heatmap
4. Interpret visually:
   - **Bright spots in back of brain** (occipital) = high visual attention
   - **Bright spots in sides** (temporal) = language/face processing
   - **Bright spots in front** (frontal) = decision/planning engagement
   - **Bright spots in middle** (limbic) = emotional response

The agent can automate this via Playwright MCP:
```
browser_navigate → aidemos.atmeta.com/tribev2
browser_fill_form → upload creative file
browser_wait_for → processing complete
browser_take_screenshot → capture brain heatmap
```

## Cache Configuration

Model weights are stored at `.gtm/models/tribev2/` (approximately 2-4GB).

This directory MUST be gitignored. The plugin's `.gitignore` already includes:
```
.gtm/models/
```

If you move projects, you'll need to re-download weights (or copy the cache directory).

## Troubleshooting

### CUDA Not Found
```
RuntimeError: No CUDA GPUs are available
```
**Fix**: Install CUDA toolkit matching your GPU driver. Or use CPU mode (slower but works):
```python
model = TribeModel.from_pretrained("facebook/tribev2", device="cpu")
```

### Out of Memory (GPU)
```
torch.cuda.OutOfMemoryError
```
**Fix**: Reduce batch size or use CPU for large videos. For static images (3-sec video), memory should be minimal. If still failing, the GPU may have < 4GB VRAM — use Colab instead.

### Model Loading Timeout
```
ConnectionError: HTTPSConnectionPool (HuggingFace)
```
**Fix**: HuggingFace may be rate-limited. Wait 5 minutes and retry. Or manually download:
```bash
git lfs install
git clone https://huggingface.co/facebook/tribev2 .gtm/models/tribev2/
```

### FFmpeg Not Found (Image Conversion)
```
FileNotFoundError: ffmpeg not found
```
**Fix**: Install ffmpeg:
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg

# Or use Python fallback (agent handles this automatically)
```

### ImportError: tribev2
```
ModuleNotFoundError: No module named 'tribev2'
```
**Fix**: Ensure you're using the right Python environment:
```bash
# If using the plugin's virtualenv
source .gtm/models/tribev2-env/bin/activate
python -c "from tribev2 import TribeModel; print('OK')"
```

## Hardware Recommendations

| Setup | Speed per Creative | Cost | Best For |
|-------|-------------------|------|----------|
| RTX 4090 (local) | ~5-10 sec | $0 (own hardware) | Daily testing, high volume |
| RTX 3060 (local) | ~15-30 sec | $0 (own hardware) | Regular testing |
| Google Colab (free T4) | ~30-60 sec | Free | Occasional testing |
| Google Colab Pro (A100) | ~5-10 sec | $10/mo | Regular testing without local GPU |
| CPU only (local) | ~2-5 min | $0 | Emergency fallback, single creative |
