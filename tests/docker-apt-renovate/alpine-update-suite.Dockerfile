FROM alpine:3.23@sha256:foo

# renovate: datasource=repology depName=alpine_3_22/curl  # Error: [wrong-suite] suite set to `3.22`, while FROM image suggests suite `3.23`
ENV CURL_VERSION="8.14.1-r2"
# renovate: datasource=repology depName=alpine_3_22/jq  # Error: [wrong-suite] suite set to `3.22`, while FROM image suggests suite `3.23`
ENV JQ_VERSION="1.8.1-r0"
RUN apk add --no-cache \
        curl=${CURL_VERSION} \
        jq=${JQ_VERSION}
