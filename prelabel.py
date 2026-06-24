"""
prelabel.py — AI-assisted pre-labeling for TakeMeter annotation

Reads truefilm_raw.csv (unlabeled), asks Groq to assign one label per post,
and writes truefilm_prelabeled.csv with a `prelabeled_by_ai` column.

YOU MUST review and correct every label before using this CSV for training.
Do not trust the AI labels without reading the post yourself.

Setup:
  pip install groq python-dotenv
  Add GROQ_API_KEY to your .env file

Usage:
  python prelabel.py                    # pre-label first 100 posts
  python prelabel.py --all              # pre-label every post (slower)
  python prelabel.py --start 100        # continue from row 100
"""

import argparse
import time
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

# ── Label definitions (copied from planning.md) ────────────────────────────────
SYSTEM_PROMPT = """You are classifying posts from r/TrueFilm, a subreddit for serious film discussion.

Assign each post to EXACTLY ONE of these four categories:

analysis: The post examines HOW a film works at the level of craft — cinematography, editing, score, performance, narrative structure, mise-en-scène. The claim is about formal technique and its effect. Evidence is specific (a named scene, a shot, a transition) and the reasoning stays close to the film as a constructed object.
Example: "Kubrick's use of one-point perspective in The Shining creates a false sense of order that the narrative systematically dismantles."

interpretation: The post proposes a reading of a film's MEANING — its themes, symbols, subtext, or allegory. The focus is on what the film is about beneath the surface. Evidence is drawn from the film (motifs, dialogue, structure) but in service of a claim about significance, not technique.
Example: "The broken clocks in Stalker aren't about time running out — they're about causality being irrelevant inside the Zone."

opinion: The post makes a VALUE JUDGMENT about a film's quality, cultural standing, or ranking. The primary claim is evaluative: good/bad, overrated/underrated, better/worse than. Evidence may be present but supports a verdict rather than being the substance of the argument.
Example: "Rashomon is overrated as a meditation on subjectivity. Kurosawa undermines his own premise and nobody seems to notice."

reaction: The post is centered on the PERSONAL EXPERIENCE of watching — emotional response, first-discovery context, what the film felt like in the moment. The post narrates a viewing experience rather than making a formal, interpretive, or evaluative argument.
Example: "I watched Yi Yi last night and I'm still processing it. I just needed to say something."

Decision rules for boundary cases:
- analysis vs interpretation: if the conclusion is about thematic meaning, it's interpretation; if it stays at the level of formal effect on the viewer, it's analysis
- interpretation vs opinion: if the unpacking is building toward a quality verdict, it's opinion; if the quality phrase is a throwaway, it's interpretation
- opinion vs reaction: remove the evaluative sentence — if the post still has a point, it's reaction; if the evaluative claim was doing the work, it's opinion
- reaction vs analysis: if the post lands on a specific formal observation, it's analysis regardless of how it got there

Respond with ONLY the label name. No explanation. No punctuation.
Valid labels: analysis, interpretation, opinion, reaction"""


def classify(client: Groq, text: str) -> str | None:
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Classify this post:\n\n{text[:1500]}"},
            ],
            temperature=0,
            max_tokens=15,
        )
        raw = response.choices[0].message.content.strip().lower()
        for label in ["analysis", "interpretation", "opinion", "reaction"]:
            if raw == label or label in raw:
                return label
        return None
    except Exception as e:
        print(f"  API error: {e}")
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Pre-label all posts, not just first 100")
    parser.add_argument("--start", type=int, default=0, help="Start from row N (for resuming)")
    args = parser.parse_args()

    if not os.path.exists("truefilm_raw.csv"):
        print("truefilm_raw.csv not found. Run collect_data.py first.")
        return

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    df = pd.read_csv("truefilm_raw.csv", dtype={"label": str, "annotation_notes": str})
    df["label"] = df["label"].fillna("")
    df["annotation_notes"] = df["annotation_notes"].fillna("")

    # Determine which rows to pre-label
    end = len(df) if args.all else min(args.start + 100, len(df))
    target_rows = list(range(args.start, end))
    print(f"Pre-labeling rows {args.start}–{end - 1} ({len(target_rows)} posts)...")
    print("Review every label yourself before using this file for training.\n")

    # Ensure columns exist
    if "prelabeled_by_ai" not in df.columns:
        df["prelabeled_by_ai"] = False

    for i, idx in enumerate(target_rows):
        text = df.at[idx, "text"]
        pred = classify(client, text)

        if pred:
            df.at[idx, "label"] = pred
            df.at[idx, "prelabeled_by_ai"] = True
        else:
            print(f"  Row {idx}: unparseable response — leaving blank for manual review")

        if (i + 1) % 10 == 0:
            pct = (i + 1) / len(target_rows) * 100
            print(f"  {i + 1}/{len(target_rows)} ({pct:.0f}%)...")

        time.sleep(0.15)  # stay within free-tier rate limits

    df.to_csv("truefilm_prelabeled.csv", index=False)

    # Print distribution of pre-labeled posts
    labeled = df[df["prelabeled_by_ai"] == True]
    print(f"\nSaved truefilm_prelabeled.csv")
    print(f"Pre-labeled: {len(labeled)} posts")
    print("\nLabel distribution (pre-labeled only — NOT final):")
    print(labeled["label"].value_counts().to_string())
    print("\nNext step: open truefilm_prelabeled.csv in a spreadsheet,")
    print("review every label, correct mistakes, and fill in annotation_notes")
    print("for any cases that gave you pause.")


if __name__ == "__main__":
    main()
