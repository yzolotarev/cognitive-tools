# Study Engine integration

Cognitive Augmentation Layer is intended to sit in front of the Study Engine.

The division is simple:

```text
any desktop app
    |
    | selected/copied text
    v
Cognitive Layer
    |
    | compress / relate / predict / reconstruct / map
    v
Study Engine
    |
    | durable state, topics, sessions, assessment, revision
    v
learning history
```

The first version does not assume a concrete Study Engine API. This keeps the tool usable immediately and avoids coupling the desktop layer to an unfinished backend.

## Suggested bridge later

A Study Engine endpoint can become the `COGNITIVE_API_URL` target or sit behind it.

The useful split is:

- Cognitive Layer: fast, transient, interaction-level operations.
- Study Engine: persistent objects and decisions.
- LLM: inference/generation only; it should not become the system of record.

A later bridge can send successful outputs back to the Study Engine as events such as:

```json
{
  "event": "cognitive_action",
  "action": "compress",
  "source": "desktop_selection",
  "output": "X causes Y under Z"
}
```

The Study Engine can then decide whether to turn that event into a note, concept, question, gap, revision item, or nothing at all.

That keeps the augmentation layer small and lets the Study Engine remain the place where durable learning state lives.
