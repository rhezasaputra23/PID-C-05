# Issue tracker: GitHub

Issues and specs for `rhezasaputra23/PID-C-05` live in GitHub Issues. Use the `gh` CLI from this repository.

## Conventions

- Create issues with `gh issue create --title "..." --body-file <file> --label "ready-for-agent"`.
- Read an issue and its comments with `gh issue view <number> --comments`.
- List issues with labels and comments using `gh issue list --state open --json number,title,body,labels,comments`.
- Comment with `gh issue comment <number> --body "..."`.
- Add or remove labels with `gh issue edit <number> --add-label "..."` or `--remove-label "..."`.
- Close an issue only when the user or the originating workflow asks for it.
- When a skill says to publish to the issue tracker, create a GitHub issue.
- PRs are not a request surface for triage.

## Dependencies

Use GitHub's native issue dependencies for blocking relationships when available. Otherwise include a `Blocked by: #<number>` line in the issue body.
