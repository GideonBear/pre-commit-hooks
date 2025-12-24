# pre-commit-hooks

## Installation

Add the following to your `.pre-commit-config.yaml`:

<!-- bumpsync: "rev: v{}" -->

```yaml
- repo: https://github.com/GideonBear/pre-commit-hooks
  rev: v1.8.1
  hooks:
    - id: ...  # pick hooks from the list below
    - id: ...
```

## Python version support

This project currently supports Python 3.12 and up. This requirement may be increased with a major version bump.
These hooks are guaranteed to always work in [pre-commit.ci](https://pre-commit.ci).

# Hooks

## `docker-image-pin` & `gha-pin`

Based
on https://nickcunningh.am/blog/how-to-automate-version-updates-for-your-self-hosted-docker-containers-with-gitea-renovate-and-komodo

```yml
# bad - don't do this
image: gitea/gitea
image: gitea/gitea:latest

# ok - better than nothing, but not specific enough for renovate to do it's job
image: gitea/gitea:1
image: gitea/gitea:1.23

# good - the @sha256 pins latest to a specific build digest, but obfuscates the real version of the image
image: gitea/gitea:latest@sha256:01bb6f98fb9e256554d59c85b9f1cb39f3da68202910ea0909d61c6b449c207d

# better - pins the image to a clear and specific image version
image: gitea/gitea:1.23.6

# best - pins the image to a specific version AND digest, makes the specific version immutable
image: gitea/gitea:1.23.6@sha256:01bb6f98fb9e256554d59c85b9f1cb39f3da68202910ea0909d61c6b449c207d
```

Exactly the same concept applies to GitHub actions.

This has an added benefit when using Dependabot or Renovate, as PRs will bump the version
instead of just the digest, prompting the bot to link/embed the correct release notes
instead of only a compare link.

Certain actions and Docker images are exempted from certain rules by default (for example `debian` which uses `x.y`
versioning). Feel free to contribute
to [default_allows.py](https://github.com/GideonBear/pre-commit-hooks/blob/main/src/pre_commit_hooks/default_allows.py)
with any other known exceptions!

`gha-pin` provides autofixes for most errors. These autofixes use the GitHub API, which means they will not be
available when you are offline, or when running in pre-commit.ci. All error detections still work offline and in
pre-commit.ci.

## `shfuncdecfmt`

```bash
# Bad:
function myfun {
function myfun() {
myfun {
myfun () {
myfun(){

# Good:
myfun() {
```

Formats function declarations accordingly, and fixes whitespace.

## `set-euo-pipefail`

Fails if you don't have `set -euo pipefail` at the top of your shell script.

## `pre-commit-additional-dependencies`

Syncs any `additional_dependencies` in your `.pre-commit-config.yaml` with `uv.lock`. Meant for use with `mirrors-mypy`.

## `pre-commit-ci-skip`

Adds `language: system` hooks to `ci: skip:` automatically

## `pre-commit-config-sections-*`

Currently supported:

- `shell` (`types: [shell]`)
- `python` (`types: [python]`)
- `pytest` (`files: ^tests/.*\.py$`)
- `docker` (`files: docker-compose\.ya?ml$|Dockerfile$`)
- `gha` (`files: ^.github/workflows/`)

If a certain type of file is present, expects a section (e.g. `# Shell`) to be present in `.pre-commit-config.yaml`.
This is meant to remind you to add pre-commit hooks when adding a new language to your repository.

## `requires-python`

Unpins your requires-python from `major.minor.patch` (`>=3.14.2`) to `major.minor` (`>=3.14`)

Designed for use with Renovate:

```json5
{
    packageRules: [
        {
            matchDepTypes: [
                "requires-python",
            ],
            rangeStrategy: "bump",
        },
        {
            matchDepTypes: [
                "requires-python",
            ],
            matchUpdateTypes: "patch",
            enabled: false,
        },
    ],
}
```

Since Renovate always wants to pin it to `major.minor.patch`, and doesn't support anything else.
