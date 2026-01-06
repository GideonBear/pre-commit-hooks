FROM debian:14@sha256:foo
FROM debian:14
FROM debian:14.0@sha256:foo
FROM debian:14.0
FROM debian:14-slim@sha256:foo
FROM debian:14-slim
FROM debian:14.0-slim@sha256:foo
FROM debian:14.0-slim
FROM debian:bookworm
FROM debian:bookworm@sha256:foo
FROM debian:bookworm-slim
FROM debian:bookworm-slim@sha256:foo

FROM debian:14@sha256:foo AS layer
FROM debian:14 AS layer
FROM debian:14.0@sha256:foo AS layer
FROM debian:14.0 AS layer
FROM debian:14-slim@sha256:foo AS layer
FROM debian:14-slim AS layer
FROM debian:14.0-slim@sha256:foo AS layer
FROM debian:14.0-slim AS layer
FROM debian:bookworm AS layer
FROM debian:bookworm@sha256:foo AS layer
FROM debian:bookworm-slim AS layer
FROM debian:bookworm-slim@sha256:foo AS layer

# Turned into 3.23
FROM alpine:3.23.2
FROM alpine:3.23
FROM alpine:3  # Error: [dynamic-suite] using dynamic suite name ('3'), which breaks this hook. Use the 'x.y' ('3.23') or 'x.y.z' version instead.
FROM alpine:edge
FROM alpine:20251224

FROM debian:latest  # Error: [latest-tag] using dynamic tag ('latest'), which breaks this hook. Use a proper pinned version number or codename instead.

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

FROM debian:trixie
# renovate: suite=foo depName=samba  # Error: [renovate-unknown-debian-version] unknown debian version 'foo'
# renovate: suite=13 depName=samba  # Error: [renovate-unknown-debian-version] unknown debian version '13' (hint: this doesn't accept numeric versions. Did you mean 'trixie'?)
