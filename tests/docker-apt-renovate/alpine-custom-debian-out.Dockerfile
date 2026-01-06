FROM atdr.meo.ws/archiveteam/warrior-dockerfile:latest@sha256:0404579c23edf10f722d6efc02d026721936ffd3531e303b8f9c071cc8de4788
# docker-apt-renovate: FROM alpine:3.22

# renovate: datasource=repology depName=alpine_3_22/curl
ENV CURL_VERSION="8.14.1-r2"
# renovate: datasource=repology depName=alpine_3_22/jq
ENV JQ_VERSION="1.8.1-r0"
RUN apk add --no-cache \
        curl=${CURL_VERSION} \
        jq=${JQ_VERSION}
