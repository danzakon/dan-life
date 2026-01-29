# Claude Skills: Complete Technical Guide

A comprehensive guide to understanding, creating, and deploying Claude Skills for Claude Code—giving Claude specialized capabilities, domain knowledge, and repeatable workflows.

---

## Overview

**Claude Skills** are modular, folder-based packages that extend Claude Code with specialized expertise. Unlike prompts that you repeat every session, skills are discovered automatically and loaded on-demand when Claude determines they're relevant to your task.

Think of skills as "expert modes" you can install. When you say "set up project memory" or "write tests for this," Claude doesn't guess—it loads specific, tested instructions for exactly that task.

Skills follow the open **Agent Skills** specification (published December 2025), which works across multiple AI tools including Claude Code, Claude.ai, and the Claude Developer Platform.

| Feature | Description |
|---------|-------------|
| **Format** | Folder containing a `SKILL.md` file + optional resources |
| **Activation** | Automatic (Claude decides) OR manual via `/skill-name` |
| **Scope** | Enterprise, personal (user-wide), project, or plugin |
| **Complexity** | Simple markdown instructions to multi-file packages with executable code |

**Note:** Custom slash commands have been merged into skills. A file at `.claude/commands/review.md` and a skill at `.claude/skills/review/SKILL.md` both create `/review` and work the same way. Existing `.claude/commands/` files continue to work.

---

## How Skills Work

### Progressive Disclosure Architecture

Claude Code uses a **progressive disclosure** pattern for skills—it only loads what it needs, when it needs it:

```
┌─────────────────────────────────────────────────────────────────┐
│  1. DISCOVERY                                                    │
│     Claude scans skill directories                               │
│     Reads ONLY metadata (name + description) from each skill     │
├─────────────────────────────────────────────────────────────────┤
│  2. MATCHING                                                     │
│     Compares your request against skill descriptions             │
│     Identifies which skills are relevant                         │
├─────────────────────────────────────────────────────────────────┤
│  3. EXECUTION                                                    │
│     Loads full SKILL.md content for matched skills               │
│     Follows instructions, accesses supporting files as needed    │
└─────────────────────────────────────────────────────────────────┘
```

This means you can have dozens of skills installed without slowing down normal interactions—Claude only loads the full skill when it's needed.

### Skills vs Other Extension Methods

| Method | Purpose | Invocation |
|--------|---------|------------|
| **Skills** | Domain knowledge and workflows | Automatic OR `/skill-name` |
| **Subagents** | Specialists with own context | Delegated by Claude |
| **CLAUDE.md** | Always-loaded project context | Automatic (every session) |
| **MCP Servers** | External tool connections | Called by Claude as needed |
| **Plugins** | Package skills + agents + hooks | Distributed via marketplaces |

---

## Skill Structure

### Directory Layout

Every skill is a folder containing at minimum a `SKILL.md` file:

```
skill-name/
├── SKILL.md              # Required: Core instructions
├── resources/            # Optional: Reference files
│   ├── templates/
│   └── examples/
└── scripts/              # Optional: Executable code
    └── helper.py
```

### The SKILL.md File

The `SKILL.md` file has two parts:

1. **YAML Frontmatter** — Metadata that tells Claude when to activate the skill
2. **Markdown Body** — Instructions Claude follows when the skill is active

```markdown
---
name: my-skill-name
description: One-line description of what this skill does and when to use it.
  Include trigger phrases like "write tests", "set up CI", or "review code".
---

# Skill Title

## Overview
What this skill does and why it exists.

## When to Use
- Condition 1
- Condition 2

## Instructions
Step-by-step guidance for Claude.

## Examples
Input/output examples showing expected behavior.
```

### Frontmatter Fields

All frontmatter fields are optional, but `description` is strongly recommended so Claude knows when to use the skill.

| Field | Description |
|-------|-------------|
| `name` | Display name for the skill. If omitted, uses directory name. Lowercase letters, numbers, hyphens only (max 64 chars). Becomes the `/slash-command`. |
| `description` | What the skill does and when to use it. **Critical**—Claude uses this to decide when to load the skill automatically. If omitted, uses first paragraph of markdown content. |
| `argument-hint` | Hint shown during autocomplete (e.g., `[issue-number]` or `[filename] [format]`) |
| `disable-model-invocation` | Set to `true` to prevent Claude from loading automatically. User must invoke with `/name`. Default: `false` |
| `user-invocable` | Set to `false` to hide from `/` menu. Only Claude can invoke. Default: `true` |
| `allowed-tools` | Tools Claude can use without permission when skill is active |
| `model` | Override the model used when skill is active |
| `context` | Set to `fork` to run in an isolated subagent context |
| `agent` | Which subagent to use when `context: fork` (e.g., `Explore`, `Plan`, `general-purpose`) |
| `hooks` | Hooks scoped to this skill's lifecycle |

### Invocation Control Matrix

| Frontmatter | You Invoke | Claude Invokes | When Loaded |
|-------------|------------|----------------|-------------|
| (default) | Yes | Yes | Description in context, full skill on invoke |
| `disable-model-invocation: true` | Yes | No | Description NOT in context |
| `user-invocable: false` | No | Yes | Description in context |

---

## Where Skills Live

Skills can be stored at multiple levels, with higher-priority locations taking precedence:

```
┌─────────────────────────────────────────────────────────────────┐
│  SKILL LOCATION PRECEDENCE (highest to lowest)                  │
├─────────────────────────────────────────────────────────────────┤
│  1. Enterprise    System-level managed settings                 │
│  2. Personal      ~/.claude/skills/                             │
│  3. Project       .claude/skills/                               │
│  4. Plugin        <plugin>/skills/ (namespaced)                 │
└─────────────────────────────────────────────────────────────────┘
```

| Location | Path | Applies To |
|----------|------|------------|
| **Enterprise** | See managed settings | All users in organization |
| **Personal** | `~/.claude/skills/<skill-name>/SKILL.md` | All your projects |
| **Project** | `.claude/skills/<skill-name>/SKILL.md` | This project only |
| **Plugin** | `<plugin>/skills/<skill-name>/SKILL.md` | Where plugin is enabled |

When skills share the same name, higher-priority locations win. Plugin skills use a `plugin-name:skill-name` namespace to avoid conflicts.

### Personal Skills (User-Wide)

```
~/.claude/skills/skill-name/SKILL.md
```

- Available in **all projects**
- Good for: general-purpose workflows, personal preferences, cross-project patterns

### Project Skills (Local)

```
.claude/skills/skill-name/SKILL.md
```

- Available **only in this project**
- Good for: team conventions, project-specific workflows, codebase patterns
- Committed to version control for team sharing

### Automatic Discovery from Nested Directories

When working with files in subdirectories, Claude Code automatically discovers skills from nested `.claude/skills/` directories. For example, if editing a file in `packages/frontend/`, Claude also looks for skills in `packages/frontend/.claude/skills/`. This supports monorepo setups where packages have their own skills.

You can also organize skills into categories:

```
~/.claude/skills/
├── testing/
│   ├── unit-testing/SKILL.md
│   └── e2e-testing/SKILL.md
├── documentation/
│   └── api-docs/SKILL.md
└── code-review/
    └── security-review/SKILL.md
```

---

## Creating Your First Skill

### Step 1: Create the Directory Structure

```bash
# For a global skill (available everywhere)
mkdir -p ~/.claude/skills/my-first-skill

# For a project-local skill
mkdir -p .claude/skills/my-first-skill
```

### Step 2: Write the SKILL.md File

Create `~/.claude/skills/my-first-skill/SKILL.md`:

```markdown
---
name: brand-guidelines
description: Apply Acme Corp brand guidelines to presentations and documents.
  Use when creating external-facing materials, marketing content, or documents
  that represent the company. Trigger phrases include "use brand guidelines",
  "apply branding", or "format for external sharing".
---

# Brand Guidelines Skill

## Overview
This skill provides Acme Corp's official brand guidelines for creating 
consistent, professional materials.

## Brand Colors
| Color | Hex | Usage |
|-------|-----|-------|
| Primary | #FF6B35 (Coral) | Headers, CTAs |
| Secondary | #004E89 (Navy) | Body text, backgrounds |
| Accent | #F7B801 (Gold) | Highlights, icons |

## Typography
- **Headers**: Montserrat Bold
- **Body**: Open Sans Regular
- **H1**: 32pt | **H2**: 24pt | **Body**: 11pt

## Logo Usage
- Full-color logo on light backgrounds
- White logo on dark backgrounds
- Minimum spacing: 0.5 inches around logo

## When to Apply
Apply these guidelines when creating:
- PowerPoint presentations
- Word documents for external sharing
- Marketing materials
- Client-facing reports
```

### Step 3: Test Your Skill

Start a new Claude Code session and try:

```
Create a presentation outline about our Q4 results using brand guidelines
```

Claude should recognize the trigger and apply your brand standards.

---

## Practical Skill Examples

### Example 1: Testing Patterns Skill

```markdown
---
name: testing-patterns
description: Jest testing patterns for this project. Use when writing tests,
  creating mocks, or following TDD workflow. Triggers on "write test",
  "add tests", "test this", "mock this", "TDD".
---

# Testing Patterns

## Arrange-Act-Assert Pattern

```typescript
// Arrange
const mockUser = getMockUser();

// Act
const result = login(mockUser);

// Assert
expect(result).toBeTruthy();
```

## Mocking Strategy
- Prefer factory functions over global mocks
- Keep mocks in `__mocks__/` directory
- Use `jest.spyOn()` for partial mocking

## Test File Naming
- Unit tests: `*.test.ts`
- Integration tests: `*.integration.test.ts`
- E2E tests: `*.e2e.test.ts`

## Coverage Requirements
- Minimum 80% line coverage
- 100% coverage for critical paths
```

### Example 2: Project Memory Skill

```markdown
---
name: project-memory
description: Set up and maintain a structured project memory system in 
  docs/project_notes/ that tracks bugs with solutions, architectural decisions,
  key project facts, and work history. Use when asked to "set up project memory",
  "track decisions", "log a bug fix", or "update project memory".
---

# Project Memory System

## File Structure

```
docs/project_notes/
├── bugs.md        # Bug fixes with solutions
├── decisions.md   # Architecture Decision Records (ADRs)
├── key_facts.md   # Important project details
└── issues.md      # Work log with ticket references
```

## bugs.md Format

```markdown
## BUG-001: [Brief description]
- **Date**: YYYY-MM-DD
- **Symptoms**: What went wrong
- **Root Cause**: Why it happened
- **Solution**: How it was fixed
- **Prevention**: How to avoid in future
```

## decisions.md Format (ADR)

```markdown
## ADR-001: [Decision Title]
- **Status**: Proposed | Accepted | Deprecated
- **Context**: Why this decision was needed
- **Decision**: What was decided
- **Alternatives**: What else was considered
- **Consequences**: What this means going forward
```

## key_facts.md Format

```markdown
## Environment URLs
- Production: https://api.prod.example.com
- Staging: https://api.staging.example.com:8443

## Key Ports
- API: 8080
- Database: 5432 (prod), 5433 (staging)
```

## Updating Memory
When the user reports a bug fix or makes a decision:
1. Ask for details if not provided
2. Format according to templates above
3. Append to appropriate file
4. Confirm the update
```

### Example 3: Code Review Skill

```markdown
---
name: code-review-checklist
description: Systematic code review following team standards. Use when
  reviewing PRs, checking code quality, or asked to "review this code",
  "check this PR", or "code review".
---

# Code Review Checklist

## Security
- [ ] No hardcoded secrets or API keys
- [ ] Input validation on all user data
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output encoding)

## Performance
- [ ] No N+1 query patterns
- [ ] Appropriate caching strategy
- [ ] No blocking operations in async code
- [ ] Bundle size impact considered

## Code Quality
- [ ] Functions under 50 lines
- [ ] Single responsibility principle
- [ ] Meaningful variable names
- [ ] No commented-out code

## Testing
- [ ] New code has tests
- [ ] Edge cases covered
- [ ] Mocks are minimal and focused

## Review Process
1. Read PR description and linked ticket
2. Run through checklist above
3. Check each file for issues
4. Provide specific, actionable feedback
5. Approve or request changes
```

---

## Adding Supporting Files

For complex skills, add reference materials:

```
my-skill/
├── SKILL.md
├── resources/
│   ├── template.md          # Reusable templates
│   ├── examples/
│   │   ├── good-example.ts  # What to do
│   │   └── bad-example.ts   # What to avoid
│   └── reference.pdf        # Documentation
└── scripts/
    └── validator.py         # Executable code
```

Reference files in your SKILL.md:

```markdown
## Templates
See `resources/template.md` for the standard format.

## Examples
Good: `resources/examples/good-example.ts`
Bad: `resources/examples/bad-example.ts`
```

---

## Advanced Patterns

### String Substitutions

Skills support dynamic string substitution for arguments and session data:

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | All arguments passed when invoking the skill |
| `$ARGUMENTS[N]` | Access specific argument by 0-based index (e.g., `$ARGUMENTS[0]`) |
| `$N` | Shorthand for `$ARGUMENTS[N]` (e.g., `$0`, `$1`) |
| `${CLAUDE_SESSION_ID}` | Current session ID (useful for logging or session-specific files) |

**Example: Fix Issue Skill**

```markdown
---
name: fix-issue
description: Fix a GitHub issue by number
disable-model-invocation: true
---

Fix GitHub issue $ARGUMENTS following our coding standards.

1. Read the issue description
2. Understand the requirements
3. Implement the fix
4. Write tests
5. Create a commit
```

When you run `/fix-issue 123`, Claude receives "Fix GitHub issue 123 following our coding standards..."

**Example: Multi-Argument Skill**

```markdown
---
name: migrate-component
description: Migrate a component from one framework to another
---

Migrate the $0 component from $1 to $2.
Preserve all existing behavior and tests.
```

Running `/migrate-component SearchBar React Vue` substitutes the arguments appropriately.

If `$ARGUMENTS` is not present in the skill content, arguments are appended as `ARGUMENTS: <value>`.

### Injecting Dynamic Context with Shell Commands

The `!`command`syntax runs shell commands before the skill content is sent to Claude. The command output replaces the placeholder.

**Example: PR Summary Skill**

```markdown
---
name: pr-summary
description: Summarize changes in a pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context

- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task

Summarize this pull request...
```

When this skill runs:
1. Each `!`command` executes immediately (before Claude sees anything)
2. The output replaces the placeholder in the skill content
3. Claude receives the fully-rendered prompt with actual PR data

This is preprocessing, not something Claude executes.

### Running Skills in a Subagent

Add `context: fork` to run a skill in isolation with its own context. The skill content becomes the prompt that drives the subagent (no access to conversation history).

```markdown
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:

1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

When this skill runs:
1. A new isolated context is created
2. The subagent receives the skill content as its prompt
3. The `agent` field determines execution environment (model, tools, permissions)
4. Results are summarized and returned to your main conversation

Available built-in agents: `Explore`, `Plan`, `general-purpose`, or any custom subagent from `.claude/agents/`.

**Note:** `context: fork` only makes sense for skills with explicit tasks. If your skill contains guidelines without a task, the subagent has nothing actionable to do.

### Restricting Tool Access

Limit what tools a skill can use:

```markdown
---
name: safe-review
description: Read-only code review
allowed-tools: Read, Grep, Glob
---
```

### Skills with Side Effects

For skills that deploy, commit, or have other side effects, prevent automatic invocation:

```markdown
---
name: deploy
description: Deploy the application to production
disable-model-invocation: true
---

Deploy $ARGUMENTS to production:

1. Run the test suite
2. Build the application
3. Push to the deployment target
4. Verify the deployment succeeded
```

You invoke with `/deploy staging` or `/deploy production`. Claude will never run this automatically.

### Extended Thinking in Skills

To enable extended thinking in a skill, include the word "ultrathink" anywhere in your skill content.

---

## Skills vs CLAUDE.md

Understanding when to use each:

| CLAUDE.md | Skills |
|-----------|--------|
| Always loaded every session | Loaded only when relevant |
| Project context and conventions | Specific workflows and expertise |
| Build commands, architecture notes | How to write tests, review code |
| Keep concise (always in context) | Can be detailed (loaded on-demand) |

### CLAUDE.md Example

```markdown
# CLAUDE.md

## Stack
- React 18 + TypeScript
- PostgreSQL + Prisma
- Jest for testing

## Commands
- `npm run dev` - Start development
- `npm test` - Run tests
- `npm run lint` - Lint code

## Architecture
- Components in src/components/
- API routes in src/api/
- Database models in prisma/schema.prisma

## Conventions
- Functional components only
- No `any` types
- All exports named (no default exports)
```

### Skill Complement

The skill provides *how* to follow these conventions:

```markdown
---
name: react-patterns
description: React component patterns for this project
---

# React Component Template

```tsx
import { FC } from 'react';

interface Props {
  // Props interface
}

export const ComponentName: FC<Props> = ({ prop1, prop2 }) => {
  return (
    <div>
      {/* Component content */}
    </div>
  );
};
```
```

---

## Packaging and Sharing Skills

### For Claude.ai (Web/Desktop)

1. Ensure folder name matches skill name
2. Create a ZIP file of the folder
3. ZIP should contain skill folder as root

```
my-skill.zip
└── my-skill/
    ├── SKILL.md
    └── resources/
```

**Incorrect:**
```
my-skill.zip
└── (files directly in ZIP root)  ❌
```

4. Upload in **Settings > Capabilities > Skills**

### For Claude Code (CLI)

Skills are just folders—share via:
- Git repository
- Copy to `~/.claude/skills/`
- Include in project `.claude/skills/`

---

## Testing Your Skills

### Before Publishing

- [ ] YAML frontmatter is valid
- [ ] Description includes trigger phrases
- [ ] All referenced files exist
- [ ] Instructions are clear and specific
- [ ] Examples show expected input/output

### After Installing

1. Start a new Claude Code session
2. Try different trigger phrases
3. Check Claude's thinking to confirm skill loaded
4. Test edge cases
5. Iterate on description if not triggering correctly

### Debugging Activation

If your skill isn't activating:

1. **Check the description** — Does it include words from your request?
2. **Be specific** — Generic descriptions compete with other skills
3. **Test trigger phrases** — Try the exact phrases in your description
4. **Check location** — Is the skill in `~/.claude/skills/` or `.claude/skills/`?
5. **Check filename** — The file must be named `SKILL.md` (case-sensitive)

---

## Best Practices

### Writing Effective Skills

| Do | Don't |
|----|-------|
| ✅ Solve specific, repeatable tasks | ❌ Try to do everything in one skill |
| ✅ Include clear trigger phrases in description | ❌ Use vague descriptions |
| ✅ Provide examples | ❌ Assume Claude knows your conventions |
| ✅ Start simple, expand later | ❌ Build complex skills before testing basic version |
| ✅ Define success criteria | ❌ Leave output format ambiguous |

### Description Writing Tips

The description is the most important part—Claude uses it to decide when to activate:

**Good:**
```yaml
description: Apply Acme Corp brand guidelines to presentations and documents.
  Use when creating external-facing materials, marketing content, or documents
  that represent the company. Triggers on "use brand guidelines", "apply branding",
  "format for external", "company presentation".
```

**Bad:**
```yaml
description: Brand guidelines for the company.
```

### Composability

Skills can work together. Multiple skills may activate for a single request:

```
"Write tests for this React component following our patterns"
         │                               │
         ▼                               ▼
  testing-patterns            react-patterns
      (skill)                    (skill)
```

---

## Security Considerations

1. **Don't hardcode secrets** — Use environment variables
2. **Review downloaded skills** — Check code before enabling
3. **Limit tool access** — Use `allowed-tools:` field for sensitive skills
4. **No sensitive data in skills** — They may be shared
5. **Audit external skills** — Pay attention to code dependencies and external network sources

---

## Related: Claude Code Configuration Hierarchy

Skills are part of a broader configuration system. Understanding where different configurations live helps when organizing your skills.

### Configuration File Locations

```
┌─────────────────────────────────────────────────────────────────┐
│  CONFIGURATION PRECEDENCE (highest to lowest)                   │
├─────────────────────────────────────────────────────────────────┤
│  1. Managed      /Library/Application Support/ClaudeCode/       │
│                  (macOS) - deployed by IT, cannot be overridden │
│  2. Command line Arguments for this session                     │
│  3. Local        .claude/settings.local.json (gitignored)       │
│  4. Project      .claude/settings.json (shared with team)       │
│  5. User         ~/.claude/settings.json (personal global)      │
└─────────────────────────────────────────────────────────────────┘
```

### What Lives Where

| Feature | User Location | Project Location | Local Location |
|---------|---------------|------------------|----------------|
| **Settings** | `~/.claude/settings.json` | `.claude/settings.json` | `.claude/settings.local.json` |
| **Skills** | `~/.claude/skills/` | `.claude/skills/` | — |
| **Subagents** | `~/.claude/agents/` | `.claude/agents/` | — |
| **MCP servers** | `~/.claude.json` | `.mcp.json` | `~/.claude.json` (per-project) |
| **Memory** | `~/.claude/CLAUDE.md` | `CLAUDE.md` or `.claude/CLAUDE.md` | `CLAUDE.local.md` |

### Managed Settings (Enterprise)

System-level locations for IT-deployed configurations:

| Platform | Path |
|----------|------|
| macOS | `/Library/Application Support/ClaudeCode/` |
| Linux/WSL | `/etc/claude-code/` |
| Windows | `C:\Program Files\ClaudeCode\` |

These are system-wide paths (not user home directories) requiring administrator privileges.

---

## Quick Reference

### File Locations

```bash
# Personal skills (all projects)
~/.claude/skills/skill-name/SKILL.md

# Project skills (this project only)
.claude/skills/skill-name/SKILL.md
```

### Minimal SKILL.md Template

```markdown
---
name: skill-name
description: What this skill does. Include trigger phrases like "do X", "set up Y".
---

# Skill Title

## Overview
Brief description.

## Instructions
1. Step one
2. Step two

## Examples
Input: "example request"
Output: Expected behavior
```

### Task-Oriented Skill Template (Manual Invocation)

```markdown
---
name: deploy
description: Deploy the application
disable-model-invocation: true
argument-hint: [environment]
---

Deploy to $ARGUMENTS:

1. Run tests
2. Build application
3. Push to deployment target
```

### Subagent Skill Template

```markdown
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS:

1. Find relevant files
2. Analyze code
3. Summarize findings
```

### Check Installed Skills

```bash
# List personal skills
ls ~/.claude/skills/

# List project skills
ls .claude/skills/

# Ask Claude what skills are available
# In Claude Code: "What skills are available?"
```

### Invoking Skills

```bash
# Manual invocation
/skill-name argument1 argument2

# Let Claude decide
"Deploy to staging"  # Claude loads deploy skill if available
```

---

## Resources

| Resource | URL |
|----------|-----|
| Official Skills Documentation | https://code.claude.com/docs/en/skills |
| Claude Code Settings | https://code.claude.com/docs/en/settings |
| Agent Skills Introduction (Anthropic) | https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills |
| Skills API Cookbook | https://platform.claude.com/cookbook/skills-notebooks-01-skills-introduction |
| Skill Authoring Best Practices | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices |
| Claude Help Center: Using Skills | https://support.claude.com/en/articles/12512180-using-skills-in-claude |

---

## Changelog

| Date | Update |
|------|--------|
| 2026-01-29 | Major update: Added invocation control, string substitutions, dynamic context injection, subagent integration, configuration hierarchy |
| 2026-01-28 | Initial guide created |
