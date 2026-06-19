# GEM Pipeline · Custom GPT Builder

> Turn a one-sentence idea into a production-ready Custom GPT — System Prompt and Knowledge Base — through a six-stage automated pipeline.

An n8n workflow that chains six specialized LLM nodes (Architect → Domain Expert → Operationalizer → KB Builder → MetaPrompt → QA Auditor) into a single webhook call. Paste a raw idea into the web UI, get back a deployable System Prompt and a retrieval-optimized Knowledge Base file, plus a deterministic audit verdict and a tactical-correction library.

Based on the **GEM (Generative Engineering Methodology)** framework by Bryan & Daron Vener, automated for self-service execution.

---

## What you get per run

| Artifact | What it's for |
|---|---|
| **System Prompt** (.md) | Paste straight into ChatGPT → Configure → Instructions |
| **Knowledge Base** (.md) | Upload to ChatGPT → Configure → Knowledge |
| **Idea Document** | The Input-Process-Output blueprint the GPT is built from |
| **Knowledge Report** | Domain frameworks, decision criteria, quality standards |
| **Operationalized SOP** | The deterministic 8-step procedure the GPT follows |
| **Audit Verdict** | PASS/FAIL across six failure modes with line-level detail |
| **Tactical Library** | 5–10 ready-to-paste steering snippets for live sessions |

---

## How it works

```
                  ┌─────────────────────────────────────────────────────────────┐
                  │                      n8n Workflow                            │
   ┌────────┐     │                                                              │     ┌──────────┐
   │ Web UI │────▶│  Webhook ──▶ N1 ──▶ N2 ──▶ N3 ──▶ N4 ──▶ N5 ──▶ N6 ──▶ Resp │────▶│ Web UI   │
   └────────┘     │            Architect│Domain│ SOP  │ KB   │Prompt│Audit         │     │ (results)│
   raw idea       │                                                              │     └──────────┘
                  └─────────────────────────────────────────────────────────────┘
                                       single webhook call · 30–90 seconds
```

Each node has a hand-crafted system prompt enforcing strict output discipline: no token shortcuts, third-person SOP voice, deterministic tie-breaking, named domain frameworks (not "consider X"), JSON-only audit output. See [`prompts-reference.md`](./prompts-reference.md) for the full prompts.

If the auditor returns `FAIL`, the UI surfaces a course-correction box pre-filled with the auditor's recommended fix. Re-run feeds the correction into the Operationalizer and downstream nodes. Loop until `PASS`, then ship.

---

## Quick start

Full instructions in [**SETUP.md**](./SETUP.md). The condensed version:

1. **API key** — grab a free Gemini key from [Google AI Studio](https://aistudio.google.com/apikey). No credit card required; 1,500 requests/day free tier covers ~250 full pipeline runs/day.
2. **n8n** — either [n8n Cloud](https://n8n.io) (14-day trial) or self-host via `npx n8n`.
3. **Credential** — in n8n, create a Header Auth credential named exactly `Gemini API Key`, header `Authorization`, value `Bearer YOUR_KEY`.
4. **Import** — open `gem-pipeline.json` from this repo into n8n. Activate the workflow.
5. **UI** — open `index.html` in any browser, paste your webhook URL, paste your idea, click run.

---

## Provider portability

The workflow uses generic HTTP Request nodes, not provider-specific n8n integrations. Default model is **Gemini 2.5 Flash** via Google AI Studio's OpenAI-compatible endpoint. To swap:

| Provider | URL | Auth header | Body change |
|---|---|---|---|
| **Gemini** (default) | `generativelanguage.googleapis.com/v1beta/openai/chat/completions` | `Authorization: Bearer ...` | — |
| **OpenAI** | `api.openai.com/v1/chat/completions` | `Authorization: Bearer ...` | — |
| **Anthropic** | `api.anthropic.com/v1/messages` | `x-api-key: ...` + `anthropic-version: 2023-06-01` | Move `system` field out of `messages` to top level; change response parse to `content[0].text` |

The six system prompts themselves are model-agnostic.

---

## Repo structure

```
.
├── README.md              ← you are here
├── SETUP.md               ← step-by-step setup
├── LICENSE                ← MIT
├── gem-pipeline.json      ← n8n workflow — import this
├── index.html             ← web UI — open in any browser
├── prompts-reference.md   ← all six node prompts in readable form
└── build_workflow.py      ← regenerates gem-pipeline.json from the prompts
```

To edit prompts and regenerate the workflow: edit the `NODE_N_SYSTEM` strings in `build_workflow.py`, then run `python3 build_workflow.py`. (Or edit the prompts directly in the n8n UI on each HTTP node's body.)

---

## Acknowledgments

The conceptual framework — Master Systems Architect, the 8-step Operationalization process, the QA Audit protocol, the Tactical Prompting Library — is the work of **Bryan and Daron Vener**, captured in their two GEM documents on Custom GPT construction. This repository automates that process; it does not invent it.

---

## License

[MIT](./LICENSE).
