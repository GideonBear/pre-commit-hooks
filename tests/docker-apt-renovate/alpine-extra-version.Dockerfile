FROM python:3.14.2-alpine3.23@sha256:foo

RUN apk add --no-cache curl jq  # Error: [unpinned] 'curl' is unpinned |AND| Error: [unpinned] 'jq' is unpinned
