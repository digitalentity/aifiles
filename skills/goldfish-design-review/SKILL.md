---
name: goldfish-design-review
description: Review a spec or design document using cold-reader comprehension and codebase grounding goldfish subagents, then synthesize an actionable report of where the design does not hold without proposing solutions.
---

Review an existing specification, PRD, or design document using the elephant/goldfish workflow. Two fresh subagents ("goldfish") with zero conversation history independently test **comprehension** (can a cold reader understand and execute the document without guessing?) and **codebase grounding** (do the document's claims hold against actual repository code and project conventions?). The elephant verifies every citation and synthesizes a structured report as a conversation artifact or repository file.

## Core Rules

1. **No solutions.** Every finding must pinpoint **where** and **why** the design does not hold, contradicts the codebase, violates project standards, or leaves an unimplementable gap. Never propose fixes, alternative architectures, code snippets, or "consider doing X instead" suggestions.
2. **Actionable through precision.** A finding is actionable because it names the exact document section, cites the exact conflicting `file:line` (or missing contract/invariant), and explains the concrete failure mode or ambiguity the author must resolve.
3. **No praise, no hedging, no invention.** State flaws directly ("Section 2.2 contradicts `pkg/foo/bar.go:42`", not "this might potentially be an issue"), skip compliment sandwiches, and drop any suspicion that cannot be backed by the text or codebase.
4. **Read-only review.** Never modify the reviewed specification, design document, or source code.

---

## Step 0: Resolve Input and Output Target

If the user did not provide a path to a spec/design document or paste one inline, ask them to identify the document before proceeding. If they referenced a package or SDD spec number, resolve the corresponding specification file (e.g., `<pkg>/spec/NNN_<feature_name>/spec.md` or `specs/NNN_<feature_name>/spec.md`).

Read the target document in full using `read_file`.

Then ask the user where to place the synthesized report via `ask_question` (or `ask_user` in Gemini CLI):

**Q1 — Report placement:**
- `question`: "Where should the design review report be saved?"
- `header`: `"Output"`
- `multiSelect`: `false`
- `options`:
  1. **(Recommended) Conversation artifact** — "Write `design-review.md` to the session artifact directory."
  2. **Alongside the spec (`<spec-dir>/design-review.md`)** — "Save as a markdown file in the same directory as the reviewed document."
  3. **Custom file path** — "I will provide a target file path in chat."

If the user selects **Custom file path**, ask for the path in chat before writing the final report in Step 3.

---

## Step 1: Run Parallel Comprehension and Grounding Goldfish

Spawn **two fresh subagents in parallel** using `invoke_subagent` (or `invoke_agent` in Gemini CLI, `agent_name="generalist"`).

**Context isolation:** Pass ONLY the prompt template and the verbatim design document text (plus its repo-relative path). Do NOT pass conversation history, user intent, or your own preliminary impressions.

### Goldfish A — Cold-Reader Comprehension & Internal Consistency

Verifies whether the document reads cleanly, is internally consistent, and specifies enough detail to be executable without guesswork.

**Prompt to send to Goldfish A:**

```
<<<COMPREHENSION_START>>>
You are a fresh reviewer with no prior context. Below is a spec / design document for the repository.

Your job has two parts:
1. Paraphrase what the document says so the author can see whether a cold reader's mental model matches their intent.
2. Identify every place where the document is ambiguous, internally contradictory, or too underspecified to implement without guessing.

STRICT CONSTRAINT: Do NOT propose solutions, fixes, rewrites, or alternative designs. Only state what is unclear, contradictory, or missing, and why the design does not hold as written.

Output these sections in order:

## 1. What this system/feature does (cold-reader view)
2-5 sentences in your own words: who or what triggers it, what changes, and what the caller or operator observes.

## 2. How the existing system works (per the document)
2-5 sentences summarizing the current surfaces, data flows, services, or components the document claims to build upon.

## 3. Comprehension & Specification Findings
Numbered list of every place where the document fails a cold reader or implementer. Hunt for:
- Ambiguous sections or undefined terms that cannot be paraphrased without guessing.
- Contradictions between sections (e.g., prose vs. Mermaid diagrams vs. data structures vs. task list).
- Underspecified interfaces: missing types, value ranges, units, error semantics, wire/storage formats, or concurrency invariants.
- Missing failure modes: unstated behavior when dependencies, I/O, transactions, or network calls fail.
- Untestable or circular verification criteria.

For each finding, output:
- **Document Location:** exact heading / section / claim.
- **Finding:** what is ambiguous, contradictory, or missing.
- **Why It Does Not Hold:** the concrete question an implementer cannot answer or the failure mode left unaddressed (NO proposed fix).

End your output with EXACTLY one of these closing lines on its own line:
- comprehension passed
- comprehension findings surfaced

DOCUMENT PATH: <REPO-RELATIVE PATH OR "INLINE">
DOCUMENT:

<PASTE FULL SPEC / DESIGN DOC HERE>
<<<COMPREHENSION_END>>>
```

### Goldfish B — Codebase & Architecture Grounding

Verifies every factual claim the document makes against the actual repository code, build manifests, schemas, and project guidelines (e.g., `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `README.md`).

**Prompt to send to Goldfish B:**

```
<<<GROUNDING_START>>>
You are a fresh reviewer with no prior context. Below is a spec / design document for this repository (inspect any root project instructions such as AGENTS.md, CLAUDE.md, GEMINI.md, or README.md for architecture and repository rules).

Your job: read the document, then inspect the actual codebase surfaces it claims to touch or depend on, and find every place where the design does not hold against reality.

STRICT CONSTRAINT: Do NOT propose solutions, fixes, or alternative designs. Report only what does not hold, cite the exact document section and repository file:line, and explain why it breaks or violates repository invariants.

Hunt for:
1. **False codebase assumptions** — files, packages, modules, types, functions, CLI flags, database tables/buckets, API endpoints, or build targets cited by the doc that do not exist, have different signatures, or behave differently than claimed.
2. **Unacknowledged callers & blast radius** — existing callers, services, schemas, or wire protocols that would break if the described changes were made.
3. **Lifecycle, concurrency & resource flaws** — race conditions, lock ordering conflicts, unclosed handles, goroutine/thread/task leaks, or unstated allocation/latency budgets on hot paths.
4. **Storage & serialization mismatches** — unhandled transaction boundaries, schema migration gaps for existing data stores, or format mismatches against project conventions.
5. **Configuration & runtime violations** — inconsistencies with existing configuration loading, environment variable binding, flag precedence, or error-handling conventions.
6. **Build, VCS & boundary violations** — violations of project build system rules, module/package boundaries, dependency policies, or repository conventions documented in project instructions.

Output two sections:

## 1. Grounding Matrix
A markdown table mapping each surface, type, target, or dependency claimed in the document to its actual state in the repository (`file:line` and status: `HOLDS`, `MISMATCH`, or `MISSING`).

## 2. Grounding Findings
Numbered list of findings where the design does not hold. For each finding:
- **Document Location:** exact section heading and claim.
- **Codebase Evidence:** exact repo-relative `file:line` (or project guidelines section).
- **Why It Does Not Hold:** concrete explanation of the mismatch, broken invariant, or failure mode (NO proposed solution).

End your output with EXACTLY one of these closing lines on its own line:
- grounding passed
- grounding findings surfaced

DOCUMENT PATH: <REPO-RELATIVE PATH OR "INLINE">
DOCUMENT:

<PASTE FULL SPEC / DESIGN DOC HERE>
<<<GROUNDING_END>>>
```

---

## Step 2: Verify and Filter Findings

Once both goldfish return, the elephant performs verification before writing the report:

1. **Verify citations:** Check every `file:line` and document section reference against the workspace. Correct inaccurate line numbers and discard any hallucinated findings that do not hold up on inspection.
2. **Deduplicate and rank:** Merge overlapping findings from Goldfish A and Goldfish B. Classify each surviving finding by severity:
   - `CRITICAL` — Design contradicts existing code/schemas, corrupts state, breaks invariants, or cannot be built as specified.
   - `MAJOR` — Significant ambiguity, missing failure mode, unaddressed blast radius, or project rule violation that blocks clean implementation.
   - `MINOR` — Localized underspecification, stale reference, or minor gap in verification criteria.
3. **Purge solutions:** Strip any phrasing from subagent outputs that suggests a fix, redesign, or recommendation (e.g., "should instead...", "consider adding...", "fix by..."). State only the defect and its consequence.

---

## Step 3: Synthesize Report

Write the synthesized report to the destination selected in Step 0:

- **If Conversation artifact:** Write `<appDataDir>/brain/<conversation-id>/design-review.md` using `write_file` with `ArtifactMetadata` (`UserFacing: true`, `RequestFeedback: false`).
- **If Alongside the spec or Custom file path:** Write the file using `write_file` at the chosen path. Use repository-root relative paths for all codebase references inside repository markdown files (avoid host-specific absolute paths or `file://` URIs).

Use this report template:

```markdown
# Design Review: <Document Title or Path>

* **Reviewed Document:** `<repo-relative-path or inline>`
* **Verdict:** `HOLDS` | `DOES NOT HOLD (<N> critical, <M> major, <K> minor)`

---

## 1. Comprehension Check (Cold-Reader View)

### Perceived Feature Behavior
<2-5 sentences from Goldfish A describing what a cold reader understood the design to do.>

### Perceived System Context
<2-5 sentences from Goldfish A describing how the document portrays the existing system.>

### Mental-Model Alignment
<1-2 sentences noting whether the document reads clearly or where a cold reader's understanding breaks down.>

---

## 2. Codebase Grounding Matrix

| Claimed Surface / Dependency | Document Section | Repository State (`file:line`) | Status |
| :--- | :--- | :--- | :--- |
| `<symbol / target / config>` | `<section>` | `<repo-relative path:line>` | `HOLDS` / `MISMATCH` / `MISSING` |

---

## 3. Actionable Findings

<If zero findings survive verification, state: "No findings. The design holds against comprehension and codebase grounding checks." Otherwise, list findings ranked worst-first (`CRITICAL`, `MAJOR`, `MINOR`):>

### [SEVERITY] F1: <Concise Statement of What Does Not Hold>
* **Category:** `Comprehension` | `Contradiction` | `Codebase Mismatch` | `Blast Radius` | `Failure Mode` | `Project Rule Violation`
* **Document Location:** `<Section heading / claim>`
* **Codebase Evidence:** `<repo-relative file:line or N/A>`
* **Why It Does Not Hold:** <Direct, concrete explanation of the contradiction, false assumption, broken invariant, or ambiguity, and the exact failure or blocker it creates. No proposed solutions.>
```

---

## Step 4: Final Summary

After writing the report:
- Point the user to the generated artifact or file path.
- Print a concise summary in chat (verdict, counts by severity, and whether comprehension aligned with the document's apparent intent) without re-summarizing the full report body.

**STOP.** Do NOT edit the reviewed document, write implementation code, or mutate VCS state.
