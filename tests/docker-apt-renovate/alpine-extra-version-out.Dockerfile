FROM python:3.14.2-alpine3.23@sha256:foo

# renovate: datasource=repology depName=alpine_3_23/curl
ENV CURL_VERSION="8.17.0-r1"
# renovate: datasource=repology depName=alpine_3_23/jq
ENV JQ_VERSION="1.8.1-r0"
RUN apk add --no-cache \
        curl=${CURL_VERSION} \
        jq=${JQ_VERSION}
