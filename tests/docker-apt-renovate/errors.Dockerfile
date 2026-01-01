FROM debian:oldoldstable@sha256:foo  # Error: [dynamic-suite] using dynamic suite name ('oldoldstable'), which breaks this hook. Use the codename ('bullseye') or version number ('11') instead.
FROM debian:oldstable@sha256:foo  # Error: [dynamic-suite] using dynamic suite name ('oldstable'), which breaks this hook. Use the codename ('bookworm') or version number ('12') instead.
FROM debian:stable@sha256:foo  # Error: [dynamic-suite] using dynamic suite name ('stable'), which breaks this hook. Use the codename ('trixie') or version number ('13') instead.
FROM debian:testing@sha256:foo  # Error: [dynamic-suite] using dynamic suite name ('testing'), which breaks this hook. Use the codename ('forky') or version number ('14') instead.
FROM debian:unstable@sha256:foo
FROM debian:oldoldstable-slim@sha256:foo  # Error: [dynamic-suite] using dynamic suite name ('oldoldstable'), which breaks this hook. Use the codename ('bullseye') or version number ('11') instead.
FROM debian:oldstable-slim@sha256:foo  # Error: [dynamic-suite] using dynamic suite name ('oldstable'), which breaks this hook. Use the codename ('bookworm') or version number ('12') instead.
FROM debian:stable-slim@sha256:foo  # Error: [dynamic-suite] using dynamic suite name ('stable'), which breaks this hook. Use the codename ('trixie') or version number ('13') instead.
FROM debian:testing-slim@sha256:foo  # Error: [dynamic-suite] using dynamic suite name ('testing'), which breaks this hook. Use the codename ('forky') or version number ('14') instead.
FROM debian:unstable-slim@sha256:foo

FROM debian:foo  # Error: [unknown-debian-version] unknown debian version 'foo'

# renovate: suite=foo depName=samba  # Error: [renovate-unknown-debian-version] unknown debian version 'foo'
# renovate: suite=13 depName=samba  # Error: [renovate-unknown-debian-version] unknown debian version '13' (hint: this doesn't accept numeric versions. Did you mean 'trixie'?)
