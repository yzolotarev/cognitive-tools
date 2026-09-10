# Cognitive Tools: Theory and Architecture

This document records the full idea behind Cognitive Tools: a small, personal-first Linux utility that places a few cognitive operations on top of the applications where a person already reads and works.

It is an architectural and methodological reconstruction of the supplied material and its Sang / iCanStudy lineage. It is not a claim that every proposition below has been independently established as scientific fact. Definitions, design principles, hypotheses, heuristics, and implementation choices should remain distinguishable.

## 1. The central idea

For a personal-first workflow, a small local Linux application can be more useful than a browser extension or a large learning platform. It lives above other applications and operates through the clipboard.

The user selects or copies text in any application, presses a hotkey, and receives one focused cognitive operation. The tool does not need to know where the text came from. It does not need to become a knowledge-management system. Its job is to make a useful next thought cheap enough to perform while reading normally.

The first-stage architecture is intentionally small:

```text
USER
  |
  | select text / Ctrl+C
  v
CLIPBOARD
  |
  v
HOTKEY
  |
  v
LOCAL APP
  |
  +-- prompt template
  +-- selected text
  +-- optional context
  +-- custom API endpoint
          |
          v
        LLM
          |
          v
    RESULT WINDOW
```

At the current stage, this is enough. A useful first experiment is not a complete learning platform. It is a reliable loop from selected text to a better cognitive action.

## 2. Make the application deliberately simple

The application should be almost boring to operate. A minimal desktop surface might expose:

```text
Cognitive Tools

Ctrl+Q  Compress
Ctrl+R  Relate
Ctrl+P  Predict
Ctrl+T  Test / Reconstruct
Ctrl+M  Map
```

The user can select text in Firefox, Obsidian, a terminal, a PDF viewer, LibreOffice, Telegram, an IDE, or another desktop application. The application should not require a dedicated reader or an integration for each source.

A typical operation is:

```python
text = clipboard.get()

prompt = """
Compress the following text into its irreducible core claim.

Rules:
- preserve the meaning
- remove rhetoric and examples
- express causal or conditional structure when present
- output 1-3 sentences maximum

TEXT:
{text}
"""
```

The program substitutes the selected text, sends the request to the configured endpoint, and displays the result. The point is the low friction of the loop, not the complexity of the client.

## 3. A custom endpoint keeps the frontend agnostic

The application should not be bound to OpenAI, Anthropic, Gemini, or another provider. The configuration should identify an endpoint, credentials, model, and a set of actions independently:

```yaml
provider:
  base_url: "https://whatever/api/v1"
  api_key: "..."
  model: "whatever-model"

actions:
  compress:
    hotkey: "ctrl+q"
    prompt: "..."

  relate:
    hotkey: "ctrl+r"
    prompt: "..."

  reconstruct:
    hotkey: "ctrl+t"
    prompt: "..."
```

The internal interface can remain simple:

```python
response = llm.complete(
    prompt=render_prompt(template, text=clipboard_text)
)
```

This permits the same frontend to work with an OpenAI-compatible endpoint, a local Ollama server, vLLM, LM Studio, a private inference service, a remote gateway, or a custom HTTP API. The application is therefore an agnostic cognitive frontend rather than a provider-specific client.

The current implementation already uses environment variables and an OpenAI-compatible chat-completions shape. Fully user-defined YAML actions are a future configuration direction, not a current feature claim.

## 4. Prompts can be the main logic

The most important architectural decision is to avoid prematurely implementing a large internal learning system. The prompt can express the cognitive operation while the local program remains an orchestrator:

```text
Action
   |
Prompt template
   |
Clipboard text
   |
LLM
   |
Result
```

This makes the theory experimentally replaceable. A change in the cognitive model can be tested by editing a prompt instead of rewriting a knowledge graph engine, retrieval engine, cognitive architecture, or adaptive learning model.

### Compress

Compression should not mean generic summarization. It should seek the smallest representation that preserves the causal and conceptual structure:

```text
You are a cognitive compression engine.

Given TEXT, produce the smallest representation
that preserves its causal and conceptual structure.

Do not summarize examples.
Do not repeat rhetoric.
Prefer:
X -> Y
X because Y
X only if Y
X constrains Y

TEXT:
{{clipboard}}
```

The desired transformation is:

```text
Text -> Invariant
```

For example, a paragraph saying that people often believe that working longer automatically increases productivity should not become a vague summary about productivity. A stronger compression is:

```text
MoreEffort does not imply MoreOutput.
```

The result is an atom that can be related, tested, predicted from, or reconstructed.

### Relate

Relation-building should identify the strongest meaningful connection rather than merely place two summaries next to each other:

```text
Given TEXT A and TEXT B:

1. Identify their core claims.
2. Determine the strongest meaningful relationship.
3. Choose one:
   causes
   enables
   constrains
   contrasts
   depends on
   exemplifies
   generalizes
   contradicts
4. Explain in <= 3 sentences.

A:
{{selection_a}}

B:
{{selection_b}}
```

### Predict

Prediction creates a hypothesis before the next piece of evidence is read. The value is not that the prediction must be correct. The value is that the learner has an active structure that can be compared with what follows.

### Test / Reconstruct

A reconstruction question should not be answerable by simply repeating the source text. It should require the user to connect concepts, explain a causal mechanism, or handle a changed condition:

```text
Generate one reconstruction question
that cannot be answered by merely repeating
the source text.

Require the user to:
- connect at least two concepts
- explain a causal mechanism
- handle a changed condition

SOURCE:
{{clipboard}}
```

The current implementation calls this operation `RECONSTRUCT` and generates a mechanism-level stress-test question.

### Map

Mapping externalizes nodes and relations compactly. It should remain a working representation, not a claim that the final knowledge structure has been discovered permanently.

## 5. Cognitive operations as a small pipeline

The operations can be composed conceptually:

```text
Q -> R -> P -> T
```

This resembles a Unix pipeline:

```text
text | compress | relate | challenge | reconstruct
```

The analogy matters because each operation should have a clear input, a clear transformation, and a useful output. The system does not need to know everything about the learner's entire history to perform the next operation.

The five core operations are:

- **Compress**: reduce material to a core invariant or claim.
- **Relate**: identify a meaningful relation between concepts or nodes.
- **Predict**: form a hypothesis before verification.
- **Reconstruct**: test the structure under changed constraints.
- **Map**: externalize nodes and relations compactly.

These actions are deliberately small. They are not intended to replace reading, thinking, practice, revision, or a durable study system.

## 6. Clipboard abstraction and application independence

The application should not try to understand where the user is. Integrating separately with browsers, PDF readers, terminals, ebook readers, chats, and IDEs creates unnecessary coupling.

The clipboard abstraction covers the common path:

```text
Any application
      |
    Ctrl+C
      |
      v
  Cognitive Tools
```

The user should be able to carry the same operation across different contexts. In the current Linux/X11 implementation, PRIMARY selection is checked first and the normal clipboard is used as a fallback.

## 7. Minimal local history

One useful extension is a small local history:

```text
10:42  Compress   [text...]
10:43  Relate     [A] [B]
10:45  Test       [question]
```

This is not intended to become a second brain, a knowledge graph, or a durable learning database. It solves one narrow problem: remembering an answer from five minutes ago.

SQLite would be sufficient for this purpose. However, local history is a proposed extension, not part of the current first-stage implementation. The current design remains stateless by default, apart from lightweight event logging.

## 8. Linux and implementation choices

For a personal tool, Python is a practical first implementation because iteration speed matters more than architectural grandeur. A possible broader stack is:

```text
Python
|-- PySide6       UI
|-- pynput/evdev  hotkeys
|-- clipboard     clipboard access
|-- httpx         API client
|-- pydantic      configuration
|-- sqlite3       history
`-- yaml          configuration
```

A possible result window could be:

```text
+-----------------------------+
| Cognitive                   |
+-----------------------------+
| Compress                    |
|                             |
| Core claim:                 |
| X causes Y under Z.         |
|                             |
| [Copy] [Insert] [Again]    |
+-----------------------------+
```

The current implementation is intentionally narrower: Python with GTK/X11, global hotkeys, X11 selection and clipboard access, an OpenAI-compatible HTTP endpoint, and a GTK popup. PySide6, `pynput`, YAML configuration, richer buttons, and SQLite history belong to the possible evolution of the design, not to the current feature list.

## 9. User-programmable cognitive augmentation

A later version can make actions entirely user-defined:

```yaml
actions:
  compress:
    hotkey: "ctrl+q"
    input: clipboard
    output: popup
    prompt: |
      ...

  why:
    hotkey: "ctrl+w"
    input: clipboard
    output: popup
    prompt: |
      ...

  relation:
    hotkey: "ctrl+r"
    input: clipboard
    prompt: |
      ...

  challenge:
    hotkey: "ctrl+t"
    input: clipboard
    prompt: |
      ...

  simplify:
    hotkey: "ctrl+s"
    input: clipboard
    prompt: |
      ...
```

This would let a user program a personal cognitive augmentation layer through prompts. The architecture remains stable while the theory and operations evolve.

## 10. What not to build first

The first version should not begin with:

- a beautiful graph of knowledge;
- an AI tutor;
- an LMS;
- a planner;
- streaks or gamification;
- accounts;
- cloud synchronization;
- a vector database;
- RAG;
- embeddings;
- a spaced-repetition algorithm.

These systems may eventually be useful, but they increase the distance between an idea and a usable experiment. The intended direction is:

```text
Idea -> Tiny experiment
```

not:

```text
Idea -> Large project
```

The tool is not a product before it has become useful to its own author.

## 11. The MVP criterion

The first criterion is concrete:

> Open a PDF, select a paragraph, press `Ctrl+Q`, and receive a useful compression.

If that operation is pleasant and reliable many times, add another operation:

```text
Ctrl+R -> relation
Ctrl+T -> reconstruction
```

After a few weeks, the project can produce actual evidence about which operations change behavior:

```text
Which operations actually change behavior?
```

That empirical feedback is more valuable than assuming in advance that every theoretically attractive operation will be useful. The framework itself should be iteratively tested, corrected, and rebuilt rather than idealized as a finished structure.

## 12. Relation to a durable Study Engine

Cognitive Tools is an interaction-side augmentation, not a replacement for a durable Study Engine:

```text
Study Engine
  durable study state / topics / sessions / revision / assessment
             ^
             |
      cognitive actions
             |
Cognitive Layer
  compress / relate / predict / reconstruct / map
             ^
             |
      selected/copied text
             ^
             |
      any desktop application
```

The Cognitive Layer should remain stateless by default. Its job is to make the next useful cognitive action cheap in the middle of normal reading. A Study Engine can remain the place where durable learning state is stored and assessed.

A later integration could let a Study Engine provide context or receive successful reconstruction results, but the first version should not require a specific Study Engine API.

## 13. Formal cognitive foundation

The following section preserves the compact formal model that accompanies the architectural theory.

### 13.1 Definitions

- **Studying**: external activity associated with learning, including reading, writing, lectures, flashcards, and highlighting.
- **Learning**: internal cognitive change, encoding, and subsequent reconstruction of knowledge.
- **Schema**: a structured network of knowledge nodes and relations.
- **Cognitive load**: the amount of active processing demand on the working-memory system.
- **Encoding**: incorporation of information into a cognitive structure.
- **Retrieval**: access to an existing representation.
- **Reconstruction**: rebuilding or recombining known elements into a new configuration and testing whether the resulting structure works.
- **Prediction error**: a mismatch between an active hypothesis and subsequently encountered information.

### 13.2 Axioms and principles

#### AX1: Learning is not identical to external study activity

```text
Learning != Studying
```

Time spent performing study behaviors is not itself evidence that durable learning occurred.

#### AX2: Useful knowledge is relationally structured

```text
Knowledge = Nodes + Relations
```

For mastery-oriented learning, isolated facts are weaker than an integrated schema of functional, causal, hierarchical, comparative, or otherwise meaningful relations.

#### AX3: Memory depends on cognitive processing, not exposure alone

```text
Retention = f(CognitiveProcessing)
```

The relevant residue of learning is connected to the thought and processing performed during engagement with the material.

#### AX4: Active processing capacity is limited

```text
WM_capacity < infinity
```

The system cannot indefinitely ingest independent units without compression, integration, or loss.

#### AX5: Useful processing occupies a bounded load range

```text
Underload < Optimum < Overload
```

Both insufficient engagement and excessive load can impair effective processing. Approaching overload is therefore a control signal, not a command to push harder.

#### AX6: Integrated processing is preferred to isolated accumulation for transferable knowledge

```text
IntegratedSchema > IsolatedAccumulation
```

This applies when the task requires understanding, flexible retrieval, transfer, or problem solving.

#### AX7: Hypothesis followed by evidence enables corrective updating

```text
Hypothesis + Evidence -> SchemaUpdate
```

A deliberate prediction creates an opportunity for a prediction error and subsequent restructuring.

#### AX8: Strong encoding reduces dependence on mechanical repetition

```text
EncodingQuality increases -> RepetitionDependence decreases
```

This does not prohibit revision or spaced repetition. It rejects their use as the primary substitute for poor encoding.

#### AX9: Mastery includes reconstruction under changed conditions

```text
Mastery -> Reconstruction
```

A stronger test of a learned structure is the ability to recombine it, explain mechanisms, or use it under altered constraints.

#### AX10: Learning is recursive and adaptive

```text
Input -> Process -> Detect -> Adjust -> Input
```

The learner monitors the state of understanding and changes the procedure accordingly.

### 13.3 Derived principles

#### T1: Study time is not a sufficient quality metric

```text
StudyTime !-> Retention
```

#### T2: Information growth creates a need for compression

```text
RawElements increase -> NeedForChunking increase
```

#### T3: Overload implies a stop-and-consolidate action

```text
Load -> Overload => StopInput -> Simplify -> Integrate -> Resume
```

#### T4: Too many relations can imply rechunking, not deletion

A dense cluster around one concept may signal that the concept should become a higher-order organizing node.

#### T5: Source order is not identical to knowledge structure

```text
SourceOrder != KnowledgeOrder
```

Reordering can avoid simply inheriting the author's presentation structure.

#### T6: Prediction error is useful when a hypothesis is revised against evidence

```text
PriorHypothesis != Evidence -> Update
```

#### T7: Recall success is not sufficient evidence of mastery

```text
Recall !-> Mastery
```

This matters when the task requires flexible reconstruction or transfer.

#### T8: A knowledge gap may be a missing relation rather than a missing node

```text
Known(A) + Known(B) + Missing(Relation(A,B)) -> StructuralGap
```

#### T9: A map is allowed to change

```text
Schema(t+1) != Schema(t)
```

A changed schema may be an improvement when new information changes the most useful organization.

#### T10: Whole-Part-Whole is a reconstruction cycle

```text
Whole -> Part -> Whole
```

Local investigation is followed by reintegration into the global model.

### 13.4 Operational methods

#### BHS

```text
Aim -> Shoot -> Skin
```

- **Aim**: scope the domain, identify relevant concepts, ask why they matter, ask how they relate, and form a tentative backbone.
- **Shoot**: inspect evidence and test or correct the backbone.
- **Skin**: consolidate, rechunk, prune, and isolate remaining arbitrary details.

#### Micro-learning cycle

```text
Prime -> Map -> Explore -> Dive -> Consolidate
```

#### Core actions

- **Compress**: reduce material to a core invariant or claim.
- **Relate**: identify an important relation between nodes.
- **Predict**: form a hypothesis before verification.
- **Reconstruct**: test the structure under new constraints.
- **Map**: externalize nodes and relations compactly.

### 13.5 Heuristics, not axioms

These numbers are operational rules from the source material, not logical consequences of the axioms:

- **2-4 rule**: aim for roughly 2-4 child items in a chunk.
- **24-hour review**: early consolidation within roughly 24 hours.
- **Expanding gaps**: roughly 2-3x growth in later revision intervals.
- **30-40 second scoping rule**: get a rough definition of an unknown term and move on.
- **15-30 keywords**: rapid first-pass scoping target.

These are tunable heuristics. They can be revised without changing the core theory.

### 13.6 Exceptions and domain boundaries

- **Arbitrary facts**: some facts cannot be usefully derived from a relational schema. Flashcards, loci, or another specialized memory mechanism may be appropriate downstream.
- **Procedural and motor skills**: it remains open whether the same framework applies seamlessly to pure procedural execution. This should remain an unresolved domain rather than an untested extension.
- **Minimal definitions**: the prohibition against isolated "What is X?" questions is not absolute. A completely unknown term may need a minimal definition before relational processing is possible.
- **Difficulty is not monotonically good**: `MoreDifficulty -> BetterLearning` is not a valid theorem. Productive challenge is bounded by the load-optimum condition.
- **Linear structures are not forbidden**: a genuinely sequential procedure can require `A -> B -> C`. The issue is relying on serial structure as the only representation when lateral or functional relations are needed.

### 13.7 Epistemic rule

The following distinctions should remain explicit:

```text
definition != empirical claim != derived principle != heuristic != anecdote
```

The system should preserve traceability to the supplied corpus and avoid silently promoting a practical heuristic into a scientific law.

## 14. Attribution and reuse

This theory and the implementation are based on the original idea and methodology developed by Justin Sung, together with the practical implementation work by the project author. Anyone who reuses, adapts, or extends this project must acknowledge:

- the project author as the original implementer of this code and tooling;
- Justin Sung as the original methodological source and conceptual foundation of the cognitive workflow;
- the Sang / iCanStudy methodological lineage from which this work derives.

Reuse is allowed, but attribution is required. The project and its conceptual model should not be presented as a fresh, standalone invention without citing the original authorship and methodological source.
