# pre-commit-hooks

## Installation

Add the following to your `.pre-commit-config.yaml`:

<!-- bumpsync: "rev: v{}" -->

```yaml
- repo: https://github.com/GideonBear/pre-commit-hooks
  rev: v2.0.3
  hooks:
    - id: ...  # pick hooks from the list below
    - id: ...
```

## Python version support

This project currently supports Python 3.12 and up. This requirement may be increased with a major version bump.
The Python version shipped with the latest stable Debian and latest LTS Ubuntu releases
(currently 3.12 and 3.13 respectively) will always be supported.

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
instead of just the digest, prompting the bot to link/embed the release notes.
Example: [before](https://github.com/GideonBear/smb-reshare/pull/32), [after](https://github.com/GideonBear/smb-reshare/pull/61).

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

Adds `language: system` hooks to `ci: skip:` automatically.

This hook messes up the formatting of `.pre-commit-config.yaml`. It's recommended to use `pre-commit-config-fmt` after
this hook.

## `pre-commit-config-sections-*`

Currently supported:

- `shell` (`types: [shell]`)
- `python` (`types: [python]`)
- `pytest` (`files: ^tests/.*\.py$`)
- `docker` (`files: docker-compose\.ya?ml$|Dockerfile$`)
- `gha` (`files: ^.github/workflows/`)

If a certain type of file is present, expects a section (e.g. `# Shell`) to be present in `.pre-commit-config.yaml`.
This is meant to remind you to add pre-commit hooks when adding a new language to your repository.

## `bumpsync`

Synchronizes the version from `pyproject.toml` to any other file of your choosing.
On the line where the version resides, or any line above it, put:
`bumpsync: "{}"`. This will match on anything matching the regex `[0-9]+\.[0-9]+\.[0-9]+`.
Besides the version (`{}`), other text can be added inside the quotes, to narrow down what to replace.
See this file (README.md) for an example: in the `## Installation` section, `bumpsync` is used to keep
the `.pre-commit-config.yaml` example in sync.

By default `bumpsync` runs on all text files, but you should probably constrain it using `filenames`.

By default `bumpsync` only properly does it's job when running with `--all-files`, e.g. in pre-commit.ci.
If you want `bumpsync` to work locally, set `always_run: true`.

## `docker-apt-renovate`

Helps with pinning Debian (apt) or Alpine (apk) packages in Dockerfiles, and bumping them with Renovate.

This repository contains Renovate presets with `customManagers` that work with `docker-apt-renovate`.
These configs are derived from the Renovate docs
([1](https://docs.renovatebot.com/modules/datasource/deb/#usage-example), [2](https://docs.renovatebot.com/modules/datasource/repology/#description)).
Available presets:

```json5
{
    "extends": [
        // Debian and Alpine, and any future package managers supported by `docker-apt-renovate`
        "github>GideonBear/pre-commit-hooks//renovate/all.json5",
        // Debian only
        "github>GideonBear/pre-commit-hooks//renovate/debian.json5",
        // Alpine only
        "github>GideonBear/pre-commit-hooks//renovate/alpine.json5",
    ],
}
```

If you don't want to use presets, you can copy the configuration
from [those files](https://github.com/GideonBear/pre-commit-hooks/tree/main/renovate) as well. You can edit the managers
as you wish, but keep in mind `docker-apt-renovate` is only guaranteed to work with these presets.

### Command line arguments

- `--indent` (default `4`): set the amount of spaces you want to indent your dockerfile with.

## `pre-commit-config-fmt`

Formats your `.pre-commit-config.yaml` with sensible newlines. If you use any other hooks that modify
`.pre-commit-config.yaml`, like `pre-commit-additional-dependencies` or `pre-commit-ci-skip`, make sure
to put `pre-commit-config-fmt` after them.
