"""
run_baseline.py — zero-shot Groq baseline for TakeMeter
Replicates Sections 1, 2, and 5 of the Colab notebook locally.
Outputs: evaluation_results_baseline.json, baseline_confusion_matrix.png
"""

import json, time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, ConfusionMatrixDisplay,
)
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

# ── Label map (must match notebook) ───────────────────────────────────────────
LABEL_MAP = {
    "analysis":       0,
    "interpretation": 1,
    "opinion":        2,
    "reaction":       3,
}
ID_TO_LABEL = {v: k for k, v in LABEL_MAP.items()}

# ── Load and split dataset (same splits as notebook) ──────────────────────────
df = pd.read_csv("dataset.csv", dtype={"label": str})
df["label"] = df["label"].fillna("").str.strip()
df = df[df["label"] != ""].reset_index(drop=True)
df["label_id"] = df["label"].map(LABEL_MAP)
df = df.dropna(subset=["label_id"])
df["label_id"] = df["label_id"].astype(int)

train_df, temp_df = train_test_split(df, test_size=0.30, random_state=42, stratify=df["label_id"])
val_df, test_df   = train_test_split(temp_df, test_size=0.50, random_state=42, stratify=temp_df["label_id"])
test_df = test_df.reset_index(drop=True)

print(f"Train: {len(train_df)}  Val: {len(val_df)}  Test: {len(test_df)}")
print("\nTest label distribution:")
print(test_df["label"].value_counts().to_string())

# ── Groq prompt ───────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are classifying posts from r/TrueFilm, a subreddit for serious film discussion.

Assign each post to EXACTLY ONE of these four categories:

analysis: The post examines HOW a film works at the level of craft — cinematography, editing, score, performance, narrative structure, mise-en-scène. The claim is about formal technique and its effect on the viewer. Evidence is specific (a named scene, a shot, a transition).
Example: "Kubrick's use of one-point perspective in The Shining creates a false sense of order — the Overlook's symmetrical corridors suggest a trap. The vanishing point pulls your eye to Jack in the bathroom scene, then reappears in the maze finale with a fatal misdirection."

interpretation: The post proposes a reading of a film's MEANING — its themes, symbols, subtext, or allegory. The focus is on what the film is about beneath the surface. Evidence is drawn from the film but in service of a claim about significance, not technique.
Example: "The broken clocks in Stalker aren't about time running out — they're about causality being irrelevant inside the Zone. The stopped clock is the film's thesis made physical."

opinion: The post makes a VALUE JUDGMENT about a film's quality, cultural standing, or ranking. The primary claim is evaluative: good/bad, overrated/underrated, better/worse than. Evidence supports a verdict rather than being the substance of the argument.
Example: "Rashomon is overrated as a meditation on subjectivity. Its central thesis — that truth is unknowable — is undercut by the woodcutter's testimony, which the film implicitly treats as reliable. Kurosawa undermines his own premise."

reaction: The post is centered on the PERSONAL EXPERIENCE of watching — emotional response, first-discovery context, what the film felt like in the moment. It narrates a viewing experience rather than making a formal, interpretive, or evaluative argument.
Example: "I watched Yi Yi last night and I'm still processing it. There's a scene near the end I wasn't expecting and I had to pause for several minutes. I don't know how to write about it yet."

Respond with ONLY the label name. No punctuation. No explanation.
Valid labels: analysis, interpretation, opinion, reaction"""


def classify(client, text):
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Classify this post:\n\n{text[:1500]}"},
            ],
            temperature=0,
            max_tokens=20,
        )
        raw = resp.choices[0].message.content.strip().lower()
        for label in sorted(LABEL_MAP, key=len, reverse=True):
            if raw == label or label in raw:
                return label
        return None
    except Exception as e:
        print(f"  API error: {e}")
        return None


# ── Run baseline ──────────────────────────────────────────────────────────────
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
print(f"\nRunning baseline on {len(test_df)} test examples...")

preds, none_count = [], 0
for i, (_, row) in enumerate(test_df.iterrows()):
    pred = classify(client, row["text"])
    preds.append(pred)
    if pred is None:
        none_count += 1
        print(f"  Row {i}: unparseable — leaving blank")
    if (i + 1) % 5 == 0:
        print(f"  {i+1}/{len(test_df)} complete")
    time.sleep(0.15)

if none_count:
    print(f"\n⚠️  {none_count} unparseable responses ({none_count/len(test_df)*100:.1f}%)")

# ── Metrics ───────────────────────────────────────────────────────────────────
valid      = [(p, t) for p, t in zip(preds, test_df["label_id"]) if p is not None]
pred_ids   = [LABEL_MAP[p] for p, _ in valid]
true_ids   = [t for _, t in valid]
label_names = [ID_TO_LABEL[i] for i in range(len(LABEL_MAP))]

accuracy = accuracy_score(true_ids, pred_ids)
print(f"\n{'='*50}")
print(f"BASELINE RESULTS  ({len(valid)}/{len(test_df)} parseable)")
print(f"{'='*50}")
print(f"Accuracy: {accuracy:.3f}")
print()
print(classification_report(true_ids, pred_ids, target_names=label_names, zero_division=0))

# ── Confusion matrix ──────────────────────────────────────────────────────────
cm = confusion_matrix(true_ids, pred_ids)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=label_names)
fig, ax = plt.subplots(figsize=(7, 5))
disp.plot(ax=ax, cmap="Blues", colorbar=False)
ax.set_title("Zero-Shot Baseline (Groq llama-3.3-70b) — Confusion Matrix")
plt.tight_layout()
plt.savefig("baseline_confusion_matrix.png", dpi=150)
print("Saved: baseline_confusion_matrix.png")

# ── Save JSON for evaluation report ──────────────────────────────────────────
from sklearn.metrics import f1_score, precision_score, recall_score
results = {
    "model": "llama-3.3-70b-versatile (zero-shot)",
    "test_set_size": len(test_df),
    "parseable_responses": len(valid),
    "accuracy": round(accuracy, 4),
    "macro_f1": round(f1_score(true_ids, pred_ids, average="macro", zero_division=0), 4),
    "weighted_f1": round(f1_score(true_ids, pred_ids, average="weighted", zero_division=0), 4),
    "per_class": {
        label_names[i]: {
            "precision": round(precision_score(true_ids, pred_ids, labels=[i], average="macro", zero_division=0), 4),
            "recall":    round(recall_score(true_ids, pred_ids, labels=[i], average="macro", zero_division=0), 4),
            "f1":        round(f1_score(true_ids, pred_ids, labels=[i], average="macro", zero_division=0), 4),
        }
        for i in range(len(LABEL_MAP))
    },
    "label_map": LABEL_MAP,
}
with open("evaluation_results_baseline.json", "w") as f:
    json.dump(results, f, indent=2)
print("Saved: evaluation_results_baseline.json")
