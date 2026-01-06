FROM alpine:3.23.2@sha256:865b95f46d98cf867a156fe4a135ad3fe50d2056aa3f25ed31662dff6da4eb62

# renovate: datasource=repology depName=alpine_3_23/curl
ENV CURL_VERSION="8.17.0-r1"
# renovate: datasource=repology depName=alpine_3_23/jq
ENV JQ_VERSION="1.8.1-r0"
RUN apk add --no-cache \
        curl=${CURL_VERSION} \
        jq=${JQ_VERSION}
