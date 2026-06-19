# GEM Pipeline — Setup

Time to first working pipeline: ~15 minutes.

What you'll have at the end: a webhook you POST to with a raw idea, and a web UI that returns a System Prompt + Knowledge Base file ready to paste into a Custom GPT's Configure tab.

---

## 1 — Prerequisites

You need:

- **A Google account** for the API key (any Gmail account works). The pipeline uses **Gemini 2.5 Flash** via Google AI Studio's free tier.
- **Free tier limits:** 1,500 requests/day, 15 requests/minute. The pipeline uses 6 requests per run, so the daily ceiling is ~250 full pipeline runs. No credit card required.
- **An n8n instance.** Two paths:
  - **n8n Cloud** (easiest) — sign up at `https://n8n.io`, 14-day free trial. No install.
  - **Self-hosted** — `npx n8n` on your machine, or Docker: `docker run -it --rm -p 5678:5678 n8nio/n8n`. Open `http://localhost:5678`.

---

## 2 — Get the Gemini API key

1. Open `https://aistudio.google.com/apikey` in your browser.
2. Sign in with your Google account.
3. Click **Create API key** → **Create API key in new project** (or pick an existing project).
4. A key like `AIza...` appears — copy it immediately. (Google shows it again later under the same page, but copy it now to be safe.)

---

## 3 — Add your Gemini credential to n8n

The workflow uses **Header Auth** to call Gemini's OpenAI-compatible endpoint. Same provider-agnostic pattern — swap key + URL later if you want to switch to Claude or GPT.

1. In n8n, open **Settings → Credentials → New** (or click the **+** in the sidebar and pick **Credential**).
2. Choose **Header Auth**.
3. Set:
   - **Credential Name:** `Gemini API Key`
   - **Name (the header name):** `Authorization`
   - **Value:** `Bearer YOUR_KEY` — replace `YOUR_KEY` with your actual `AIza...` key. **Include the word `Bearer` and one space before the key.** Example: `Bearer AIzaSyD...XYZ`
4. Save.

> Note the credential name exactly — `Gemini API Key`. If you rename it, you'll need to re-link each HTTP node manually after import.

---

## 4 — Import the workflow

1. In n8n, open **Workflows → New**, then click the **⋮** menu top-right → **Import from File**.
2. Select **`gem-pipeline.json`** (the file shared with this setup).
3. The workflow loads with 15 nodes in a horizontal chain.

### Re-link the credential

On import, each HTTP Request node may show a red badge ("Credentials missing"). For each of the six nodes named `N1 · Architect` through `N6 · QA Auditor`:

1. Click the node.
2. Under **Authentication**, confirm it's set to **Generic Credential Type → Header Auth**.
3. Under **Credential for Header Auth**, pick your `OpenAI Auth Header`.
4. Close.

(If you named your credential exactly `OpenAI Auth Header` before importing, this step is often automatic.)

---

## 5 — Activate and copy the webhook URL

1. Click the **Webhook In** node (first node).
2. Toggle **Active** in the top-right of the workflow editor.
3. In the Webhook node, copy the **Production URL** (looks like `https://your-instance.app.n8n.cloud/webhook/gem-pipeline` or `http://localhost:5678/webhook/gem-pipeline`).

> n8n distinguishes **Test URL** (only listens for one call, used while editing) from **Production URL** (always-on, used after activation). Use the Production URL in the web UI.

---

## 6 — Open the web UI

1. Open **`index.html`** in any modern browser. Easiest: double-click the file.
2. Paste the **Production webhook URL** into field 01.
3. Type your raw idea into field 02. Example:
   > A GPT that takes a startup's landing page URL and returns a structured critique scoring clarity, value proposition strength, social proof, and CTA effectiveness on a 0–10 scale, with specific rewrite suggestions for each section.
4. (Optional) System context in field 03 — only if this GPT is part of a multi-GPT chain.
5. **Run pipeline →**

The pipeline visualization pulses while running (expect 30–90 seconds). When complete, the verdict banner shows PASS or FAIL, then sections for System Prompt, Knowledge Base, audit detail, and the Tactical Library.

---

## 7 — Ship the Custom GPT

In ChatGPT:

1. **Create a GPT** → **Configure** tab.
2. **Name:** copy the GPT Name from the verdict header.
3. **Instructions:** paste the **System Prompt** (Section B in the UI). Use the **Copy** button.
4. **Knowledge:** click **Upload files**, attach the downloaded **Knowledge Base** .md (Section C → **Download .md**).
5. Save. Test with sample inputs.

---

## 8 — What to do if the audit FAILs

The auditor checks for six failure modes: missed constraints, strategic drift, token shortcuts, forbidden second-person voice, broken KB references, and I/O mismatches. If any fail, the UI shows a **Course correction** box pre-filled with the auditor's suggested correction text.

1. Read the failing checks under **Audit Detail** (Section D).
2. Edit the correction text if needed.
3. **Re-run with corrections →** — this re-runs the entire pipeline, with your corrections injected into the Operationalizer (Node 3) and downstream.

Run the loop until verdict = PASS, then ship.

---

## 9 — The Tactical Library

Section E contains 5–10 short steering snippets you paste into a live ChatGPT session **if the deployed GPT starts drifting from its SOP**. Each one has a `use_when` trigger and the exact text to paste. Keep this file handy after you launch the GPT — drift is the most common failure mode in long sessions, and the library is the fastest way to re-anchor.

---

## Troubleshooting

**"Webhook not registered"** — the workflow isn't active. Toggle Active in the workflow editor, then retry. (The test URL only fires once; you want the production URL.)

**HTTP 401 / 403 from Gemini** — the API key is wrong, the `Bearer ` prefix is missing from the credential value, or the header name is misspelled (must be exactly `Authorization`, capital A). Edit the credential.

**Audit returns valid PASS but `audit` field is empty in the UI** — the QA auditor wrapped its JSON in code fences. Open the Parse N6 node in n8n and check the `audit` expression; the regex strips ` ```json ` fences but new variants may slip through.

**"Maximum execution time exceeded"** — n8n's default execution timeout (in self-hosted) is 120s, which is tight for 6 GPT-4o calls. Set `EXECUTIONS_TIMEOUT=300` in your n8n environment.

**Want to swap models** — every HTTP node has a `model` value inside its JSON body. Current default is `gemini-2.5-flash` (free tier). Swap to `gemini-2.5-pro` for higher reasoning quality (uses the same key but counts against the paid tier's quota if you're outside free limits).

**Want to upgrade to Claude or GPT later** — change `url` and the credential header (Anthropic needs `x-api-key` plus an `anthropic-version: 2023-06-01` header; OpenAI keeps `Authorization: Bearer ...`). For Anthropic also move the `system` field out of the messages array to the top level, and parse `content[0].text` instead of `choices[0].message.content`. The prompts themselves are model-agnostic.

---

## File map

```
gem-pipeline.json     → import into n8n
index.html            → open in browser; talks to the webhook
prompts-reference.md  → human-readable copy of all six node prompts (edit in n8n)
SETUP.md              → this file
```
