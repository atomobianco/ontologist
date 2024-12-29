# Branch Naming

A git branch should start with a category. Pick one of these: `feature`, `bugfix`, `hotfix`, or `test`.

- `feature` is for adding, refactoring or removing a feature
- `fix` is for fixing a bug
- `test` is for experimenting outside an issue/ticket

After the category, there should be a "/" followed by a description which sums up the purpose of this specific branch. This description should be short and "kebab-cased".

# Commit Naming

A commit message should start with a category of change.
You can pretty much use the following 4 categories for everything: `feat`, `fix`, `refactor`, and `chore`:

- `feat` is for adding a new feature
- `fix` is for fixing a bug
- `refactor` is for changing code for performance or convenience purpose (e.g. readibility)
- `chore` is for everything else (writing documentation, formatting, adding tests, cleaning useless code etc.)

After the category, there should be a ":" announcing the commit description.

# Code Development

- Use types whenever possible.
- Use pytest for testing.
- Compose code without comments, but existing comments should remain.
