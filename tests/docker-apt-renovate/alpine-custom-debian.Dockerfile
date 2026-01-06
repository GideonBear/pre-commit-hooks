FROM atdr.meo.ws/archiveteam/warrior-dockerfile:latest@sha256:0404579c23edf10f722d6efc02d026721936ffd3531e303b8f9c071cc8de4788
# docker-apt-renovate: FROM alpine:3.22

RUN apk add --no-cache curl jq  # Error: [unpinned] 'curl' is unpinned |AND| Error: [unpinned] 'jq' is unpinned
