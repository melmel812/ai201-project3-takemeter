"""
TakeMeter Demo — r/TrueFilm Post Classifier
Classifies posts using zero-shot Groq (llama-3.1-8b-instant).
To use the fine-tuned DistilBERT model, download takemeter-model/ from Colab
and swap the classify() function for local inference.
"""

import os
import gradio as gr
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

LABEL_DESCRIPTIONS = {
    "analysis": "Examines HOW a film works at the craft level (cinematography, editing, score, narrative structure). Argument is about technique and its effect on the viewer.",
    "interpretation": "Proposes a reading of what a film MEANS — its themes, symbols, subtext, or allegory. Evidence is drawn from the film in service of a claim about significance.",
    "opinion": "Makes a VALUE JUDGMENT about a film's quality, cultural standing, or ranking. The primary claim is evaluative: good/bad, overrated/underrated, better/worse.",
    "reaction": "Centered on the PERSONAL EXPERIENCE of watching — emotional response, first-discovery context, what the film felt like. Narrates an experience rather than making an argument.",
}

VALID_LABELS = list(LABEL_DESCRIPTIONS.keys())

SYSTEM_PROMPT = """Classify this r/TrueFilm post into exactly one of these four categories:

analysis: examines HOW a film works at the craft level — cinematography, editing, score, performance, narrative structure. The claim is about formal technique and its effect on the viewer. Evidence is specific: a named scene, a shot, a transition.

interpretation: proposes a reading of what a film MEANS — its themes, symbols, subtext, or allegory. Evidence is drawn from the film in service of a claim about significance, not technique.

opinion: makes a VALUE JUDGMENT about a film's quality, cultural standing, or ranking. The primary claim is evaluative: good/bad, overrated/underrated, better/worse. Evidence supports a verdict.

reaction: centered on the PERSONAL EXPERIENCE of watching — emotional response, first-discovery context, what the film felt like in the moment. Narrates a viewing experience rather than making an argument.

Respond with ONLY the label. No punctuation. No explanation.
Valid responses: analysis, interpretation, opinion, reaction"""


def classify_post(text: str):
    if not text or not text.strip():
        return "—", 0.0, "Please enter a post."

    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text.strip()[:1500]},
            ],
            temperature=0,
            max_tokens=10,
            logprobs=True,
            top_logprobs=4,
        )
    except Exception as e:
        return "Error", 0.0, f"API error: {e}"

    raw = resp.choices[0].message.content.strip().lower()
    predicted = None
    for label in sorted(VALID_LABELS, key=len, reverse=True):
        if raw == label or label in raw:
            predicted = label
            break

    if predicted is None:
        return f"Unparseable: '{raw}'", 0.0, "Model returned an unexpected response."

    # Extract token-level log probabilities if available
    confidence = None
    try:
        top_lp = resp.choices[0].logprobs.content[0].top_logprobs
        for lp in top_lp:
            tok = lp.token.strip().lower()
            if tok == predicted:
                import math
                confidence = round(math.exp(lp.logprob), 3)
                break
    except Exception:
        pass

    if confidence is None:
        confidence = "n/a (logprobs unavailable)"

    description = LABEL_DESCRIPTIONS[predicted]
    explanation = (
        f"**Predicted label:** `{predicted}`  \n"
        f"**Confidence:** {confidence}  \n\n"
        f"**What this label means:** {description}"
    )

    return predicted.upper(), confidence, explanation


EXAMPLES = [
    ["Kubrick's use of one-point perspective in The Shining creates a false sense of order that the narrative systematically dismantles. The Overlook's symmetrical corridors suggest a trap — space that looks rational but leads nowhere. The geometry in the bathroom scene, where the vanishing point pulls your eye directly to Jack, reappears in the maze finale with a fatal misdirection."],
    ["The recurring motif of broken clocks in Tarkovsky's Stalker isn't about time running out — it's about time being irrelevant inside the Zone. Causality itself doesn't apply there. The stopped clock is the film's thesis made physical: you've entered a space where the rules governing the rest of the world no longer hold."],
    ["Inland Empire is Lynch's best work and it's not close. It's the only film in his catalog that earns its incoherence — the fragmentation feels necessary, not decorative. Mulholland Drive is more digestible, but it's also more contained."],
    ["I watched Yi Yi last night and I'm still processing it. There's a scene near the end with a phone call I wasn't expecting and I had to pause for several minutes. I don't know how to write about it yet — I just needed to say something."],
]

with gr.Blocks(title="TakeMeter — r/TrueFilm Post Classifier") as demo:
    gr.Markdown(
        """
# TakeMeter
### r/TrueFilm Post Classifier

Classifies a post into one of four discourse categories:
`analysis` · `interpretation` · `opinion` · `reaction`

*Powered by zero-shot Groq (llama-3.1-8b-instant). For fine-tuned DistilBERT inference, load `takemeter-model/` from the Colab notebook.*
        """
    )

    with gr.Row():
        with gr.Column(scale=2):
            text_input = gr.Textbox(
                label="Paste a r/TrueFilm post",
                placeholder="Paste a post here...",
                lines=8,
            )
            classify_btn = gr.Button("Classify", variant="primary")

        with gr.Column(scale=1):
            label_output = gr.Textbox(label="Predicted Label", interactive=False)
            confidence_output = gr.Textbox(label="Confidence", interactive=False)
            explanation_output = gr.Markdown(label="Explanation")

    gr.Examples(
        examples=EXAMPLES,
        inputs=text_input,
        label="Example posts (one per label)",
    )

    classify_btn.click(
        fn=classify_post,
        inputs=text_input,
        outputs=[label_output, confidence_output, explanation_output],
    )

if __name__ == "__main__":
    demo.launch()
