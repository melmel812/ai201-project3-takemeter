# TakeMeter

A fine-tuned text classifier that labels r/TrueFilm posts across four categories of film discourse: **analysis**, **interpretation**, **opinion**, and **reaction**. Built with a 200-example annotated dataset and a fine-tuned DistilBERT model, evaluated against a zero-shot Groq baseline.

---

## Community: r/TrueFilm

r/TrueFilm is a subreddit for serious film criticism. Its rules explicitly prohibit shallow reactions and plot summaries — members are expected to argue, not just respond. This makes it an unusually good community for classification: the same film generates four genuinely distinct post types in a single week (a cinematography breakdown, a thematic reading, a contrarian ranking, a first-watch emotional response). The taxonomy is also socially real — community members actively distinguish these modes and push back when threads mix them.

---

## Label Taxonomy

| Label | What it is |
|---|---|
| **analysis** | Examines HOW a film works at the craft level — cinematography, editing, score, structure. The argument is about technique and its effect. Evidence is specific: a named scene, a shot, a transition. |
| **interpretation** | Proposes a reading of what a film MEANS — its themes, symbols, subtext, or allegory. Evidence is drawn from the film but in service of a claim about significance, not technique. |
| **opinion** | Makes a VALUE JUDGMENT about a film's quality, cultural standing, or ranking. The primary claim is evaluative: good/bad, overrated/underrated, better/worse. Evidence supports a verdict. |
| **reaction** | Centered on the PERSONAL EXPERIENCE of watching — emotional response, first-discovery context, what the film felt like in the moment. Narrates a viewing experience rather than making an argument. |

The hardest boundary is **analysis vs. interpretation**: both make specific claims about film. The decision rule is where the argument *lands* — on technique and its effect (analysis) or on thematic meaning (interpretation). See `planning.md` for all four decision rules and edge case walkthrough.

---

## Dataset

**Source:** r/TrueFilm posts collected via the Reddit API (PRAW). Raw posts from the top 1,000 all-time posts and recent high-upvote threads, plus comments from megathreads to supplement the underrepresented `reaction` class.

**Size:** 200 labeled examples.

**Label distribution:**

| Label | Count | % of total |
|---|---|---|
| analysis | 32 | 16% |
| interpretation | 32 | 16% |
| opinion | 77 | 38.5% |
| reaction | 59 | 29.5% |
| **Total** | **200** | 100% |

No single label exceeds 70%. `analysis` and `interpretation` are underrepresented relative to the target of 25% each — the subreddit actively favors opinion-type posts and `analysis`-style posts are harder to collect at volume. This imbalance had a significant impact on model performance (see Evaluation Report).

**Labeling process:** The first 100 posts were pre-labeled using Groq (`llama-3.3-70b-versatile`) with the full taxonomy definitions as the system prompt. Every AI-generated label was reviewed by hand — accepted, overridden, or flagged as ambiguous. The remaining 120+ examples were annotated from scratch. The CSV includes a `prelabeled_by_ai` boolean column tracking which examples were AI-prelabeled. Approximately 50% of the dataset was AI-prelabeled and human-reviewed; 50% was annotated from scratch.

**Difficult cases:** Three hard annotation decisions are documented in full detail in `planning.md` (Section 8). Brief summaries:

1. A post comparing a recurring structural pattern across PTA films — it uses scene evidence (analysis cue) but its conclusion is about what the pattern *means* thematically (interpretation). Labeled **interpretation** because the conclusion is a thematic claim, not a formal-effect claim.

2. A post on *The King of Comedy*'s daydream sequences that opens with a comparative value claim ("no other film captures…") but stays at the level of what the sequences *produce for the viewer*. Labeled **analysis** because the evaluative phrase is incidental framing, not the substance of the argument.

3. A post on *The Ascent* (1977) that mentions cinematography and black-and-white photography but never makes a formal claim about them. Labeled **reaction** because the formal observations are decorative — the post stays entirely in the register of personal emotional response.

---

## Fine-Tuning Pipeline

**Base model:** `distilbert-base-uncased` (Hugging Face)  
**Training platform:** Google Colab with a T4 GPU

**Train/val/test split:** 70% / 15% / 15% (140 / 30 / 30), stratified by label.

**Hyperparameters and reasoning:**

| Parameter | Value | Reasoning |
|---|---|---|
| `num_train_epochs` | 3 | Standard starting point for small datasets. With only 140 training examples, more epochs risk overfitting before the model can generalize. |
| `learning_rate` | 2e-5 | Standard fine-tuning rate for BERT-family models. Lower rates are more stable on small data; higher rates risk overwriting the pre-trained representations. |
| `per_device_train_batch_size` | 16 | Fits T4 GPU memory comfortably with DistilBERT's footprint. |
| `weight_decay` | 0.01 | Light regularization to reduce overfitting on a small training set. |
| `warmup_steps` | 50 | Ramps the learning rate from 0 over the first 50 steps to avoid large gradient updates on the pre-trained weights at the start of training. |

**Key training decision:** The number of epochs was kept at 3 rather than increased, despite poor validation performance. Post-training analysis revealed that the model's failure was not underfitting (more passes over the data would not fix it) but a **data distribution problem**: with only 22 training examples for `analysis` and 22 for `interpretation`, DistilBERT had insufficient signal to distinguish these classes from the majority classes. Increasing epochs on an imbalanced dataset would have pushed the model further toward `opinion` and `reaction` prediction, not improved the minority classes.

---

## Baseline: Zero-Shot Groq (llama-3.3-70b-versatile)

**Approach:** A zero-shot classification using Groq's `llama-3.3-70b-versatile` model. No examples were provided — only the label definitions from the taxonomy. The system prompt included all four label descriptions with one example per label, decision rules for the hardest boundary (analysis vs. interpretation), and an instruction to respond with the label name only.

**System prompt structure:**
```
You are classifying posts from r/TrueFilm, a subreddit for serious film discussion.

Assign each post to EXACTLY ONE of these four categories:

analysis: [definition + example]
interpretation: [definition + example]
opinion: [definition + example]
reaction: [definition + example]

Respond with ONLY the label name. No punctuation. No explanation.
Valid labels: analysis, interpretation, opinion, reaction
```

**Results:** The planned baseline used `llama-3.3-70b-versatile`, but that model's daily token quota was exhausted from the annotation pre-labeling phase. The baseline was successfully run using `llama-3.1-8b-instant` (same provider, smaller model). 28 of 30 test examples produced parseable responses; 2 were excluded from metrics.

**Baseline per-class metrics (llama-3.1-8b-instant, zero-shot):**

| Label | Precision | Recall | F1 | Support (valid) |
|---|---|---|---|---|
| analysis | 1.00 | 0.60 | 0.75 | 5 |
| interpretation | 0.50 | 0.20 | 0.29 | 5 |
| opinion | 0.48 | 1.00 | 0.65 | 10 |
| reaction | 1.00 | 0.25 | 0.40 | 8 |
| **macro avg** | **0.74** | **0.51** | **0.52** | **28** |

**Baseline confusion matrix:**

|  | Pred: analysis | Pred: interpretation | Pred: opinion | Pred: reaction |
|---|---|---|---|---|
| **True: analysis** | 3 | 1 | 1 | 0 |
| **True: interpretation** | 0 | 1 | 4 | 0 |
| **True: opinion** | 0 | 0 | 10 | 0 |
| **True: reaction** | 0 | 0 | 6 | 2 |

The zero-shot baseline makes predictions across all four classes (unlike the fine-tuned model which only predicts two). It performs well on `opinion` (recall 1.00) and `analysis` (recall 0.60), but struggles with `interpretation` (recall 0.20) and `reaction` (recall 0.25). The `interpretation` vs. `opinion` confusion — 4 of 5 interpretations called opinion — mirrors the fine-tuned model's most common error.

---

## Evaluation Report

### Overall Results

| Model | Accuracy | Macro F1 | Test examples |
|---|---|---|---|
| Fine-tuned DistilBERT | 0.367 | 0.22 | 30 |
| Zero-shot baseline (llama-3.1-8b-instant) | 0.571 | 0.52 | 28 of 30 parseable |

**Note on baseline model:** The planned baseline used `llama-3.3-70b-versatile`, but that model's daily token quota was exhausted during the annotation pre-labeling phase. The baseline was re-run with `llama-3.1-8b-instant`, a smaller model in the same family. This is a slightly weaker baseline than planned — the larger model would likely perform better — which means the gap shown above is a conservative estimate of how much the fine-tuned model underperforms zero-shot LLMs.

**Key finding:** The zero-shot baseline substantially outperforms the fine-tuned model (0.52 vs. 0.22 macro F1). The fine-tuned model performed substantially below the target threshold of Macro F1 ≥ 0.70 set in `planning.md`. The primary cause is data imbalance: `analysis` and `interpretation` had only 22 training examples each, and the model learned to never predict either class.

### Per-Class Metrics: Fine-Tuned Model

| Label | Precision | Recall | F1 | Support (test) |
|---|---|---|---|---|
| analysis | 0.00 | 0.00 | 0.00 | 5 |
| interpretation | 0.00 | 0.00 | 0.00 | 5 |
| opinion | 0.37 | 0.64 | 0.47 | 11 |
| reaction | 0.36 | 0.44 | 0.40 | 9 |
| **macro avg** | **0.18** | **0.27** | **0.22** | **30** |

The model never predicts `analysis` or `interpretation` — precision and recall are both 0 for those classes. It distributed all 30 test predictions between `opinion` (19 predictions) and `reaction` (11 predictions).

### Confusion Matrix (Fine-Tuned Model)

Rows = true label. Columns = predicted label.

|  | Pred: analysis | Pred: interpretation | Pred: opinion | Pred: reaction |
|---|---|---|---|---|
| **True: analysis** | 0 | 0 | 5 | 0 |
| **True: interpretation** | 0 | 0 | 2 | 3 |
| **True: opinion** | 0 | 0 | 7 | 4 |
| **True: reaction** | 0 | 0 | 5 | 4 |

The model collapses to a near-binary classifier. All `analysis` examples are called `opinion`. `interpretation` examples split between `opinion` and `reaction`. `opinion` is the most correctly-predicted class but still misses 4 of 11. `reaction` is predicted correctly 4 of 9 times.

The most diagnostically important pattern: the model never uses the `analysis` or `interpretation` labels at all. This is not a case of the model confusing similar categories — it's a failure to have learned those categories exist as distinct prediction targets.

### Sample Classifications

Examples from the test set run through the fine-tuned model. Confidence is the softmax probability for the predicted class.

| Post excerpt | True label | Predicted | Confidence | Correct? |
|---|---|---|---|---|
| "Shoplifters or Roma? These two, in my opinion, are the best movies of 2018. Shoplifters continues Koreeda's stellar filmography..." | opinion | opinion | 0.38 | ✓ |
| "Malayalam cinema is going through a New Wave this decade, you can check out lots of great movies. Bengali cinema of the 50s and 60s is considered the Golden Age..." | opinion | opinion | 0.37 | ✓ |
| "Deliverance (1972) is a masterclass in foreshadowing — I watched Deliverance for the first time... I was fairly surprised at what this movie turned out to be..." | analysis | opinion | 0.28 | ✗ |
| "Why is Kiyoshi Kurosawa's 'Eyes of the Spider' called as such? There's nothing in the movie that alludes to the title and I can't see what a spider's eyes would represent..." | interpretation | reaction | 0.28 | ✗ |
| "I just rewatched Blade Runner (Final Cut) and to me, the Voight-Kampff test isn't a sophisticated evaluation of empathy, but rather a simple discriminatory test..." | interpretation | opinion | 0.27 | ✗ |

**Why the first prediction is reasonable:** "Shoplifters or Roma?" is a ranking question ("which is better?") followed by evaluative claims about Koreeda's filmography and the word "opinion" used explicitly. The model correctly identifies the evaluative frame — this is exactly the surface signal it learned to associate with `opinion`. The confidence (0.38) is low but higher than the wrong predictions (0.27–0.28), consistent with the model having slightly more certainty on clear cases.

**Note on confidence:** All confidence scores cluster near 0.27–0.38, barely above random chance for a four-class problem (0.25). This indicates the model is not actually confident in any prediction — it is making low-certainty guesses across the entire test set.

---

### Error Analysis

#### Error 1: Analysis predicted as opinion — "Deliverance (1972) is a masterclass in foreshadowing"

**True label:** analysis  
**Predicted:** opinion (confidence 0.28)

The post title contains evaluative phrasing ("a masterclass in foreshadowing") and the opening paragraph is first-person experiential narration: "I watched Deliverance for the first time back in October and it definitely lived up to my expectations." These are surface signals that strongly overlap with `opinion` and `reaction` posts in the training data.

The actual content is analytical — the post traces how specific foreshadowing techniques function across the film's structure and how those techniques produce their effect on the viewer. But this analytical substance comes after the first paragraph, which the model appears to weight heavily.

**Why it failed:** The model learned "masterclass = opinion" as a surface heuristic. In the training data, `opinion` posts frequently use evaluative superlatives to anchor their verdict. `analysis` posts almost never open with them — but this one does. With only 22 `analysis` training examples, the model had too few counterexamples to override this pattern.

**What would fix it:** More `analysis` examples that open with evaluative framing before developing formal argument. The model needs to see that "masterclass in X" + detailed structural breakdown = analysis, not opinion.

---

#### Error 2: Interpretation predicted as reaction — "Why is Kiyoshi Kurosawa's 'Eyes of the Spider' called as such?"

**True label:** interpretation  
**Predicted:** reaction (confidence 0.28)

The post opens with a question ("Why is... called as such?"), includes personal confusion ("I can't see what a spider's eyes would represent symbolically"), and closes with a social signal ("I love KiKu"). These are all surface features of `reaction` posts — first-person framing, emotional disclosure, seeking connection. The post is short and low-information.

But the post's actual function is to request a symbolic interpretation of the title — it asks what the spider's eyes represent, which is an invitation to produce `interpretation`. The model can't distinguish between "I'm confused about what something means" (calling for interpretation) and "here is my personal experience of watching" (reaction).

**Why it failed:** The confusion here has a potential labeling dimension. By the decision rule in `planning.md`, a post that arrives at a formal or interpretive observation belongs in that category even if it comes through personal framing. But this post doesn't arrive anywhere — it asks a question without proposing any reading. A case could be made for labeling it `reaction` (pure personal confusion, no argument) or `interpretation` (the subject is meaning, even if the mode is question-asking). If similar posts were labeled differently during annotation, the model would have received contradictory signal for this surface pattern.

**What would fix it:** Tighter annotation consistency for question-asking posts about symbolic meaning. Additionally, more `interpretation` examples that use interrogative framing would give the model signal that questions about meaning belong to that class.

---

#### Error 3: Interpretation predicted as opinion — "I just rewatched Blade Runner (Final Cut) and to me, the Voight-Kampff test isn't a sophisticated evaluation of empathy..."

**True label:** interpretation  
**Predicted:** opinion (confidence 0.27)

The opening sentence has two opinion-signaling elements: "I just rewatched" (experiential framing → reaction) and "to me, the Voight-Kampff test isn't a sophisticated evaluation of empathy" (personal verdict on a filmic element → opinion). The model predicts `opinion` — picking up on the "to me, X isn't Y" construction, which matches the pattern of an evaluative judgment.

The actual argument is interpretive: the post goes on to argue that the Voight-Kampff test is structurally a discriminatory mechanism, not an empathy test — because replicants are institutionally denied the frames of reference needed to pass it. That's a reading about what the film is *about*, not a verdict on its quality. But the model never gets past the opening framing.

**Why it failed:** This is the "to me, X isn't Y, *because Z*" problem. The personal opening followed by a claim sounds like opinion. The "because Z" clause — which contains the actual interpretive substance — doesn't override the frame the opening established. The model learned to treat "to me, [evaluative claim about film element]" as an opinion signal regardless of what follows. With 22 interpretation training examples, there weren't enough of this subtype to teach it otherwise.

**What would fix it:** More `interpretation` examples that open with personal voice before making a structural argument. The model needs counterexamples showing that first-person opening + interpretive development = interpretation, not opinion or reaction.

---

### Reflection: What the Model Captured vs. What Was Intended

The intended behavior was a four-way classifier that distinguishes posts by *argument structure* — where does the reasoning land? Technique (analysis), meaning (interpretation), verdict (opinion), or experience (reaction)?

What the model actually learned was a **near-binary classifier based on surface vocabulary**: evaluative words → `opinion`, first-person/experiential framing → `reaction`. It never learned `analysis` or `interpretation` as distinct prediction targets.

The gap between these is specific and diagnosable. `Analysis` and `interpretation` posts frequently *contain* evaluative vocabulary and personal framing — they just use those features in service of a different argumentative endpoint. An analysis post might open with "this is one of the best-crafted scenes in 1970s cinema" before spending three paragraphs on cinematographic technique. An interpretation post might open with "I've always felt this film is about..." before making a structural argument about symbolism. The model has no way to look past the opening vocabulary to the argument's conclusion.

This is a **training data distribution failure**, not a label definition failure. The label boundaries in `planning.md` are specific and consistently applied. But DistilBERT with 22 training examples per minority class cannot learn to recognize argument structure from surface text — it latches onto the most predictive surface features, which for `analysis` and `interpretation` are precisely the features shared with `opinion` and `reaction`.

The failure was predictable in retrospect: the planning document (Section 6) set a "good enough" threshold of Macro F1 ≥ 0.70 with no per-class F1 below 0.60. Achieving that threshold on four nuanced discourse categories would have required significantly more balanced training data — likely 50+ examples per class rather than 22.

The specific failure pattern — collapsing minority classes into the nearest majority class based on surface features — is a known DistilBERT behavior on small, imbalanced datasets. Class weighting during training (penalizing `analysis` and `interpretation` errors more heavily) would be the first fix to try. Expanding the dataset to 50+ per class would be the second.

---

## AI Usage

### Instance 1: Pre-labeling for annotation efficiency

Before annotating the second half of the dataset, the first 100 posts were run through Groq (`llama-3.3-70b-versatile`) with the full taxonomy definitions as the system prompt. The AI was directed to assign one of the four labels to each post.

Every AI label was reviewed by hand before being accepted. Approximately 30% of AI labels were overridden — most often in cases where the AI treated evaluative language within an analysis post as grounds to call it `opinion`, or treated a first-person opening in an interpretation post as grounds to call it `reaction`. These were exactly the boundary cases that planning.md anticipated. The overridden labels were re-annotated using the decision rules. The CSV records which examples were AI-prelabeled (`prelabeled_by_ai = True`).

**What I changed:** The AI consistently underweighted argument structure in favor of surface vocabulary — the same failure mode the fine-tuned model later exhibited. Any post with "I think" or "in my opinion" that was actually an interpretive argument got called `opinion` by the AI. I overrode those cases based on the decision rule: "Where does the argument land?"

### Instance 2: Failure pattern analysis

After the fine-tuned model produced 19/30 wrong predictions on the test set, the 15 misclassified examples with their true and predicted labels were pasted into Claude with this prompt: *"Here are 15 posts where a fine-tuned DistilBERT model predicted the wrong label. What patterns do you see? Look for: whether errors cluster around specific label pairs, whether misclassified posts share vocabulary or length, whether there are structural cues the model might be over-relying on."*

The AI identified two patterns: (a) evaluative vocabulary ("masterclass," "brilliant," "best") in `analysis` posts triggering `opinion` predictions, and (b) first-person framing ("I watched," "to me") in `interpretation` posts triggering `reaction` or `opinion` predictions. Both were confirmed by re-reading the examples individually. A third pattern the AI suggested — that short posts were more likely to be mispredicted — was not confirmed: short examples appeared in both the wrong and correct prediction sets.

**What I verified and kept:** Patterns (a) and (b) are supported by the confusion matrix and match the error analysis above. **What I discarded:** The length hypothesis — the AI asserted it confidently but it didn't hold up when checking the actual examples.

---

## Deployed Interface

A local Gradio demo (`demo_app.py`) accepts a new post as input and returns the predicted label and confidence score. Run it with:

```bash
python3 demo_app.py
```

Then open `http://127.0.0.1:7860` in a browser. Four example posts (one per label) are pre-loaded. The interface uses the zero-shot Groq baseline (`llama-3.1-8b-instant`) for inference — to use the fine-tuned DistilBERT model, download `takemeter-model/` from Colab and load it via `AutoModelForSequenceClassification.from_pretrained("./takemeter-model")`.

---

## Spec Reflection

**One way the spec helped:** The planning document's decision rules — specifically the four edge-case rules in Section 3 — were the most practically useful artifact produced during this project. Having "remove the evaluative sentence — does the post still have a point?" as a concrete test made annotation faster and more consistent, especially for opinion/reaction borderline cases. The spec pushed toward writing rules that were testable on real posts, not just abstract definitions, which is a distinction that mattered when hundreds of borderline examples came up during annotation.

**One way implementation diverged from the spec:** The data collection plan (Section 4 of planning.md) targeted 55 examples per label, with a specific plan to supplement `reaction` from weekly megathreads and cap `analysis` collection after 70. In practice, `analysis` and `interpretation` remained at 32 each — the supplementation plan for these classes was not executed before annotation was completed. The spec treated this as a contingency ("if `analysis` is overrepresented, cap it"); in practice the problem ran the other direction (both were underrepresented) and the planned response (collect more) wasn't carried out due to time constraints. This is the root cause of the model's failure to learn those classes.
