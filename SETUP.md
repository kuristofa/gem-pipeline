# GEM Pipeline — Setup

Time to first working pipeline: ~15 minutes.

What you'll have at the end: a webhook you POST to with a raw idea, and a web UI that returns a System Prompt + Knowledge Base file ready to paste into a Custom GPT's Configure tab.

The pipeline defaults to **Claude Sonnet 4.6** per the GEM specification's "GPT-4o / Claude 3.5" recommendation. Sonnet 4.6 is the current Sonnet-tier model in Anthropic's lineup and is the direct lineage successor to Claude 3.5.

---

## 1 — Prerequisites

You need:

- **An Anthropic API key.** Sign up at `https://console.anthropic.com`. Add at least $5 of prepaid credits. The pipeline does 6 Claude Sonnet 4.6 calls per run; each full run costs roughly $0.25–$0.40 depending on output length. $5 covers ~15–20 full runs — enough to validate the pipeline and iterate.
- **An n8n instance.** Two paths:
  - **n8n Cloud** (easiest) — sign up at `https://n8n.io`, 14-day free trial. No install.
  - **Self-hosted** — `npx n8n` on your machine (requires Node.js 20+), or Docker: `docker run -it --rm -p 5678:5678 n8nio/n8n`. Open `http://localhost:5678`.

---

## 2 — Get the Anthropic API key

1. Open `https://console.anthropic.com` and sign in.
2. In the left sidebar, click **Plans & Billing**.
3. Add a payment method, then click **Buy credits** and load $5 (the minimum).
4. In the left sidebar, click **API keys**.
5. Click **Create Key** → name it `n8n-gem-pipeline` (for your bookkeeping only) → Permission: Full access → **Create**.
6. The key (`sk-ant-...`, ~100 characters) appears once. **Copy it immediately and store it somewhere safe.** Anthropic does not show it again.

---

## 3 — Add your Anthropic credential to n8n

The workflow uses **Header Auth** to authenticate, sending the key as the `x-api-key` header (Anthropic's required header name).

1. In n8n, open **Credentials** in the sidebar.
2. Click **+ Add credential** (or **Create Credential**).
3. Choose **Header Auth**.
4. Set:
   - **Credential Name:** `Anthropic API Key`
   - **Name** (the HTTP header name): `x-api-key`
   - **Value** (the HTTP header value): your full `sk-ant-...` key — **no `Bearer` prefix**, no quotes, no leading or trailing whitespace.
5. Save.

> The credential name must be exactly `Anthropic API Key`. The workflow JSON looks up the credential by that name on import to auto-link all six HTTP nodes. A different name means you'd have to link each of the six nodes manually.
>
> The `anthropic-version: 2023-06-01` header is set inside each HTTP node in the workflow itself — you do not add it to the credential. Anthropic's Header Auth via n8n only supports one header value (the `x-api-key`); other static headers live in the node config.

---

## 4 — Import the workflow

1. In n8n, open **Workflows → New**, or click **+ Add workflow** on the Overview page.
2. In the new workflow editor, click the **⋮** menu in the top-right.
3. Choose **Import from File**.
4. Select **`gem-pipeline.json`** from this repository.
5. After a moment, 15 nodes appear in a horizontal chain — starting with **Webhook In** on the left, ending with **Respond** on the right.

### Verify the credential is linked

Double-click **N1 · Architect** (the third node from the left, first one with a globe icon). In the right-side panel:

- **Authentication:** Generic Credential Type
- **Generic Auth Type:** Header Auth
- **Credential for Header Auth:** **Anthropic API Key**

If the credential dropdown shows red or empty, click it and pick **Anthropic API Key** from the list. Repeat for N2 through N6 if needed (you typically only need to do this on one node if you named the credential correctly — the others auto-link).

Also confirm the **URL** field shows `https://api.anthropic.com/v1/messages`.

---

## 5 — Publish and copy the webhook URL

1. Click **Publish** in the top-right (some n8n versions show this as "Active" — same concept).
2. Give the version a name like `v1.0 — claude sonnet 4.6` and confirm.
3. Click the **Webhook In** node.
4. Two URLs appear: **Test URL** and **Production URL**. Copy the **Production URL** (it looks like `https://your-instance.app.n8n.cloud/webhook/gem-pipeline` or `http://localhost:5678/webhook/gem-pipeline`).

> Use **Production**, not Test. The Test URL only listens for a single call while you're actively viewing the workflow; the Production URL stays on as long as the workflow is published.

---

## 6 — Open the web UI

1. Open **`index.html`** in any modern browser. Easiest: double-click the file in your file explorer.
2. Paste the **Production webhook URL** into field 01. (Saved locally on the device for next time.)
3. Type your raw idea into field 02. For example:

   > A GPT that takes a startup's landing page URL and returns a structured critique scoring clarity, value proposition strength, social proof, and CTA effectiveness on a 0–10 scale, with specific rewrite suggestions for each section.

4. (Optional) System context in field 03 — only if this GPT is part of a multi-GPT chain.
5. **Run pipeline →**.

The pipeline visualization pulses while running (expect 40–80 seconds with Sonnet 4.6). When complete, the verdict banner shows PASS or FAIL, then sections expand for System Prompt, Knowledge Base, audit detail, and the Tactical Library.

---

## 7 — Ship the Custom GPT

In ChatGPT:

1. **Create a GPT** → **Configure** tab.
2. **Name:** copy the GPT name from the UI's verdict header.
3. **Instructions:** paste the **System Prompt** (Section B in the UI). Use the **Copy** button.
4. **Knowledge:** click **Upload files**, attach the downloaded **Knowledge Base** .md (Section C → **Download .md**).
5. Save. Test with sample inputs.

---

## 8 — What to do if the audit FAILs

The auditor checks for six failure modes: missed constraints, strategic drift, token shortcuts, forbidden second-person voice, broken KB references, and I/O mismatches. If any fail, the UI surfaces a **Course correction** box pre-filled with the auditor's recommended fix text.

1. Read the failing checks under **Audit Detail** (Section D).
2. Edit the correction text if needed.
3. **Re-run with corrections →** — the pipeline re-runs end-to-end with your correction injected into the Operationalizer and downstream nodes.

Run the loop until verdict = PASS, then ship.

---

## 9 — The Tactical Library

Section E contains 5–10 short steering snippets you paste into a live ChatGPT session **if the deployed GPT starts drifting from its SOP**. Each one has a `use_when` trigger and the exact text to paste. Keep this file handy after you launch the GPT — drift is the most common failure mode in long sessions, and the library is the fastest way to re-anchor.

---

## Troubleshooting

**"Webhook not registered"** — the workflow isn't published. Click Publish, then retry. The Test URL only fires once; you want the Production URL.

**HTTP 401 / 403 from Anthropic** — the API key is wrong, the credential value has an accidental `Bearer ` prefix (Anthropic does not use one), or the header name is misspelled (must be exactly `x-api-key`, lowercase, with the hyphen). Open the credential, double-check all three fields, save.

**HTTP 400 from Anthropic with "max_tokens"** — extremely unusual since the workflow sends `max_tokens` on every call, but if it appears, check N3 / N4 / N5 — they're set to 8192. Anthropic's Sonnet 4.6 supports much more than that, so it's a body-structure issue, not a limit issue.

**Audit returns `verdict: PARSE_ERROR`** — N6 emitted something other than pure JSON (probably wrapped its output in markdown code fences or added a preamble). The defensive parser strips fences and extracts the largest JSON object it can find, but unusual variants slip through occasionally. Open the Parse N6 node in n8n and inspect the `audit_raw` field to see exactly what came back, then either tune the N6 system prompt or extend the defensive parser regex.

**"Maximum execution time exceeded" on self-hosted n8n** — n8n's default execution timeout in self-hosted mode is 120s, which can be tight for 6 sequential Sonnet 4.6 calls. Set `EXECUTIONS_TIMEOUT=300` in the environment before starting n8n.

**Want to swap models** — every HTTP node in the workflow has a `model` value inside its JSON body. Current default is `claude-sonnet-4-6` (balanced cost/quality, spec-compliant). Swap to `claude-opus-4-7` per node for higher quality on the heavier nodes (N3 Operationalizer, N4 KB Builder, N5 MetaPrompt) — roughly 1.7× the cost but markedly better on long reasoning. Or `claude-haiku-4-5` for cheaper drafting.

**Want to swap providers entirely** — see the Provider portability table in the README. Each provider needs different URL, auth header, body schema, and response parse path. The six system prompts themselves are model-agnostic.

---

## File map

```
gem-pipeline.json     → import into n8n
index.html            → open in browser; talks to the webhook
prompts-reference.md  → human-readable copy of all six node prompts (edit in n8n)
build_workflow.py     → regenerates gem-pipeline.json from the embedded prompts
SETUP.md              → this file
README.md             → project front door
LICENSE               → MIT
```
