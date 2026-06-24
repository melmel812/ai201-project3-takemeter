# TakeMeter — Planning Document

---

## 1. Community

**r/TrueFilm** is a subreddit dedicated to serious film discussion. Unlike general movie communities, it explicitly discourages plot summary and shallow reactions in favor of critical engagement. The subreddit's own rules push members toward argument and evidence: posts must go beyond "I liked it" to make a claim, and titles alone can't carry the weight of a submission.

**Why it's a good fit for classification:** The same film can generate four completely different types of discourse on r/TrueFilm in the same week — a technical breakdown of a director's cinematography, a symbolic reading of the ending, a contrarian opinion about its cultural standing, and a first-time-watch emotional response. This isn't true of most communities. On r/movies or Letterboxd, posts collapse into a narrower range (mostly opinion and reaction). r/TrueFilm's explicit culture of critical seriousness creates natural variety in how people write, which is exactly what a classifier needs to learn from.

The distinctions also *matter* to community members. A post calling a film "the best of the decade" (opinion) produces a different thread than one explaining why a specific scene's color grading encodes character psychology (analysis). Members expect different responses to different kinds of posts, and frequently complain when a thread devolves from one type to another. This makes the taxonomy socially real, not just analytically convenient.

---

## 2. Label Taxonomy

### `analysis`
A post that examines **how** a film works at the level of craft: cinematography, editing, score, performance, narrative structure, mise-en-scène. The claim is about formal technique and its effect on the viewer. Evidence is specific — a named scene, a shot, a transition — and the reasoning stays close to the film as a constructed object.

**Example 1:**
> "Kubrick's use of one-point perspective in *The Shining* creates a false sense of order that the narrative systematically dismantles. The Overlook's symmetrical corridors suggest a trap — space that looks rational but leads nowhere. The geometry in the bathroom scene, where the vanishing point pulls your eye directly to Jack, reappears in the maze finale with a fatal misdirection. The visual language is consistent; the meaning it carries flips."

**Example 2:**
> "Wong Kar-wai shoots almost entirely with a 28mm lens in *Chungking Express*, producing a slight fisheye distortion that pushes background figures into soft blur while pulling foreground faces uncomfortably close. This isn't purely aesthetic — it encodes the characters' emotional state: hyper-aware of whoever is in front of them, barely conscious of the world beyond. The lens choice *is* the characterization."

---

### `interpretation`
A post that proposes a reading of a film's **meaning** — its themes, symbols, subtext, or allegory. The focus is on what the film is *about* beneath the surface. Evidence is drawn from the film (motifs, dialogue, structure) but in service of a claim about significance, not technique.

**Example 1:**
> "The recurring motif of broken clocks in Tarkovsky's *Stalker* isn't about time running out — it's about time being irrelevant inside the Zone. Causality itself doesn't apply there. The stopped clock is the film's thesis made physical: you've entered a space where the rules governing the rest of the world no longer hold."

**Example 2:**
> "The Zone in *Stalker* is a projection of desire, which is why it destroys those who approach it instrumentally. The Stalker doesn't protect it because he believes in its magic; he protects it because he believes in the pilgrims' *need* for it to be magic. The film is about what it costs to keep something sacred in a world that has stopped believing."

---

### `opinion`
A post that makes a **value judgment** about a film's quality, cultural standing, or ranking. The primary claim is evaluative: good/bad, overrated/underrated, better/worse than. Evidence may be present, but it's deployed in support of a verdict rather than as the substance of an argument.

**Example 1:**
> "*Rashomon* is overrated as a meditation on subjectivity. Every film textbook treats it as the definitive example of unreliable narration, but the central thesis — that truth is unknowable — is undercut by the woodcutter's testimony at the end, which the film implicitly treats as reliable. Kurosawa undermines his own premise, and nobody seems to notice."

**Example 2:**
> "*Inland Empire* is Lynch's best work and it's not close. It's the only film in his catalog that earns its incoherence — the fragmentation feels necessary, not decorative. *Mulholland Drive* is more digestible, but it's also more contained. *Inland Empire* is genuinely untamable, which is exactly what Lynch has always been reaching for."

---

### `reaction`
A post centered on the **personal experience of watching** — emotional response, the context of first discovery, what the film felt like in the moment. The post narrates a viewing experience rather than making a formal, interpretive, or evaluative argument.

**Example 1:**
> "I watched *Yi Yi* last night and I'm still processing it. There's a scene near the end with a phone call I wasn't expecting and I had to pause for several minutes. I don't know how to write about it yet — I just needed to say something."

**Example 2:**
> "Just finished *Caché* for the first time. I spent the entire second half convinced I knew what was happening and the film just... refused to confirm it. Still don't know how I feel. I'm going to go for a walk and come back to this."

---

## 3. Edge Cases and Decision Rules

### analysis vs. interpretation
**Hard case:** A post about handheld camera in *Children of Men* that starts with technique ("the camera puts you inside the chaos") and ends with a thematic claim ("it implicates the viewer — you're not watching a dystopia, you're in one").

**Decision rule:** Where does the argument land? If the conclusion is about what the technique *produces in the viewer as an experience* (tension, disorientation, immersion), it's **analysis**. If the conclusion is about what the technique *means thematically* (complicity, moral implication, the film's political argument), it's **interpretation**.

---

### interpretation vs. opinion
**Hard case:** A post that unpacks an ending ("the ending is Hogg accepting that memory is a construct — the film she's making is the only truth she can access") and then concludes: "this is why it's Hogg's masterpiece."

**Decision rule:** What is the post *building toward*? If the interpretive unpacking is in service of a value judgment at the end, it's **opinion**. If the evaluative phrase is a throwaway and the substance is unpacking meaning, it's **interpretation**. The evaluative claim must be *incidental* to label it interpretation.

---

### opinion vs. reaction
**Hard case:** "I finally watched *Jeanne Dielman* last week. By the end I had completely lost track of the outside world. I think it might be the most important film I've ever seen."

**Decision rule:** Remove the evaluative sentence — does the post still have a point? If yes (the watching experience is the point), it's **reaction**. If the evaluative claim is doing the work, it's **opinion**. Here, removing the last sentence leaves a pure watching experience → **reaction**.

---

### reaction vs. analysis
**Hard case:** "I was completely transfixed by the way *Stalker* uses silence — there's almost no score for the first hour and I didn't notice until the music finally arrived. That's an incredible technical achievement."

**Decision rule:** If the post arrives at a specific formal observation even via personal experience, it's **analysis**. The personal narration is incidental. Reaction posts never land on a technical claim — they stay in the register of feeling and experience.

---

### Unresolvable cases
Posts that sit at a genuine boundary after applying all four rules will be noted and excluded from the dataset rather than assigned arbitrarily. A forced label on a genuinely ambiguous post adds noise, not signal.

---

## 4. Data Collection Plan

**Source:** r/TrueFilm posts and top-level comments via the Reddit API (PRAW). Target: the top 1,000 posts of all time and the top 200 posts from the past year, plus comments from high-upvote threads.

**Target volume:** 220 labeled examples — 55 per label. This gives 70% / 15% / 15% train/val/test splits of roughly 154 / 33 / 33, with at least 8 test examples per class.

**Expected imbalance:** `reaction` posts are underrepresented on r/TrueFilm because the subreddit actively discourages them (the mod team redirects pure reaction posts to weekly threads). If I reach 200 examples and `reaction` is below 40, I will supplement from:
1. r/TrueFilm weekly "Just Watched" and "First Time Watch" megathreads
2. The "What did you watch this week?" thread, which collects shorter emotional responses

If `analysis` is overrepresented (likely, since it's the prestige post type), I will stop collecting analysis posts after 70 and continue collecting other types.

**Annotation process:** All examples annotated by me using the definitions and decision rules in Section 3. I will annotate in batches of 30 and review each batch against the decision rules before continuing. For each borderline case, I write a one-line note in the CSV explaining which rule I applied.

**CSV format:** `text`, `label`, `source_url`, `annotation_notes` (optional).

---

## 5. Evaluation Metrics

**Primary metric: macro F1**

Macro F1 averages the F1 score across all four classes with equal weight, regardless of class frequency. This is the right primary metric because:
- The dataset will likely be unbalanced (`reaction` rarer than `analysis`). Accuracy and weighted F1 are dominated by the majority classes — a model that ignores `reaction` entirely could still score 75% accuracy if `reaction` is only 15% of the test set.
- A community tool needs to work for all four post types. A classifier that's excellent at `analysis` but useless for `reaction` is not deployable. Macro F1 penalizes this equally.

**Secondary metrics:**

| Metric | Why it's needed |
|---|---|
| Per-class precision | How often the model is right when it predicts a specific label. Low precision = the label gets applied too broadly. |
| Per-class recall | How many examples of a class the model catches. Low recall = the model misses most of a class. |
| Confusion matrix | Shows which specific label pairs get confused. analysis↔interpretation confusion is expected and tolerable; reaction↔analysis confusion is a sign of a broken model. |
| Accuracy | Reported for completeness and for the required comparison table with the baseline. |

**Why accuracy alone is not enough:** If `reaction` is 15% of the test set, a model that never predicts `reaction` achieves 85% accuracy — but it's worthless for the use case. Macro F1 catches this; accuracy doesn't.

---

## 6. Definition of Success

A classifier is **genuinely useful** for a community tool (e.g., a subreddit sidebar widget that auto-tags posts) if:

1. **Macro F1 ≥ 0.72** on the held-out test set. At four classes, random chance is 0.25 (25%). A macro F1 of 0.72 represents strong performance across all four label types and is meaningfully above what a keyword-based baseline could achieve.

2. **Per-class F1 ≥ 0.60 for every label.** No label can be completely broken. A community tool that never correctly identifies `reaction` posts is not usable, even if overall macro F1 looks acceptable.

3. **Fine-tuned DistilBERT outperforms the zero-shot Groq baseline by at least 0.08 macro F1.** This validates that fine-tuning on domain-specific annotated data was worth the effort. If the zero-shot baseline is already within 0.05 of the fine-tuned model, the annotation investment was not justified.

**Error tolerance:** The most tolerable errors are analysis↔interpretation confusion (adjacent, nuanced categories; a regular member would also hesitate). The least tolerable errors are reaction↔analysis and reaction↔opinion confusion (these are the most distant categories semantically; getting them wrong would clearly misrepresent a post to the community). If any non-adjacent confusion exceeds 20% of that class's test examples, the classifier is not deployable.

**"Good enough" threshold:** Macro F1 ≥ 0.70 with no per-class F1 below 0.60. Below this, the classifier adds noise rather than value.

---

## 7. AI Tool Plan

### Label stress-testing (before annotation)

**When:** Before annotating any examples.

**What:** Give Claude all four label definitions and the four edge case decision rules, then prompt: *"Generate 8 posts for r/TrueFilm that each sit at the boundary between analysis and interpretation. Each post should use specific film vocabulary, cite a real film, and make it genuinely hard to classify using the decision rule I've written."* Repeat for the interpretation/opinion boundary (the second hardest pair).

**How I'll use the output:** If any generated post is impossible to classify cleanly under the existing rules, that's a signal that the rule is underspecified — I'll tighten the definition before starting annotation. If all 8 posts are classifiable with only mild hesitation, the definitions are ready.

**What I won't do:** Use the AI-generated boundary posts as training examples. They'll be used only to probe definition quality, then discarded.

---

### Annotation assistance (during annotation)

**Decision:** Yes, I will use Groq (llama-3.3-70b, the same model as the baseline) to pre-label the first 100 posts before reviewing them myself.

**Workflow:**
1. Collect 100 posts from r/TrueFilm
2. Run them through Groq with the same classification prompt I'll eventually use for the baseline (Section 5 of the notebook)
3. Review every Groq label myself — accept, override, or flag as ambiguous
4. For the remaining 120+ examples, annotate from scratch without AI pre-labeling

**Tracking:** The CSV will include a `prelabeled_by_ai` boolean column. Any example where Groq's label was accepted without modification will have `True`; examples I labeled from scratch or where I overrode Groq will have `False`.

**Disclosure:** The AI usage section of the README will note that ~50% of the dataset was AI-prelabeled and human-reviewed, and ~50% was annotated from scratch.

**Why not AI-label everything:** Pre-labeling then reviewing is faster than from-scratch annotation, but I need to annotate at least half from scratch to have a baseline sense of where the model consistently fails — which is valuable information before I even start training.

---

### Failure analysis (after training)

**When:** After Section 4 of the notebook produces the wrong-prediction list.

**What I'll give the AI:** The 15 wrong predictions printed by the notebook, with their true label, predicted label, and the post text.

**Prompt:** *"Here are 15 posts where a fine-tuned DistilBERT model predicted the wrong label. Each entry shows the post text, the true label, and the predicted label. What patterns do you see? Look for: (a) whether errors cluster around specific label pairs, (b) whether misclassified posts share a length range or vocabulary style, (c) whether there are structural cues the model might be over-relying on (e.g., first-person framing triggering 'reaction' regardless of content)."*

**How I'll verify:** I'll read every pattern the AI identifies and confirm it holds across at least 3 of the 15 examples before citing it in the evaluation report. I won't report a pattern I can't independently confirm in the data.

**What I'm looking for specifically:**
- analysis posts called interpretation (expected — the most frequent error)
- reaction posts called opinion when the post ends with a value-laden sentence (tests the "remove the evaluative sentence" rule)
- short posts misclassified as reaction regardless of content (a length-confound)

---

## 8. Annotation Log — Hard Cases

---

### Hard Case 1: analysis vs. interpretation
**Post excerpt:**
> "The 'Disillusionment' Moments In Paul Thomas Anderson Films — Years ago I noticed the thematic similarity between a scene in There Will Be Blood and a scene in The Master... The moment when the 'skeptic' challenges Phillip Seymour Hoffman ('I've never been to the Pyramids, and yet we know they are there, for learned men have told us.') is by far my favorite scene in The Master, and it reminds me of the funniest scene in There Will Be Blood..."

**Labels it could belong to:** `analysis` vs. `interpretation`

**What made it hard:** The post identifies a *recurring structural pattern* across multiple PTA films — which sounds like formal analysis of how those films are constructed. But the argument is ultimately about what these moments *mean* thematically across the filmography: the "disillusionment" motif as a statement about faith, belief, and the moment institutions fail their followers. The evidence is specific scenes, but the claim is about significance.

**Decision:** `interpretation` — the post's conclusion is a thematic claim about what a recurring motif means across PTA's work, not a claim about how a technique produces a formal effect; following the analysis vs. interpretation rule, if the conclusion is about thematic meaning, it's interpretation.

---

### Hard Case 2: analysis vs. interpretation
**Post excerpt:**
> "No other film captures the harshness of daydreaming as well as Scorsese's The King of Comedy. I'm referring to the scenes in which Rupert Pupkin (De Niro) daydreams about being so famous that Jerry Lewis has to beg him to come on his show... Daydreaming is quite a regular feature of our life. Yet, I haven't seen a single film capturing this all-pervasive fact of the human condition. Martin Scorsese did it though, and quite astutely."

**Labels it could belong to:** `analysis` vs. `interpretation` (and possibly `opinion` for the comparative quality claim)

**What made it hard:** The post opens with a comparative value judgment ("no other film captures..."), which pulls toward `opinion`. It then discusses what the daydream *scenes do* in the film — which pulls toward `analysis`. But the broader argument is about what daydreaming *means* as a human condition and how the film illuminates it — which pulls toward `interpretation`. Three labels have a plausible claim.

**Decision:** `analysis` — the core argument stays at the level of what the daydream sequences *produce for the viewer* (capturing the harshness of daydreaming as an experience) rather than making a thematic claim about what the film is ultimately about; the comparative quality phrase is incidental framing, not the substance of the argument.

---

### Hard Case 3: reaction vs. analysis
**Post excerpt:**
> "The Ascent (1977) and Larisa Shepitko — Going in, I knew very little about this one... Well, I had high hopes but this blew me away on a wholly unexpected level. The first thing to draw me in was the beautiful cinematography, the snow-filled setting in black and white worked superbly. I was enthralled from the start, but it's the second half that really floored me..."

**Labels it could belong to:** `reaction` vs. `analysis`

**What made it hard:** The post mentions specific formal elements — cinematography, the black-and-white snow-filled setting — which are the vocabulary of analysis. A reader could reasonably expect this to develop into a formal examination of how those choices work. But the post never lands on a formal claim; it stays in the register of "drew me in," "blew me away," "floored me." The formal observations are decorative rather than argumentative.

**Decision:** `reaction` — per the reaction vs. analysis rule, a post that arrives at a specific formal observation belongs in analysis even if it comes through personal experience; this post mentions formal elements but never makes a claim about them, staying entirely in the register of personal emotional response.

---

### Label Distribution After Annotation

| Label | Count | % of total |
|---|---|---|
| analysis | 32 | 16% |
| interpretation | 32 | 16% |
| opinion | 77 | 38.5% |
| reaction | 59 | 29.5% |
| **Total** | **200** | 100% |

Any label above 70%? No. However, `analysis` and `interpretation` are underrepresented at 16% each. To improve model balance before training, additional `analysis` and `interpretation` examples will be collected to bring each class closer to 25% (target: 50+ per class).
