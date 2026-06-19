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
                                       single webhook call · 40–80 seconds
```

Each node has a hand-crafted system prompt enforcing strict output discipline: no token shortcuts, third-person SOP voice, deterministic tie-breaking, named domain frameworks (not "consider X"), JSON-only audit output. See [`prompts-reference.md`](./prompts-reference.md) for the full prompts.

If the auditor returns `FAIL`, the UI surfaces a course-correction box pre-filled with the auditor's recommended fix. Re-run feeds the correction into the Operationalizer and downstream nodes. Loop until `PASS`, then ship.

---

## Quick start

Full instructions in [**SETUP.md**](./SETUP.md). The condensed version:

1. **API key** — sign up at [Anthropic Console](https://console.anthropic.com), add ~$5 of prepaid credits, generate an API key. Per the GEM spec, the pipeline targets **Claude Sonnet 4.6** (modern equivalent of the spec's "Claude 3.5" recommendation). Each full pipeline run costs roughly $0.30.
2. **n8n** — either [n8n Cloud](https://n8n.io) (14-day trial) or self-host via `npx n8n`.
3. **Credential** — in n8n, create a Header Auth credential named exactly `Anthropic API Key`, header `x-api-key`, value `sk-ant-...` (no `Bearer` prefix).
4. **Import** — open `gem-pipeline.json` from this repo into n8n. Publish the workflow.
5. **UI** — open `index.html` in any browser, paste your webhook URL, paste your idea, click run.

---

## Provider portability

The GEM specification recommends **GPT-4o or Claude 3.5** as the LLM backbone. This repository defaults to **Claude Sonnet 4.6** (current Sonnet generation). The workflow uses generic HTTP Request nodes rather than provider-specific n8n integrations, so swapping providers requires changing only the URL, the auth header, and a couple of body/parse fields.

| Provider | URL | Auth header | Body change | Response field |
|---|---|---|---|---|
| **Anthropic** (default, spec-compliant) | `api.anthropic.com/v1/messages` | `x-api-key: ...` + `anthropic-version: 2023-06-01` | `system` as top-level field; `max_tokens` required | `content[0].text` |
| **OpenAI** (spec-compliant alternative) | `api.openai.com/v1/chat/completions` | `Authorization: Bearer ...` | `system` as message in `messages` array | `choices[0].message.content` |
| **Gemini** (free tier, fallback for testing) | `generativelanguage.googleapis.com/v1beta/openai/chat/completions` | `Authorization: Bearer ...` | OpenAI-compatible; add `reasoning_effort: "none"` for Gemini 2.5 Flash | `choices[0].message.content` |

The six system prompts themselves are model-agnostic. Edit them in `build_workflow.py` (variables `NODE_1_SYSTEM` through `NODE_6_SYSTEM`) and rerun the script to regenerate the workflow JSON.

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

To edit prompts and regenerate the workflow: edit the `NODE_N_SYSTEM` strings in `build_workflow.py`, then run `python3 build_workflow.py`. Or edit the prompts directly in the n8n UI on each HTTP node's body.

---

## Acknowledgments

The conceptual framework — Master Systems Architect, the 8-step Operationalization process, the QA Audit protocol, the Tactical Prompting Library — is the work of **Bryan and Daron Vener**, captured in their two GEM documents on Custom GPT construction. This repository automates that process; it does not invent it.

---

## License

[MIT](./LICENSE).
