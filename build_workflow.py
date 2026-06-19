#!/usr/bin/env python3
"""Build the n8n workflow JSON for the GEM Pipeline.

Generates `gem-pipeline.json` ready to import into n8n.

The workflow:
  Webhook → Initial Setup → 
    Node 1 Architect → Parse 1 → 
    Node 2 Domain   → Parse 2 → 
    Node 3 SOP      → Parse 3 → 
    Node 4 KB       → Parse 4 → 
    Node 5 Prompt   → Parse 5 → 
    Node 6 Audit    → Parse 6 → 
    Respond
"""

import json
import uuid
from textwrap import dedent

# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPTS (kept here so escaping is handled by json.dumps)
# ─────────────────────────────────────────────────────────────────────────────

NODE_1_SYSTEM = dedent("""\
    You are a Master Systems Architect and AI Operations Engineer. You apply strict Systems Thinking (the Input-Process-Output model) to clarify a raw idea into a precise operational blueprint for Custom GPT construction.

    You treat each GPT as a highly focused operational node. If a System Context is provided, do not assign the GPT tasks that belong to other nodes in that system. If the GPT is standalone, ensure it is fully self-sufficient.

    You produce exactly two artifacts and nothing else.

    PART A — IDEA DOCUMENT (use this exact structure and headings):

    Target GPT: [Name of GPT]
    Core Role: [1-2 sentences defining its exact operational purpose]
    Main Job (Processing):
    - [Actionable task 1]
    - [Actionable task 2]
    - [Internal logic, frameworks, or decisions it must apply]
    Inputs (Upstream Dependencies):
    - [Exactly what data/variables it receives from the user or the previous system node]
    Outputs (Downstream Deliverables):
    - [Exactly what it must produce, including specific formatting, tables, or data structures]
    Guardrails & Constraints:
    - [What it MUST NOT do]
    - [Limits on length, tone, or format]

    PART B — PURPOSE STATEMENT (one sentence, this exact template):

    "I want to create a Custom GPT that does [XYZ] to produce [Output] within [Constraints] in order to [Goal]."

    OUTPUT RULES (absolute):
    - No conversational preamble.
    - No closing remarks or meta-commentary.
    - Begin immediately with the line "Target GPT:".
    - Separate Part A and Part B with the exact delimiter line: ---PURPOSE---
    - Do not wrap the output in code fences.
""")

NODE_2_SYSTEM = dedent("""\
    You produce a Knowledge Report analyzing the domain of an AI Assistant's purpose statement. You operate in two phases.

    PHASE 1 — EXPERT DOMAIN RESOURCES
    Map the premier methodologies, frameworks, and expert practices in the field. Cover:
    - Industry-standard frameworks (name them specifically).
    - Proven expert workflows.
    - Best-in-class tools and approaches.
    - Established quality benchmarks.

    PHASE 2 — AI-EXECUTABLE STRATEGY
    From Phase 1, extract ONLY the intellectual components that add value beyond basic LLM capabilities:
    - Strategic frameworks that guide decision-making.
    - Domain-specific analytical methods.
    - Expert heuristics and rules of thumb.
    - Quality standards specific to the field.

    You EXCLUDE general LLM capabilities such as language understanding, conversation management, or basic logical reasoning.

    OUTPUT FORMAT (Markdown, these exact sections, in this order):

    # Knowledge Report: [GPT Name]

    ## 1. Core Domain Knowledge
    ### Critical principles unique to this field
    ### Expert-level decision criteria
    ### Field-specific evaluation methods

    ## 2. Strategic Process
    ### Key decision points and their triggers
    ### Essential domain questions to consider
    ### Critical success factors

    ## 3. Quality Standards
    ### Domain-specific benchmarks
    ### Industry-standard quality indicators
    ### Field-recognized best practices

    OUTPUT RULES (absolute):
    - No preamble. Begin with "# Knowledge Report:".
    - No closing remarks.
    - Every bullet is field-specific and concrete. Generic AI advice is forbidden.
    - Name frameworks explicitly (e.g., "Cynefin", "Wardley Mapping", "Jobs-To-Be-Done"), not generically ("a framework for thinking").
    - Do not wrap the output in code fences.
""")

NODE_3_SYSTEM = dedent("""\
    You are the Operationalizer. You transform a Knowledge Report into an executable, machine-ready Standard Operating Procedure (SOP) for a Custom GPT.

    You execute an 8-step process IN ORDER, fully completing each step before moving to the next. You output ALL EIGHT STEPS in a single response. You do not skip steps. You do not compress. You do not truncate.

    THE EIGHT STEPS:

    ## STEP 1 — Process Decomposition
    Break the GPT's main job into discrete, sequenced sub-processes. For each sub-process state: trigger, input, transformation, output.

    ## STEP 2 — Input/Output Schema
    For each sub-process, define the exact data shape: fields, types, required vs optional, formats, valid value ranges.

    ## STEP 3 — Decision Logic and Branching
    Specify every conditional in deterministic form: "If [condition], then [action]; else [alternate action]." Forbidden words in this step: "consider", "may", "might", "could", "as appropriate".

    ## STEP 4 — Domain Frameworks Embedded
    For each decision point in Step 3, name the specific framework, heuristic, or quality benchmark from the Knowledge Report being applied. Embed the framework's rule set inline. Do not reference it by name only.

    ## STEP 5 — Quality Validation Criteria
    For each output defined in Step 2, list the deterministic checks that must pass before the GPT emits it. Include: format checks, semantic checks, constraint checks, length checks.

    ## STEP 6 — Edge Case Handling
    Enumerate predictable edge cases (empty input, ambiguous input, conflicting input, out-of-scope input, malformed input, hostile input) and the deterministic response to each.

    ## STEP 7 — Deterministic Tie-Breaking and Selection Rules
    When multiple candidate outputs satisfy all validation, specify the deterministic selection rule. Default rule unless context dictates otherwise: "Select the shortest candidate that preserves 100% of intent and satisfies all safety validation."

    ## STEP 8 — Master Operationalized Process (Final SOP)
    Consolidate Steps 1–7 into a single, formal, third-person SOP document. This is the final deliverable. It MUST:
    - Read as a Standard Operating Procedure manual for a machine.
    - Use third-person declarative voice ("The system parses...", "The process selects...", "The assistant validates...").
    - Number all procedures (1.0, 1.1, 1.2, 2.0, ...).
    - Include every constraint, framework, rule, and edge case defined in Steps 1–7 in full.

    The Step 8 SOP MUST NOT:
    - Use second-person "you" language.
    - Use system-prompt phrasing such as "You are an AI" or "Your role is".
    - Summarize, compress, or truncate Steps 1–7.
    - Refer to earlier steps by step number (the SOP must stand alone).

    OUTPUT RULES (absolute):
    - Output all 8 steps, in order, in a single response.
    - Fully complete Step 7 before beginning Step 8.
    - No preamble. Begin with "## STEP 1 — Process Decomposition".
    - No closing remarks after Step 8.
    - Do not wrap the output in code fences.
""")

NODE_4_SYSTEM = dedent("""\
    You are the Knowledge Base Master Builder. You transform a Purpose Statement, Knowledge Report, and Operationalized Process (SOP) into a single Knowledge Base file optimized for retrieval by a Custom GPT.

    Your optimization objective is INFORMATION DENSITY: Accuracy ÷ Length. Every sentence must carry retrievable signal. Filler is forbidden.

    PROCESSING RULES:
    - Regroup information semantically by theme and action, not by source document.
    - Use Markdown headings (##, ###) so the GPT can navigate by section.
    - For each domain-specific term the GPT will encounter, include a one-line definition.
    - Embed INSTRUCTION TRIGGERS: explicit lines stating "When [trigger], retrieve [section]." This tells the GPT precisely when to pull a section into context.
    - Use bullet lists for enumerable rules.
    - Use Markdown tables for comparative or schema information.
    - No prose paragraph exceeds 3 sentences.

    OUTPUT FORMAT:

    # Knowledge Base: [GPT Name]

    ## Retrieval Triggers
    A table mapping user-input triggers to KB sections.

    | Trigger | Retrieve Section |
    |---------|------------------|
    | ... | ## ... |

    ## Core Definitions
    Every domain-specific term, one line each.

    ## Domain Frameworks
    Each framework as a named ### subsection containing: Purpose · When to apply · Steps · Success criteria.

    ## Decision Rules
    Deterministic if/then rules extracted from the SOP.

    ## Quality Standards
    The validation criteria the GPT applies to its own outputs.

    ## Edge Case Playbook
    Each edge case with its deterministic response.

    OUTPUT RULES (absolute):
    - No preamble. Begin with "# Knowledge Base:".
    - Markdown only. No code fences wrapping the whole document.
    - Dense, retrieval-optimized prose. No marketing tone. No conversational tone.
    - Do not include the SOP verbatim. Restructure semantically.
""")

NODE_5_SYSTEM = dedent("""\
    You are the MetaPrompt Synthesizer. You produce the final System Prompt for a Custom GPT, ready to paste into the GPT's "Instructions" field in the Configure tab.

    You follow this exact template. You fill every section. You leave no placeholders.

    # [NAME_OF_AI_ASSISTANT]

    ## Identity
    [Concise statement of what this assistant is, directed at the model.]

    ## Objective
    [The single specific outcome this assistant must produce.]

    ## Workflow
    The assistant follows this workflow on every invocation:
    1. ...
    2. ...
    3. ...
    (Continue with every step from the SOP.)

    ## Domain Frameworks
    The assistant applies the following frameworks. For each, the assistant retrieves the corresponding section from its attached Knowledge Base file when the trigger fires:
    - [Framework name] — When [trigger], retrieve "## [section]" from the attached Knowledge Base.

    ## Knowledge Base Retrieval Rules
    The assistant retrieves from its attached Knowledge Base file according to these rules:
    - When the user input matches [pattern], retrieve [section].

    ## Decision Rules
    [Every deterministic if/then rule from the SOP, in declarative form.]

    ## Quality Standards
    Before emitting any output, the assistant verifies:
    - ...

    ## Edge Case Handling
    - If [edge case], the assistant [response].

    ## Constraints
    The assistant MUST NOT:
    - ...

    ## Output Format
    [The exact format of the assistant's deliverable, with schema or example.]

    OUTPUT RULES (absolute):
    - Output ONLY the populated System Prompt, beginning with "# [Name]".
    - No preamble, no closing remarks, no meta-commentary about your process.
    - Fill every section. Do not leave bracketed placeholders.
    - Reference the Knowledge Base as "your attached Knowledge Base file" (the user uploads the .md in the Configure tab).
    - Do not wrap output in code fences.
""")

NODE_6_SYSTEM = dedent("""\
    You are the QA Auditor. You verify that the final System Prompt and SOP satisfy the original Idea/Constraints. You produce a structured audit verdict in JSON.

    CHECKS TO PERFORM:

    1. CONSTRAINT COVERAGE
    For each item in the Idea Document's "Guardrails & Constraints" section, verify it appears semantically in the System Prompt's Constraints section. List any missing constraints verbatim.

    2. STRATEGIC DRIFT
    Compare the System Prompt's Objective and Workflow to the Purpose Statement. Flag scope, output, or intent drift.

    3. TOKEN SHORTCUTS
    Inspect the SOP for compression artifacts: "etc.", "and so on", "...", "as needed", "various", vague references to "the framework" or "the process" without naming it. Flag every instance with quoted text.

    4. FORBIDDEN FORMAT
    Verify the SOP uses third-person SOP voice. Flag any "You are an AI", "Your role is", or second-person system-prompt phrasing in the SOP.

    5. INTERNAL CONSISTENCY
    Verify that every section referenced in the System Prompt's "Knowledge Base Retrieval Rules" actually exists as a heading in the Knowledge Base.

    6. INPUT/OUTPUT FAITHFULNESS
    Verify the System Prompt's "Output Format" matches the "Outputs (Downstream Deliverables)" section of the Idea Document.

    OUTPUT (JSON only — no prose, no markdown fences, no commentary):

    {
      "verdict": "PASS" or "FAIL",
      "checks": {
        "constraint_coverage": { "status": "PASS or FAIL", "missing": [] },
        "strategic_drift": { "status": "PASS or FAIL", "drifts": [] },
        "token_shortcuts": { "status": "PASS or FAIL", "instances": [] },
        "forbidden_format": { "status": "PASS or FAIL", "instances": [] },
        "internal_consistency": { "status": "PASS or FAIL", "broken_references": [] },
        "io_faithfulness": { "status": "PASS or FAIL", "mismatches": [] }
      },
      "course_correction_prompt": "",
      "tactical_library": [
        { "tactic": "", "use_when": "", "snippet": "" }
      ]
    }

    RULES:
    - Output ONLY valid JSON. No code fences. No leading or trailing text.
    - verdict is "FAIL" if any check status is "FAIL".
    - course_correction_prompt: the exact text the user would send back to the Operationalizer to fix all failed checks. Empty string if verdict is PASS.
    - tactical_library: 5 to 10 short steering snippets the user pastes mid-session if the deployed GPT drifts. Each tactic has: a short label, a use_when trigger, and the exact snippet text.
""")

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def nid():
    """Generate an n8n-style node id."""
    return str(uuid.uuid4())


def http_gemini_node(name: str, position: list, system_prompt: str,
                     user_prompt_expr: str, temperature: float = 0.2,
                     model: str = "gemini-2.5-flash", max_tokens: int = 4096) -> dict:
    """Build an HTTP Request node that calls Gemini's OpenAI-compatible endpoint.

    Uses Google AI Studio's OpenAI-compatibility layer at
    https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
    which accepts standard OpenAI chat-completion request bodies.
    """
    sys_js = json.dumps(system_prompt)
    body_expr = (
        "={{ JSON.stringify({"
        f' "model": "{model}",'
        f' "temperature": {temperature},'
        f' "max_tokens": {max_tokens},'
        ' "messages": ['
        f'   {{ "role": "system", "content": {sys_js} }},'
        f'   {{ "role": "user", "content": {user_prompt_expr} }}'
        ' ]'
        "}) }}"
    )
    return {
        "parameters": {
            "method": "POST",
            "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "Content-Type", "value": "application/json"}
                ]
            },
            "sendBody": True,
            "contentType": "json",
            "specifyBody": "json",
            "jsonBody": body_expr,
            "options": {
                "response": {
                    "response": {
                        "responseFormat": "json"
                    }
                },
                "timeout": 180000
            }
        },
        "id": nid(),
        "name": name,
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": position,
        "credentials": {
            "httpHeaderAuth": {
                "id": "REPLACE_WITH_YOUR_CREDENTIAL_ID",
                "name": "Gemini API Key"
            }
        }
    }


def set_node(name: str, position: list, assignments: list,
             keep_only_set: bool = False) -> dict:
    """Build a Set (Edit Fields) node.

    assignments is a list of (name, value_expr, type) tuples. value_expr is an
    n8n expression string (use "=..." for expression mode, or plain string for
    literal).
    """
    values = []
    for fname, fval, ftype in assignments:
        values.append({
            "id": nid(),
            "name": fname,
            "value": fval,
            "type": ftype
        })
    return {
        "parameters": {
            "mode": "manual",
            "duplicateItem": False,
            "assignments": {
                "assignments": values
            },
            "includeOtherFields": not keep_only_set,
            "options": {}
        },
        "id": nid(),
        "name": name,
        "type": "n8n-nodes-base.set",
        "typeVersion": 3.4,
        "position": position
    }


# ─────────────────────────────────────────────────────────────────────────────
# BUILD NODES
# ─────────────────────────────────────────────────────────────────────────────

X = 0     # x coordinate (we lay out left-to-right)
Y = 300   # y coordinate (single row)
STEP = 240

nodes = []

# 1. Webhook
nodes.append({
    "parameters": {
        "httpMethod": "POST",
        "path": "gem-pipeline",
        "responseMode": "responseNode",
        "options": {
            "allowedOrigins": "*"
        }
    },
    "id": nid(),
    "name": "Webhook In",
    "type": "n8n-nodes-base.webhook",
    "typeVersion": 2,
    "position": [X, Y],
    "webhookId": str(uuid.uuid4())
})
X += STEP

# 2. Initial Setup — extract inputs from webhook body
nodes.append(set_node(
    "Initial Setup",
    [X, Y],
    [
        ("raw_idea", "={{ $json.body.raw_idea }}", "string"),
        ("system_context", "={{ $json.body.system_context || '' }}", "string"),
        ("course_correction", "={{ $json.body.course_correction || '' }}", "string"),
    ],
    keep_only_set=True,
))
X += STEP

# 3. HTTP Node 1 — Architect
user1 = (
    "`Raw Idea / Goal:\\n` + $json.raw_idea + "
    "`\\n\\nSystem Context (may be empty):\\n` + ($json.system_context || '')"
)
nodes.append(http_gemini_node("N1 · Architect", [X, Y], NODE_1_SYSTEM, user1))
X += STEP

# 4. Parse Node 1 — split idea_document and purpose_statement, extract gpt_name
nodes.append(set_node(
    "Parse N1",
    [X, Y],
    [
        ("raw_idea", "={{ $('Initial Setup').item.json.raw_idea }}", "string"),
        ("system_context", "={{ $('Initial Setup').item.json.system_context }}", "string"),
        ("course_correction", "={{ $('Initial Setup').item.json.course_correction }}", "string"),
        ("n1_raw", "={{ $json.choices[0].message.content }}", "string"),
        ("idea_document",
         "={{ $json.choices[0].message.content.split('---PURPOSE---')[0].trim() }}",
         "string"),
        ("purpose_statement",
         "={{ ($json.choices[0].message.content.split('---PURPOSE---')[1] || '').trim() }}",
         "string"),
        ("gpt_name",
         "={{ (($json.choices[0].message.content.match(/Target GPT:\\s*(.+)/) || [])[1] || 'Custom GPT').trim() }}",
         "string"),
    ],
    keep_only_set=True,
))
X += STEP

# 5. HTTP Node 2 — Domain
user2 = "`Purpose Statement:\\n` + $json.purpose_statement + `\\n\\nIdea Document (for context):\\n` + $json.idea_document"
nodes.append(http_gemini_node("N2 · Domain", [X, Y], NODE_2_SYSTEM, user2, temperature=0.3))
X += STEP

# 6. Parse Node 2
nodes.append(set_node(
    "Parse N2",
    [X, Y],
    [
        ("raw_idea", "={{ $('Parse N1').item.json.raw_idea }}", "string"),
        ("system_context", "={{ $('Parse N1').item.json.system_context }}", "string"),
        ("course_correction", "={{ $('Parse N1').item.json.course_correction }}", "string"),
        ("idea_document", "={{ $('Parse N1').item.json.idea_document }}", "string"),
        ("purpose_statement", "={{ $('Parse N1').item.json.purpose_statement }}", "string"),
        ("gpt_name", "={{ $('Parse N1').item.json.gpt_name }}", "string"),
        ("knowledge_report", "={{ $json.choices[0].message.content }}", "string"),
    ],
    keep_only_set=True,
))
X += STEP

# 7. HTTP Node 3 — Operationalizer
user3 = (
    "`Purpose Statement:\\n` + $json.purpose_statement + "
    "`\\n\\nKnowledge Report:\\n` + $json.knowledge_report + "
    "`\\n\\nIdea Document:\\n` + $json.idea_document + "
    "`\\n\\nCourse Correction (may be empty — if non-empty, integrate these corrections into the SOP):\\n` + ($json.course_correction || '')"
)
nodes.append(http_gemini_node("N3 · Operationalizer", [X, Y], NODE_3_SYSTEM, user3, max_tokens=8192))
X += STEP

# 8. Parse Node 3
nodes.append(set_node(
    "Parse N3",
    [X, Y],
    [
        ("raw_idea", "={{ $('Parse N2').item.json.raw_idea }}", "string"),
        ("system_context", "={{ $('Parse N2').item.json.system_context }}", "string"),
        ("course_correction", "={{ $('Parse N2').item.json.course_correction }}", "string"),
        ("idea_document", "={{ $('Parse N2').item.json.idea_document }}", "string"),
        ("purpose_statement", "={{ $('Parse N2').item.json.purpose_statement }}", "string"),
        ("gpt_name", "={{ $('Parse N2').item.json.gpt_name }}", "string"),
        ("knowledge_report", "={{ $('Parse N2').item.json.knowledge_report }}", "string"),
        ("sop", "={{ $json.choices[0].message.content }}", "string"),
    ],
    keep_only_set=True,
))
X += STEP

# 9. HTTP Node 4 — KB Master Builder
user4 = (
    "`Purpose Statement:\\n` + $json.purpose_statement + "
    "`\\n\\nKnowledge Report:\\n` + $json.knowledge_report + "
    "`\\n\\nOperationalized Process (SOP):\\n` + $json.sop"
)
nodes.append(http_gemini_node("N4 · KB Builder", [X, Y], NODE_4_SYSTEM, user4, max_tokens=8192))
X += STEP

# 10. Parse Node 4
nodes.append(set_node(
    "Parse N4",
    [X, Y],
    [
        ("raw_idea", "={{ $('Parse N3').item.json.raw_idea }}", "string"),
        ("system_context", "={{ $('Parse N3').item.json.system_context }}", "string"),
        ("course_correction", "={{ $('Parse N3').item.json.course_correction }}", "string"),
        ("idea_document", "={{ $('Parse N3').item.json.idea_document }}", "string"),
        ("purpose_statement", "={{ $('Parse N3').item.json.purpose_statement }}", "string"),
        ("gpt_name", "={{ $('Parse N3').item.json.gpt_name }}", "string"),
        ("knowledge_report", "={{ $('Parse N3').item.json.knowledge_report }}", "string"),
        ("sop", "={{ $('Parse N3').item.json.sop }}", "string"),
        ("kb_file", "={{ $json.choices[0].message.content }}", "string"),
    ],
    keep_only_set=True,
))
X += STEP

# 11. HTTP Node 5 — MetaPrompt
user5 = (
    "`GPT Name (use exactly):\\n` + $json.gpt_name + "
    "`\\n\\nPurpose Statement:\\n` + $json.purpose_statement + "
    "`\\n\\nIdea Document:\\n` + $json.idea_document + "
    "`\\n\\nOperationalized Process (SOP):\\n` + $json.sop + "
    "`\\n\\nKnowledge Base (for retrieval rule alignment):\\n` + $json.kb_file"
)
nodes.append(http_gemini_node("N5 · MetaPrompt", [X, Y], NODE_5_SYSTEM, user5, max_tokens=8192))
X += STEP

# 12. Parse Node 5
nodes.append(set_node(
    "Parse N5",
    [X, Y],
    [
        ("raw_idea", "={{ $('Parse N4').item.json.raw_idea }}", "string"),
        ("system_context", "={{ $('Parse N4').item.json.system_context }}", "string"),
        ("course_correction", "={{ $('Parse N4').item.json.course_correction }}", "string"),
        ("idea_document", "={{ $('Parse N4').item.json.idea_document }}", "string"),
        ("purpose_statement", "={{ $('Parse N4').item.json.purpose_statement }}", "string"),
        ("gpt_name", "={{ $('Parse N4').item.json.gpt_name }}", "string"),
        ("knowledge_report", "={{ $('Parse N4').item.json.knowledge_report }}", "string"),
        ("sop", "={{ $('Parse N4').item.json.sop }}", "string"),
        ("kb_file", "={{ $('Parse N4').item.json.kb_file }}", "string"),
        ("system_prompt", "={{ $json.choices[0].message.content }}", "string"),
    ],
    keep_only_set=True,
))
X += STEP

# 13. HTTP Node 6 — QA Auditor
user6 = (
    "`Idea Document:\\n` + $json.idea_document + "
    "`\\n\\nPurpose Statement:\\n` + $json.purpose_statement + "
    "`\\n\\nOperationalized Process (SOP):\\n` + $json.sop + "
    "`\\n\\nKnowledge Base:\\n` + $json.kb_file + "
    "`\\n\\nSystem Prompt:\\n` + $json.system_prompt"
)
nodes.append(http_gemini_node("N6 · QA Auditor", [X, Y], NODE_6_SYSTEM, user6, temperature=0.0, max_tokens=4096))
X += STEP

# 14. Parse Node 6 — extract audit JSON
nodes.append(set_node(
    "Parse N6",
    [X, Y],
    [
        ("gpt_name", "={{ $('Parse N5').item.json.gpt_name }}", "string"),
        ("idea_document", "={{ $('Parse N5').item.json.idea_document }}", "string"),
        ("purpose_statement", "={{ $('Parse N5').item.json.purpose_statement }}", "string"),
        ("knowledge_report", "={{ $('Parse N5').item.json.knowledge_report }}", "string"),
        ("sop", "={{ $('Parse N5').item.json.sop }}", "string"),
        ("kb_file", "={{ $('Parse N5').item.json.kb_file }}", "string"),
        ("system_prompt", "={{ $('Parse N5').item.json.system_prompt }}", "string"),
        ("audit_raw", "={{ $json.choices[0].message.content }}", "string"),
        # Defensive parse: tolerate code fences, stray text, or malformed JSON.
        # On parse failure return a structured fallback so the workflow still completes.
        ("audit",
         "={{ (() => { const s = $json.choices[0].message.content || ''; const m = s.match(/\\{[\\s\\S]*\\}/); const j = m ? m[0] : s.replace(/^```json\\n?/i,'').replace(/```$/,'').trim(); try { return JSON.parse(j); } catch (e) { return { verdict: 'PARSE_ERROR', error: e.message, raw: s }; } })() }}",
         "object"),
    ],
    keep_only_set=True,
))
X += STEP

# 15. Respond to Webhook
nodes.append({
    "parameters": {
        "respondWith": "json",
        "responseBody": "={{ { ok: true, gpt_name: $json.gpt_name, idea_document: $json.idea_document, purpose_statement: $json.purpose_statement, knowledge_report: $json.knowledge_report, sop: $json.sop, kb_file: $json.kb_file, system_prompt: $json.system_prompt, audit: $json.audit } }}",
        "options": {}
    },
    "id": nid(),
    "name": "Respond",
    "type": "n8n-nodes-base.respondToWebhook",
    "typeVersion": 1.1,
    "position": [X, Y]
})

# ─────────────────────────────────────────────────────────────────────────────
# CONNECTIONS — linear chain
# ─────────────────────────────────────────────────────────────────────────────

names = [n["name"] for n in nodes]
connections = {}
for i in range(len(names) - 1):
    connections[names[i]] = {
        "main": [[{"node": names[i + 1], "type": "main", "index": 0}]]
    }

# ─────────────────────────────────────────────────────────────────────────────
# ASSEMBLE WORKFLOW
# ─────────────────────────────────────────────────────────────────────────────

workflow = {
    "name": "GEM Pipeline · Custom GPT Builder",
    "nodes": nodes,
    "connections": connections,
    "active": False,
    "settings": {"executionOrder": "v1"},
    "versionId": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "meta": {
        "templateCredsSetupCompleted": False
    },
    "tags": []
}

OUT = "/home/claude/gem-pipeline/gem-pipeline.json"
with open(OUT, "w") as f:
    json.dump(workflow, f, indent=2)

print(f"Wrote {OUT}")
print(f"  nodes: {len(nodes)}")
print(f"  connections: {len(connections)}")
print(f"  bytes: {len(json.dumps(workflow))}")
