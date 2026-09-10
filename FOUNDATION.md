# Cognitive Learning Foundation

This file is the compact formal basis we extracted from the supplied Sang/iCanStudy corpus. It is a reconstruction of the corpus, not a claim that every underlying empirical statement has been independently established.

## 1. Definitions

- **Studying** — external activity associated with learning: reading, writing, lectures, flashcards, highlighting, etc.
- **Learning** — internal cognitive change / encoding and subsequent reconstruction of knowledge.
- **Schema** — a structured network of knowledge nodes and relations.
- **Cognitive Load** — the amount of active processing demand on the working-memory system.
- **Encoding** — incorporation of information into a cognitive structure.
- **Retrieval** — access to an existing representation.
- **Reconstruction** — rebuilding or recombining known elements into a new configuration and testing whether the resulting structure works.
- **Prediction Error** — a mismatch between an active hypothesis and subsequently encountered information.

## 2. Axioms

### AX1 — Learning is not identical to external study activity

`Learning != Studying`

Time spent performing study behaviors is not itself evidence that durable learning occurred.

### AX2 — Useful knowledge is relationally structured

`Knowledge = Nodes + Relations`

For mastery-oriented learning, isolated facts are weaker than an integrated schema of functional, causal, hierarchical, comparative, or otherwise meaningful relations.

### AX3 — Memory depends on cognitive processing, not exposure alone

`Retention = f(CognitiveProcessing)`

The relevant residue of learning is connected to the thought and processing performed during engagement with the material.

### AX4 — Active processing capacity is limited

`WM_capacity < infinity`

The system cannot indefinitely ingest independent units without compression, integration, or loss.

### AX5 — Useful processing occupies a bounded load range

`Underload < Optimum < Overload`

Both insufficient engagement and excessive load can impair effective processing. Approaching overload is therefore a control signal, not a command to push harder.

### AX6 — Integrated processing is preferred to isolated accumulation for transferable knowledge

`IntegratedSchema > IsolatedAccumulation`

when the task requires understanding, flexible retrieval, transfer, or problem solving.

### AX7 — Hypothesis followed by evidence enables corrective updating

`Hypothesis + Evidence -> SchemaUpdate`

A deliberate prediction creates an opportunity for a prediction error and subsequent restructuring.

### AX8 — Strong encoding reduces dependence on frequent mechanical repetition

`EncodingQuality ↑ -> RepetitionDependence ↓`

This does not prohibit revision or spaced repetition; it rejects their use as the primary substitute for poor encoding.

### AX9 — Mastery includes reconstruction under changed conditions

`Mastery -> Reconstruction`

A stronger test of a learned structure is the ability to recombine it, explain mechanisms, or use it under altered constraints.

### AX10 — Learning is recursive and adaptive

`Input -> Process -> Detect -> Adjust -> Input`

The learner continually monitors the state of understanding and changes the procedure accordingly.

## 3. Derived theorems / principles

### T1 — Study time is not a sufficient quality metric

From AX1 and AX3:

`StudyTime !-> Retention`

### T2 — Information growth creates a need for compression

From AX2 and AX4:

`RawElements ↑ -> NeedForChunking ↑`

### T3 — Overload implies a stop-and-consolidate action

From AX4 and AX5:

`Load -> Overload => StopInput -> Simplify -> Integrate -> Resume`

### T4 — Too many relations can imply rechunking, not deletion

A dense cluster around one concept may signal that the concept should become a higher-order organizing node.

### T5 — Source order is not identical to knowledge structure

`SourceOrder != KnowledgeOrder`

Reordering can be used to avoid simply inheriting the author's presentation structure.

### T6 — Prediction error is useful when a hypothesis is revised against evidence

`PriorHypothesis != Evidence -> Update`

### T7 — Recall success is not sufficient evidence of mastery

`Recall !-> Mastery`

when the task actually requires flexible reconstruction or transfer.

### T8 — A knowledge gap may be a missing relation rather than a missing node

`Known(A) + Known(B) + Missing(Relation(A,B)) -> StructuralGap`

### T9 — A map is allowed to change

`Schema(t+1) != Schema(t)`

may be an improvement rather than an error when new information changes the most useful organization.

### T10 — Whole–Part–Whole is a reconstruction cycle

`Whole -> Part -> Whole`

The local investigation is followed by reintegration into the global model.

## 4. Operational methods derived from the basis

### BHS

`Aim -> Shoot -> Skin`

- **Aim:** scope the domain, identify relevant concepts, ask why they matter, ask how they relate, form a tentative backbone.
- **Shoot:** inspect evidence and test/correct the backbone.
- **Skin:** consolidate, rechunk, prune, and isolate remaining arbitrary details.

### Micro-learning cycle

`Prime -> Map -> Explore -> Dive -> Consolidate`

### Core cognitive actions

- **Compress** — reduce material to a core invariant or claim.
- **Relate** — identify an important relation between nodes.
- **Predict** — form a hypothesis before verification.
- **Reconstruct** — test the structure under new constraints.
- **Map** — externalize nodes and relations compactly.

## 5. Heuristics, not axioms

These numbers are operational rules from the corpus, not logical consequences of the axioms:

- **2–4 rule:** aim for roughly 2–4 child items in a chunk.
- **24-hour review:** early consolidation within roughly 24 hours.
- **Expanding gaps:** roughly 2–3× growth in later revision intervals.
- **30–40 second scoping rule:** get a rough definition of an unknown term and move on.
- **15–30 keywords:** rapid first-pass scoping target.

These should be treated as tunable heuristics and can be revised without changing the core theory.

## 6. Exceptions / domain boundaries

### E1 — Arbitrary facts

Some facts cannot be usefully derived from the relational schema. A specialized memory mechanism such as flashcards or loci may be appropriate downstream.

### E2 — Procedural and motor skills

The supplied corpus itself leaves open whether the same framework applies seamlessly to pure procedural execution. Treat this as an unresolved domain rather than silently extending the theory.

### E3 — Minimal definitions are allowed

The prohibition against isolated `What is X?` questions is not absolute. When a term is completely unknown, a minimal definition may be needed before relational processing becomes possible.

### E4 — Difficulty is not monotonically good

`MoreDifficulty -> BetterLearning` is not a valid theorem. Productive challenge is bounded by the load-optimum condition.

### E5 — Linear structures are not forbidden

A genuinely sequential procedure can require `A -> B -> C`. The issue is relying on serial structure as the only representation when lateral / functional relations are needed.

## 7. Epistemic rule

The following distinctions should remain explicit:

`definition != empirical claim != derived principle != heuristic != anecdote`

The system should preserve traceability to the supplied corpus and avoid silently promoting a practical heuristic into a scientific law.
