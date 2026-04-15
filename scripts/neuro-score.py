#!/usr/bin/env python3
"""
GTM Engineering Command Center — Neural Creative Scorer
Uses Meta's Tribe v2 to predict brain response to ad creatives.
Outputs JSON with ROI scores for each creative.

Usage:
    python neuro-score.py --input creative1.png creative2.png --cache-dir .gtm/models/tribev2/
    python neuro-score.py --input video_ad.mp4 --output scores.json
    python neuro-score.py --compare ad_a.png ad_b.png
"""

import argparse
import json
import os
import sys
import time
import subprocess
import tempfile
from pathlib import Path

import numpy as np


# --- ROI Vertex Mappings (fsaverage5, Desikan-Killiany atlas) ---
# Approximate ranges for left hemisphere. Right hemisphere offset: +10242

N_VERTICES_PER_HEMI = 10242

def bilateral(lh_range):
    """Get bilateral vertex indices from left-hemisphere range."""
    lh = list(lh_range)
    rh = [v + N_VERTICES_PER_HEMI for v in lh_range]
    return lh + rh

ROI_VERTICES = {
    'visual_cortex': bilateral(range(0, 3500)),
    'fusiform_face': bilateral(range(5000, 5500)),
    'amygdala_region': bilateral(range(8000, 8300)),
    'hippocampus': bilateral(range(8300, 9200)),
    'wernicke': bilateral(range(6000, 7000)),
    'prefrontal': bilateral(range(14000, 17000)),
    'striatum_region': bilateral(range(9000, 9500)),
}

METRIC_MAP = {
    'attention': 'visual_cortex',
    'face_response': 'fusiform_face',
    'emotion': 'amygdala_region',
    'memory': 'hippocampus',
    'comprehension': 'wernicke',
    'decision': 'prefrontal',
    'reward': 'striatum_region',
}

# Default composite weights (override with calibration file)
DEFAULT_WEIGHTS = {
    'attention': 0.25,
    'emotion': 0.20,
    'memory': 0.20,
    'decision': 0.20,
    'comprehension': 0.10,
    'reward': 0.05,
}


def image_to_video(image_path, output_path, duration=3, fps=30):
    """Convert static image to short video for Tribe v2 input."""
    # Try ffmpeg first
    try:
        subprocess.run([
            'ffmpeg', '-loop', '1', '-i', str(image_path),
            '-c:v', 'libx264', '-t', str(duration),
            '-pix_fmt', 'yuv420p',
            '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2',
            str(output_path), '-y'
        ], capture_output=True, check=True, timeout=30)
        return output_path
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Python fallback
    try:
        from PIL import Image
        import imageio
        img = Image.open(image_path).convert('RGB').resize((1280, 720))
        arr = np.array(img)
        frames = [arr] * (duration * fps)
        imageio.mimwrite(str(output_path), frames, fps=fps)
        return output_path
    except ImportError:
        print(f"ERROR: Neither ffmpeg nor imageio available for image conversion", file=sys.stderr)
        sys.exit(1)


def extract_roi_scores(avg_activation):
    """Extract mean activation for each ROI."""
    scores = {}
    n = len(avg_activation)
    for region, vertices in ROI_VERTICES.items():
        valid = [v for v in vertices if v < n]
        if valid:
            scores[region] = float(np.mean(avg_activation[valid]))
    return scores


def normalize_scores(all_scores):
    """Min-max normalize scores across a batch to 0-100."""
    if len(all_scores) < 2:
        # Single creative: use absolute values, normalize to 50-centered
        return all_scores

    regions = set()
    for s in all_scores:
        regions.update(s.keys())

    bounds = {}
    for region in regions:
        vals = [s.get(region, 0) for s in all_scores]
        bounds[region] = (min(vals), max(vals))

    normalized = []
    for scores in all_scores:
        normed = {}
        for region, val in scores.items():
            lo, hi = bounds[region]
            if hi > lo:
                normed[region] = ((val - lo) / (hi - lo)) * 100
            else:
                normed[region] = 50.0
        normalized.append(normed)
    return normalized


def map_to_metrics(roi_scores):
    """Map ROI region names to marketing metric names."""
    return {metric: roi_scores.get(region, 0) for metric, region in METRIC_MAP.items()}


def compute_composite(metric_scores, weights=None):
    """Compute weighted composite score."""
    w = weights or DEFAULT_WEIGHTS
    return sum(metric_scores.get(m, 0) * w.get(m, 0) for m in w)


def get_verdict(composite):
    """Determine deploy/test/iterate/skip verdict."""
    if composite >= 70:
        return "DEPLOY"
    elif composite >= 55:
        return "TEST"
    elif composite >= 40:
        return "ITERATE"
    else:
        return "SKIP"


def load_calibration(calibration_path=".gtm/learnings/neuro-calibration.md"):
    """Load calibrated weights if available."""
    if not os.path.exists(calibration_path):
        return None
    try:
        with open(calibration_path) as f:
            content = f.read()
        # Parse weights from markdown (look for key: value pairs)
        weights = {}
        for line in content.split('\n'):
            for metric in DEFAULT_WEIGHTS:
                if metric in line.lower() and ':' in line:
                    try:
                        val = float(line.split(':')[-1].strip())
                        weights[metric] = val
                        break
                    except ValueError:
                        pass
        return weights if len(weights) == len(DEFAULT_WEIGHTS) else None
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description='Neural Creative Scorer (Tribe v2)')
    parser.add_argument('--input', nargs='+', required=True, help='Creative file(s) to score')
    parser.add_argument('--cache-dir', default='.gtm/models/tribev2/', help='Model cache directory')
    parser.add_argument('--output', default=None, help='Output JSON file path')
    parser.add_argument('--compare', action='store_true', help='Side-by-side comparison mode')
    parser.add_argument('--device', default=None, help='Force device (cuda/cpu)')
    args = parser.parse_args()

    start_time = time.time()

    # Load model
    print("Loading Tribe v2 model...", file=sys.stderr)
    try:
        from tribev2 import TribeModel
        import torch
        device = args.device or ('cuda' if torch.cuda.is_available() else 'cpu')
        model = TribeModel.from_pretrained('facebook/tribev2', cache_folder=args.cache_dir)
        print(f"Model loaded on {device}", file=sys.stderr)
    except ImportError:
        print(json.dumps({"error": "tribev2 not installed. Run: pip install tribev2"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Model loading failed: {str(e)}"}))
        sys.exit(1)

    # Load calibration weights
    weights = load_calibration() or DEFAULT_WEIGHTS
    calibrated = weights != DEFAULT_WEIGHTS

    # Process each creative
    results = []
    temp_files = []

    for creative_path in args.input:
        path = Path(creative_path)
        if not path.exists():
            results.append({"file": str(path), "error": "File not found"})
            continue

        print(f"Scoring: {path.name}...", file=sys.stderr)

        # Convert image to video if needed
        stimulus_path = str(path)
        if path.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp'):
            tmp = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_files.append(tmp.name)
            stimulus_path = image_to_video(str(path), tmp.name)

        try:
            # Run Tribe v2 inference
            df = model.get_events_dataframe(video_path=stimulus_path)
            preds, segments = model.predict(events=df)

            # Average activation across time
            avg_activation = np.mean(preds, axis=0)

            # Extract ROI scores
            roi_scores = extract_roi_scores(avg_activation)

            results.append({
                "file": str(path),
                "roi_scores": roi_scores,
                "prediction_shape": list(preds.shape),
            })
        except Exception as e:
            results.append({"file": str(path), "error": str(e)})

    # Normalize across batch
    valid_results = [r for r in results if 'roi_scores' in r]
    if valid_results:
        raw_scores = [r['roi_scores'] for r in valid_results]
        normalized = normalize_scores(raw_scores)

        for r, normed in zip(valid_results, normalized):
            metrics = map_to_metrics(normed)
            composite = compute_composite(metrics, weights)
            r['scores'] = {k: round(v, 1) for k, v in metrics.items()}
            r['composite'] = round(composite, 1)
            r['verdict'] = get_verdict(composite)

    # Clean up temp files
    for f in temp_files:
        try:
            os.unlink(f)
        except OSError:
            pass

    elapsed = time.time() - start_time

    # Output JSON
    output = {
        "results": results,
        "execution_mode": f"local_{device}" if 'device' in dir() else "local",
        "inference_time_seconds": round(elapsed, 1),
        "calibrated_weights": calibrated,
        "weights_used": {k: round(v, 3) for k, v in weights.items()},
        "creatives_scored": len(valid_results),
        "creatives_failed": len(results) - len(valid_results),
    }

    output_json = json.dumps(output, indent=2)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_json)
        print(f"Results saved to {args.output}", file=sys.stderr)

    print(output_json)


if __name__ == '__main__':
    main()
