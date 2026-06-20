---
name: goal-prompt-generator
description: >-
  Turn an implementation plan or task description into a bounded, self-contained
  goal prompt that another agent session can pursue autonomously and be checked
  against. Produces a structured prompt with objective, definition of done, repo
  constraints, verification gates, and stop conditions. TRIGGER when: user asks
  to package work for another session, write a goal prompt, prepare a task for
  autonomous execution, or hand off a task to a fresh agent. DO NOT TRIGGER
  when: the user just wants a plan for the current session or a quick task
  completable in one exchange.
origin: ECC
---

# Goal Prompt Generator

Turn an implementation plan or task description into a bounded goal prompt a
fresh agent session can execute autonomously and that you can verify without
re-deriving the plan.

## When to Activate

- User says: "package this for another session", "write a goal prompt", "prepare
  this for autonomous execution", "hand this off", "give me a prompt I can paste"
- A task is too large or context-heavy for the current session and needs to be
  delegated cold
- User wants to verify a task's completion criteria before starting it
- Any time the receiving agent will have zero context from this conversation

**Do not activate** when the user wants a plan for the current session, or for
tasks completable in a single exchange.

## How It Works

### Phase 1: Extract

Read the task description or implementation plan and extract:

- The single overarching objective (what success looks like)
- Every concrete deliverable (files changed, tests passing, behaviour enabled)
- The affected area of the repository (dirs, files, subsystems)
- Any files or areas that must not change (infra, unrelated modules, configs)
- The commands that prove completion (test suite, linter, build, smoke test)
- Decision points where a wrong assumption would cause significant rework

### Phase 2: Identify gaps

Before writing, flag anything the receiving agent would need but doesn't have:

- Exact file paths (never write "the config file" — write the path)
- Branch names, PR numbers, issue references
- Environment variables or credentials needed (note them; do not paste values)
- External dependencies or services the task touches
- Non-obvious constraints (performance budget, backward-compat requirement,
  locked API surface)

Fill gaps from context if you have it; list them as UNKNOWNS if you don't.

### Phase 3: Write the goal prompt

Produce a Markdown document with exactly these five sections in order:

---

#### OBJECTIVE

One paragraph. State what the agent must build or fix, why it matters, and what
the system looks like when the work is done. No bullet points — prose only. The
agent should be able to read this paragraph and understand the job completely.

#### DEFINITION OF DONE

A checklist of verifiable statements. Every item must be checkable by running a
command or inspecting a file — no subjective criteria allowed.

```
- [ ] <verifiable statement>
- [ ] <verifiable statement>
```

Good: `[ ] All 42 tests in tests/lib/utils.test.js pass with exit code 0`
Bad:  `[ ] Code is clean and well-tested`

#### REPO CONSTRAINTS

Two sub-lists:

**May modify:**
- List every directory, file, or glob pattern the agent is allowed to touch.
  Be specific. If unsure, err toward narrower scope.

**Must NOT touch:**
- List every area that is off-limits. Include infra files, CI configs, unrelated
  modules, lock files, and anything the task description did not mention.
- When in doubt, add it here — the agent must stop and ask if the task
  requires touching a file not on the allowed list.

#### VERIFICATION GATES

The exact shell commands to run, in order, with the expected output or exit code.
The agent must run these before declaring completion. No approximations.

```bash
# Gate 1: [description]
<command>
# Expected: <output or "exit 0">

# Gate 2: [description]
<command>
# Expected: <output or "exit 0">
```

#### STOP CONDITIONS

Situations where the agent must halt immediately and ask instead of improvising.
Write these as specific triggerable conditions, not vague warnings.

- If a required file is missing from the repo (not just empty)
- If any verification gate fails after two attempts
- If the task requires modifying a file in the Must NOT touch list
- If an external service (API, DB, queue) is unreachable and the task depends
  on it
- If the implementation plan contradicts the existing code in a way that would
  require a design decision (e.g., the plan says "add a field" but the model
  is immutable)
- [Add task-specific stop conditions here]

---

### Phase 4: Self-containment check

Before delivering, answer both questions silently:

1. **Execution test**: Could a competent agent with zero context from this
   conversation read this prompt and execute the task correctly?
2. **Verification test**: Could I verify the result without re-deriving the
   plan — just by running the verification gates?

If either answer is "no", revise the prompt until both are "yes".

### Phase 5: Deliver

Present the goal prompt as a fenced Markdown block (so the user can copy it
cleanly). Briefly note any UNKNOWNS you could not fill and what the user should
resolve before sending the prompt to another session.

## Output Template

````markdown
# Goal Prompt: <short title>

## OBJECTIVE

<one paragraph>

## DEFINITION OF DONE

- [ ] <verifiable statement>
- [ ] <verifiable statement>
- [ ] <verifiable statement>

## REPO CONSTRAINTS

**May modify:**
- `<path or glob>`
- `<path or glob>`

**Must NOT touch:**
- `<path or glob>`
- `<path or glob>`

## VERIFICATION GATES

```bash
# Gate 1: <description>
<command>
# Expected: <output or exit 0>

# Gate 2: <description>
<command>
# Expected: <output or exit 0>
```

## STOP CONDITIONS

- If <specific condition>, halt and ask.
- If <specific condition>, halt and ask.
- If any verification gate fails after two attempts, halt and ask.
- If the task requires modifying a file not listed under "May modify", halt and
  ask.
````

## Quality Rules

| Rule | Enforcement |
|------|-------------|
| No relative paths | Write `skills/goal-prompt-generator/SKILL.md`, not `the skill file` |
| No subjective done criteria | Every DoD item must be checkable by a command |
| Exact commands in gates | Copy-pasteable, not paraphrased |
| Narrow may-modify list | Default to the smallest scope that can complete the task |
| Stop conditions are specific | "if X happens" not "if something goes wrong" |
| One objective paragraph | If it takes two, split into two goal prompts |

## Examples

### Example 1 — Adding a new skill

```
User: Package the task "add a goal-prompt-generator skill to skills/" for
      another session.
```

Output: a goal prompt with objective (create the skill file), DoD (file exists,
frontmatter valid, markdownlint passes), constraints (may modify `skills/` only),
verification gates (`node tests/run-all.js`, `npx markdownlint-cli 'skills/**/*.md'`),
stop conditions (if the skill format diverges from the existing SKILL.md template).

### Example 2 — Bug fix

```
User: Prepare a goal prompt to fix the broken package-manager detection in
      scripts/lib/package-manager.js — it returns "npm" even when a bun.lockb
      is present.
```

Output: objective explains the detection order bug; DoD includes the specific
test case that must pass; constraints limit edits to `scripts/lib/package-manager.js`
and `tests/lib/package-manager.test.js`; gates run `node tests/lib/package-manager.test.js`;
stop conditions include "if fixing this requires changing the public API surface
of package-manager.js".

### Example 3 — Multi-file refactor

For larger tasks, generate one goal prompt per logical unit of work (e.g., one
per PR). Each prompt is independently verifiable. Link them by noting which
gate output one step produces that the next step depends on.
