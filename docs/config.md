# Configuration (role-time choices)

The supervisor agent should be configurable **when assuming the role**.

## Required knobs

### Merge mode
- `auto_merge`: Supervisor can enable GitHub auto-merge for low-risk PRs.
- `recommend_only`: Supervisor labels/comments "safe to merge" but does not enable auto-merge.

### Canonical language
- Default: `en`
- Optional: `zh-hant`, etc.
- Rule: output in canonical language; include short bilingual summary when needed.

## Where to store
For minimalism, a repo-level config file is enough:

- `.supervisor-agent.yml`

Example:
```yaml
merge_mode: auto_merge
canonical_language: en
bilingual_summary_languages: ["zh-hant"]
protected_paths:
  - ".github/workflows/**"
  - "**/auth/**"
  - "**/security/**"
  - "Dockerfile"
  - "docker-compose.*"
reviewer_rules:
  - "docs/**=octo-docs"
  - "scripts/**=octo-eng"
```

`reviewer_rules` format: `glob=reviewer1,reviewer2` (or `glob:reviewer1,reviewer2`).
If a changed file matches a glob, the supervisor requests those reviewers on the PR.

The supervisor may override these at run-time (role assumption), but should print the chosen settings in its first comment.
