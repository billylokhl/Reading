---
name: git_commit_conventions
description: Guidelines for committing vault updates using Conventional Commits and atomic staging.
---

# Git Commit Guidelines for this Vault

When making code changes or updating notes in this vault, always commit your changes using Conventional Commits and atomic staging.

## 1. Commit Message Format

Commit messages must follow the [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) specification:

```
<type>(<scope>): <description>
```

### Supported Types:
- **feat**: A new feature or major addition (e.g., a new dashboard component, a logs importer script).
- **fix**: A bug fix (e.g., fixing regex properties, repairing a layout alignment).
- **chore**: Maintenance tasks, ignore-file updates, or Obsidian configuration changes.
- **docs**: Documentation updates (e.g., walkthroughs, READMEs).

### Supported Scopes (Examples):
- `dashboard`: Changes related to the pages-read chart or its interface.
- `logs`: Log import operations, parsing scripts, or chapter mapping updates.
- `materials`: Updates to book files, authors, page numbers, or Tables of Contents.
- `git`: Changes to `.gitignore` or git tracking configurations.
- `obsidian`: Machine configs, templates, themes, or workspace metadata.

---

## 2. Atomic Commits

Do not combine unrelated changes into a single monolithic commit. Group your commits by logical folders or functions:

1.  **Configuration**: Stage and commit `.gitignore` or `.obsidian/` configs separately.
2.  **Reading Materials**: Commit modifications to the `Reading Materials/` directory.
3.  **Reading Logs**: Commit updates to log notes or parser scripts separately.
4.  **Dashboard**: Commit changes to `Dashboard.md`.

Use selective staging (`git add <file>`) to ensure each commit addresses a single atomic purpose.

---

## 3. Git Ignore Rules

Keep Obsidian workspace state files out of version control. The following should always be ignored:
- `**/workspace.json`
- `**/workspace-mobile.json`
- `.DS_Store`
- `*.log`
