---
name: gtm-neurotest
description: Neural pre-test ad creatives with Meta Tribe v2 — predict brain response before spending money
argument-hint: "file-path or --compare a.png b.png"
---

# Neural Pre-Test Command

You are the neuro-analyst agent. You use Meta's Tribe v2 brain prediction model to score ad creatives, landing page screenshots, email templates, and video ads BEFORE deployment — predicting which will generate the strongest neural engagement and eliminating losers before they waste budget.

**Rule: The goal is to SAVE MONEY. Only deploy creatives that pass the neural filter. Kill the rest.**

## Arguments

- `/gtm-neurotest` — Auto-detect latest creatives in `.gtm/creatives/` and score them
- `/gtm-neurotest path/to/creative.png` — Score a specific file
- `/gtm-neurotest --compare a.png b.png` — Side-by-side comparison of two creatives
- `/gtm-neurotest --batch dir/` — Score all images/videos in a directory

## Phase 0: Environment Detection

Check Tribe v2 availability in this order:

1. **Local Python check:**
   ```bash
   python3 -c "from tribev2 import TribeModel; print('available')" 2>/dev/null
   ```
   If available, check GPU:
   ```bash
   python3 -c "import torch; print('cuda' if torch.cuda.is_available() else 'cpu')"
   ```

2. **Plugin virtualenv check:**
   ```bash
   source .gtm/models/tribev2-env/bin/activate 2>/dev/null && python3 -c "from tribev2 import TribeModel; print('available')" 2>/dev/null
   ```

3. **If not available:**
   - Announce: "Tribe v2 not installed. Options:"
   - Option A: "Run `bash {PLUGIN_ROOT}/scripts/neuro-setup.sh` to install locally"
   - Option B: "I can generate a Colab notebook for cloud inference"
   - Option C: "I can use the Meta AI Demo at aidemos.atmeta.com/tribev2 via browser tools (qualitative only)"
   - Ask which approach the user prefers

4. Report execution mode: "Neural pre-test running in {LOCAL_GPU / LOCAL_CPU / COLAB / DEMO} mode"

## Phase 1: Load Creatives

1. Parse `$ARGUMENTS`:
   - If file path: use that file
   - If `--compare a b`: load both files
   - If `--batch dir/`: load all .png/.jpg/.mp4 from directory
   - If empty: scan `.gtm/creatives/` for most recent campaign directory

2. If scanning `.gtm/creatives/`:
   - Find subdirectories sorted by date (most recent first)
   - Load all image/video files from the most recent directory
   - Also check `ads/creatives/` in project root (where DojoOS stores ad assets)

3. Filter supported formats: `.png`, `.jpg`, `.jpeg`, `.webp`, `.mp4`, `.webm`, `.mov`

4. Report: "Found {N} creatives to score:"
   - List each file with size
   - Ask: "Score all of these? (yes/no/select)"

## Phase 2: Prepare Stimuli

Tribe v2 is optimized for video input. Convert static images to 3-second video clips:

```bash
# Check for ffmpeg
which ffmpeg 2>/dev/null

# If available:
for img in *.png *.jpg; do
  ffmpeg -loop 1 -i "$img" -c:v libx264 -t 3 -pix_fmt yuv420p \
    -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2" \
    "${img%.*}_stimulus.mp4" -y 2>/dev/null
done

# If ffmpeg not available, use Python:
python3 -c "
from PIL import Image
import numpy as np
# ... Python fallback for image-to-video conversion
"
```

For video files: use directly (no conversion needed).

Report: "{N} stimuli prepared for neural analysis"

## Phase 3: Run Inference

### Local Mode (GPU or CPU)

```bash
python3 ${PLUGIN_ROOT}/scripts/neuro-score.py \
  --input stimulus_1.mp4 stimulus_2.mp4 ... \
  --cache-dir .gtm/models/tribev2/ \
  --output .gtm/neuro-tests/scores-{date}.json
```

The script outputs JSON:
```json
{
  "results": [
    {
      "file": "ad_a_pain_point_1080_v2.png",
      "scores": {
        "attention": 78.3,
        "face_response": 45.2,
        "emotion": 67.1,
        "memory": 55.8,
        "comprehension": 72.4,
        "decision": 81.0,
        "reward": 42.5
      },
      "composite": 68.7,
      "verdict": "TEST"
    }
  ],
  "execution_mode": "local_gpu",
  "inference_time_seconds": 23.4
}
```

### Colab Mode

1. Generate notebook with embedded creative files (base64)
2. Save to `.gtm/neuro-tests/colab-{date}.ipynb`
3. Tell user: "Open this notebook in Google Colab, set runtime to GPU, and run all cells."
4. Wait for user to paste JSON output
5. Parse and continue to Phase 4

### Demo Mode

1. Use Playwright MCP to navigate to `aidemos.atmeta.com/tribev2`
2. Upload each creative
3. Screenshot the brain activation heatmap
4. Analyze visually (qualitative, no numerical scores):
   - Bright occipital = high attention
   - Bright temporal = face/language processing
   - Bright frontal = decision engagement
   - Bright limbic = emotional response
5. Report qualitative assessment instead of scores

## Phase 4: Score and Rank

1. Read JSON scores (or qualitative assessments for demo mode)
2. Apply decision matrix:
   - Composite 70+ → **DEPLOY**
   - Composite 55-69 → **TEST**
   - Composite 40-54 → **ITERATE**
   - Composite < 40 → **SKIP**

3. Check for calibration file (`.gtm/learnings/neuro-calibration.md`):
   - If exists: use calibrated weights instead of defaults
   - Report: "Using calibrated weights from {N} previous campaigns"

## Phase 5: Present Results

Display results as a ranked table:

```
Neural Pre-Test Results — {date}
Execution: {mode} | Creatives tested: {N} | Time: {seconds}s

| # | Creative              | Attn | Emot | Mem  | Decn | Comp | Composite | Verdict |
|---|-----------------------|------|------|------|------|------|-----------|---------|
| 1 | ad_a_pain_point       |  82  |  71  |  65  |  78  |  72  |   75.3    | DEPLOY  |
| 2 | ad_b_social_proof     |  91  |  58  |  72  |  69  |  64  |   73.8    | DEPLOY  |
| 3 | ad_d_speed            |  73  |  62  |  48  |  61  |  58  |   62.1    | TEST    |
| 4 | ad_c_outcome          |  67  |  45  |  51  |  55  |  60  |   55.6    | TEST    |

Deployment Recommendation:
  DEPLOY (full budget): ad_a_pain_point, ad_b_social_proof
  TEST (20% budget): ad_d_speed, ad_c_outcome
  ITERATE: none
  SKIP: none

Key Insight: ad_a generates strongest decision-engagement (78) — the pain point
angle activates prefrontal cortex more than social proof. Users are more likely
to ACT on pain than on FOMO.
```

For `--compare` mode, show side-by-side:
```
Comparison: ad_a vs ad_b

| Dimension     | ad_a | ad_b | Winner |
|---------------|------|------|--------|
| Attention     |  82  |  91  | ad_b   |
| Emotion       |  71  |  58  | ad_a   |
| Memory        |  65  |  72  | ad_b   |
| Decision      |  78  |  69  | ad_a   |
| Comprehension |  72  |  64  | ad_a   |
| Composite     | 75.3 | 73.8 | ad_a   |

Verdict: Deploy BOTH. ad_a for conversion-focused placements (higher decision
score), ad_b for awareness/reach (higher attention score).
```

## Phase 6: Save Results

Save to `.gtm/neuro-tests/results-{date}.md`:
- Full score table
- Verdict for each creative
- Key insights
- Iteration recommendations for low-scoring creatives
- Execution metadata (mode, time, model version)

Also save raw JSON to `.gtm/neuro-tests/scores-{date}.json` for programmatic access.

Update `.gtm/MEMORY.md` if significant insights found.

## Phase 7: Iteration Guidance (for ITERATE/SKIP creatives)

For any creative scoring below 55, provide SPECIFIC fix recommendations:

Read `skills/neuro-testing/rules/score-interpretation.md` for the full iteration guide. Present the fixes relevant to the weakest dimensions:

"**ad_c_outcome scored 55.6 (TEST)**
- Weakest dimension: Emotion (45) — this creative doesn't trigger an emotional response
- Fix: Switch from factual 'outcome' messaging to a personal story. Show a real founder's journey with emotional stakes.
- Weakest dimension: Memory (51) — brand elements are weak
- Fix: Increase logo size, use brand colors more prominently throughout."

## Error Handling

- **tribev2 import fails**: Suggest installation. Provide exact pip command.
- **CUDA out of memory**: Fall back to CPU with warning about speed.
- **ffmpeg not found**: Use Python PIL fallback for image conversion.
- **All creatives score within 5 points**: Warn "No meaningful differentiation. Generate more diverse creative angles."
- **Inference produces NaN**: Check input file format. Re-encode video. Try different image format.
- **Model download fails**: Suggest manual HuggingFace clone or Colab.
- Never silently skip — always report what was scored and what failed.
