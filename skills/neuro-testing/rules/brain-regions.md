# Brain Region Parcellation for Marketing ROI Extraction

## fsaverage5 Cortical Surface

Tribe v2 outputs predictions on the FreeSurfer `fsaverage5` mesh — approximately 20,484 vertices covering the cortical surface of both hemispheres. Each vertex represents a predicted BOLD (blood-oxygen-level-dependent) activation value.

To extract marketing-relevant scores, we map vertex ranges to brain regions using the Desikan-Killiany atlas parcellation adapted to fsaverage5.

## Region-of-Interest Vertex Mappings

These are approximate vertex ranges for the left hemisphere. Right hemisphere vertices are offset by ~10,242 (half of fsaverage5). When extracting scores, average BOTH hemispheres for a bilateral measure.

### Visual Processing (Attention)

| Region | Approximate Vertices (LH) | Function |
|--------|--------------------------|----------|
| V1 (primary visual) | 0-800 | Low-level visual features: edges, contrast, color |
| V2/V3 | 800-1800 | Mid-level: texture, shape, depth |
| V4 | 1800-2500 | Higher visual: color constancy, object parts |
| Lateral occipital | 2500-3500 | Object recognition, scene understanding |

**Marketing relevance**: High activation = the creative is visually striking. Low activation = it blends into the feed. For scroll-stopping ads, you want V1-V4 activation > 60th percentile.

### Face Processing (Human Connection)

| Region | Approximate Vertices (LH) | Function |
|--------|--------------------------|----------|
| Fusiform face area | 5000-5500 | Face detection and recognition |
| Superior temporal sulcus | 5500-6000 | Social perception, gaze direction, facial expression |

**Marketing relevance**: High activation = strong human element in the creative. Faces consistently outperform faceless ads in engagement metrics. If fusiform activation is low, consider adding a human face or eye contact.

### Emotional Processing

| Region | Approximate Vertices (LH) | Function |
|--------|--------------------------|----------|
| Amygdala-adjacent cortex | 8000-8300 | Emotional salience, threat/reward detection |
| Insula | 7500-8000 | Emotional awareness, empathy, disgust |
| Anterior cingulate | 12000-12500 | Emotional regulation, conflict monitoring |

**Marketing relevance**: High activation = the creative triggers an emotional response (positive or negative). Emotional ads are shared 2x more than rational ads. For viral potential, you want amygdala-region activation > 65th percentile.

**Note**: The amygdala is a subcortical structure. The fsaverage5 surface model captures amygdala-adjacent cortical activation, which correlates with but doesn't directly measure amygdala activity. Interpret as an approximation.

### Memory Encoding

| Region | Approximate Vertices (LH) | Function |
|--------|--------------------------|----------|
| Hippocampus-adjacent cortex | 8300-8700 | Memory formation, spatial navigation |
| Parahippocampal gyrus | 8700-9200 | Scene processing, contextual memory |
| Entorhinal cortex | 9200-9500 | Memory gateway, pattern separation |

**Marketing relevance**: High activation = the content is being encoded into memory. Brand recall correlates with parahippocampal and hippocampal activity. A creative that scores high here will be remembered tomorrow; one that scores low is forgotten in seconds.

### Language Comprehension

| Region | Approximate Vertices (LH) | Function |
|--------|--------------------------|----------|
| Wernicke's area (STG) | 6000-6500 | Speech comprehension, word meaning |
| Angular gyrus | 6500-7000 | Semantic integration, reading |
| Inferior frontal (Broca's) | 13000-13500 | Language production, syntax processing |

**Marketing relevance**: High activation = the copy/message is being processed and understood. If comprehension scores are low with text-heavy creatives, the copy is too complex or the visual hierarchy is poor. Simplify the message.

### Decision and Action

| Region | Approximate Vertices (LH) | Function |
|--------|--------------------------|----------|
| Dorsolateral prefrontal | 14000-15500 | Working memory, planning, decision-making |
| Ventromedial prefrontal | 15500-16500 | Value assessment, preference formation |
| Orbitofrontal | 16500-17000 | Reward evaluation, cost-benefit analysis |

**Marketing relevance**: This is the conversion zone. High prefrontal activation = the viewer is actively considering the offer, weighing value, and deciding whether to act. Strong decision-engagement is the #1 predictor of CTA clicks.

### Reward Processing

| Region | Approximate Vertices (LH) | Function |
|--------|--------------------------|----------|
| Ventral striatum-adjacent | 9000-9300 | Reward anticipation, motivation |
| Nucleus accumbens-adjacent | 9300-9500 | Pleasure, positive reinforcement |

**Marketing relevance**: High activation = the creative activates reward circuitry. The viewer perceives the offer as genuinely valuable. Low reward activation with a strong CTA = the offer doesn't feel worth it (pricing perception issue).

**Note**: Like amygdala, striatum is subcortical. Surface model captures adjacent cortical spillover. Lower confidence than cortical ROIs.

## Extraction Code Pattern

```python
import numpy as np

# Define bilateral ROI vertices
def get_bilateral_vertices(lh_range, n_vertices_per_hemi=10242):
    lh = list(lh_range)
    rh = [v + n_vertices_per_hemi for v in lh_range]
    return lh + rh

ROI_VERTICES = {
    'visual_cortex': get_bilateral_vertices(range(0, 3500)),
    'fusiform_face': get_bilateral_vertices(range(5000, 5500)),
    'amygdala_region': get_bilateral_vertices(range(8000, 8300)),
    'hippocampus': get_bilateral_vertices(range(8300, 9200)),
    'wernicke': get_bilateral_vertices(range(6000, 7000)),
    'prefrontal': get_bilateral_vertices(range(14000, 17000)),
    'striatum_region': get_bilateral_vertices(range(9000, 9500)),
}

def extract_roi_scores(avg_activation):
    """Extract mean activation for each ROI from a vertex array."""
    scores = {}
    n_vertices = len(avg_activation)
    for region, vertices in ROI_VERTICES.items():
        valid = [v for v in vertices if v < n_vertices]
        if valid:
            scores[region] = float(np.mean(avg_activation[valid]))
    return scores
```

## Normalization

Raw activation values are arbitrary-scaled BOLD signal predictions. To get comparable 0-100 scores:

```python
def normalize_scores(all_creative_scores):
    """Min-max normalize across a set of creatives."""
    all_values = {}
    for region in ROI_VERTICES:
        vals = [s[region] for s in all_creative_scores if region in s]
        if vals:
            min_v, max_v = min(vals), max(vals)
            all_values[region] = (min_v, max_v)
    
    normalized = []
    for scores in all_creative_scores:
        normed = {}
        for region, val in scores.items():
            min_v, max_v = all_values[region]
            if max_v > min_v:
                normed[region] = ((val - min_v) / (max_v - min_v)) * 100
            else:
                normed[region] = 50  # No differentiation
        normalized.append(normed)
    return normalized
```

**Important**: Normalization is relative to the set being tested. A score of 90 means "best in this batch," not "objectively great." Always test 3+ creatives together for meaningful comparison.
