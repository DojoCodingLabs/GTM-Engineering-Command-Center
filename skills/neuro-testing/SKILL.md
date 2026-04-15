---
name: neuro-testing
description: Neural pre-testing with Meta Tribe v2 — brain response prediction for ad creatives, scoring algorithm, ROI mapping, and interpretation guide
---

# Neural Pre-Testing with Tribe v2

Pre-test ad creatives, landing pages, email templates, and video ads using Meta's open-source brain prediction model. Predict which creative generates the strongest attention, emotional response, and memory activation BEFORE spending a dollar on deployment.

## What Is Tribe v2?

Tribe v2 is Meta FAIR's open-source predictive foundation model that predicts human brain responses (fMRI activation) to visual, auditory, and linguistic stimuli. Trained on 700+ subjects and 1,100+ hours of fMRI data, it produces high-resolution predictions (~20K cortical vertices) with zero-shot generalization to new content.

- **Repo**: github.com/facebookresearch/tribev2
- **Weights**: HuggingFace `facebook/tribev2`
- **License**: CC-BY-NC-4.0 (non-commercial)
- **Inputs**: Video, audio, text (images converted to 3-sec video)
- **Outputs**: Predicted fMRI activation map (n_timesteps × ~20K vertices)

## Brain Region → Marketing Metric Mapping

| Brain Region | Cortical Area | Marketing Metric | Significance |
|-------------|---------------|-----------------|-------------|
| Visual cortex (V1-V4) | Occipital lobe | **Attention** | Does the creative stop the scroll? |
| Fusiform face area | Temporal lobe | **Face Response** | Does it leverage human connection? |
| Amygdala region | Medial temporal | **Emotional Intensity** | Will it trigger sharing/action? |
| Hippocampus region | Medial temporal | **Memory Encoding** | Will they remember the brand? |
| Wernicke's area | Superior temporal | **Comprehension** | Is the message understood? |
| Prefrontal cortex | Frontal lobe | **Decision Engagement** | Are they considering action? |
| Ventral striatum | Subcortical | **Reward Response** | Does it feel valuable? |

## Composite Scoring Formula

```
composite = (
    attention      × 0.25 +   # Must see it first
    emotion        × 0.20 +   # Must feel something
    memory         × 0.20 +   # Must remember the brand
    decision       × 0.20 +   # Must consider action
    comprehension  × 0.10 +   # Must understand the offer
    reward         × 0.05     # Must feel it's valuable
)
```

Weights are default starting values. After campaigns, `/gtm-learn` correlates neural scores with actual CPA/CTR and saves calibrated weights to `.gtm/learnings/neuro-calibration.md`.

## Decision Matrix

| Composite | Verdict | Action |
|-----------|---------|--------|
| 70-100 | **DEPLOY** | Full budget. High confidence this creative performs. |
| 55-69 | **TEST** | Reduced budget (20%). Include as B-variant to validate. |
| 40-54 | **ITERATE** | Don't deploy yet. Fix weak dimensions, re-score. |
| 0-39 | **SKIP** | Kill it. Fundamental creative problems. |

## Execution Modes

### Mode A: Local Python (preferred)
- Requires: Python 3.11+, tribev2 package, CUDA GPU recommended
- Speed: ~10-30 seconds per creative (GPU) or ~2-5 minutes (CPU)
- Setup: `bash scripts/neuro-setup.sh` or `pip install tribev2`

### Mode B: Google Colab (no local GPU)
- Upload creatives, run inference notebook, copy results back
- Speed: ~1-2 minutes per creative (free Colab GPU)

### Mode C: Meta AI Demo (quick preview)
- URL: aidemos.atmeta.com/tribev2
- Upload via Playwright/Computer Use, screenshot brain heatmap
- Qualitative only — no numerical scores

## Limitations

1. **CC-BY-NC license** — Non-commercial use only. Fine for internal testing, cannot be sold as SaaS.
2. **Group-average predictions** — Predicts average response across 700+ subjects, not individual reactions. Good for general audience, less useful for niche micro-segments.
3. **GPU recommended** — CPU inference works but is 10x slower. Colab provides free GPU fallback.
4. **Not a replacement for A/B testing** — Use as pre-filter to reduce waste (deploy top 2 instead of all 5), not as sole decision maker.
5. **Image-to-video conversion** — Static images need conversion to 3-second video clips. Adds a processing step.
6. **Subcortical resolution** — fMRI surface model has limited resolution for deep brain structures (amygdala, striatum). Scores for these regions are approximations.

## Integration Points

- `/gtm-neurotest` — Standalone command to score any creative
- `/gtm-create` Phase 5.5 — Auto-scores after creative generation
- `/gtm` Phase 4.5 — Neural pre-test between Create and Deploy
- `/gtm-learn` — Calibrates scoring weights from actual campaign data
- `agents/creative-director.md` — Uses neuro feedback to iterate on weak creatives

## Rules

- `rules/brain-regions.md` — Cortical parcellation and vertex mappings
- `rules/score-interpretation.md` — How to read scores, iterate on weak dimensions
- `rules/setup-guide.md` — Installation, configuration, troubleshooting
