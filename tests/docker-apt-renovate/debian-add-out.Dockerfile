FROM debian:13.2@sha256:c71b05eac0b20adb4cdcc9f7b052227efd7da381ad10bb92f972e8eae7c6cdc9

# renovate: suite=trixie depName=samba
ENV SAMBA_VERSION="2:4.22.6+dfsg-0+deb13u1"
# renovate: suite=trixie depName=cifs-utils
ENV CIFSUTILS_VERSION="2:7.4-1"

# renovate: suite=trixie depName=curl
ENV CURL_VERSION="8.14.1-2+deb13u2"
# renovate: suite=trixie depName=gosu
ENV GOSU_VERSION="1.17-3"
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        samba=${SAMBA_VERSION} \
        cifs-utils=${CIFSUTILS_VERSION} \
        # Also tests comments \
        # Some unnecessary package: ffmpeg \
        # Also tests multiple on one line doesn't result in an empty line \
        # curl also tests multiple versions. Had warning when using API, html implementation does this fine. \
        # gosu also tests "and others" \
        curl=${CURL_VERSION} \
        gosu=${GOSU_VERSION} \
    && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
    && apt-get clean

# renovate: suite=trixie depName=curl
ENV CURL_VERSION="8.14.1-2+deb13u2"
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        samba=${SAMBA_VERSION} \
        cifs-utils=${CIFSUTILS_VERSION} \
        curl=${CURL_VERSION}

# renovate: suite=trixie depName=curl
ENV CURL_VERSION="8.14.1-2+deb13u2"
# renovate: suite=trixie depName=gosu
ENV GOSU_VERSION="1.17-3"
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        samba=${SAMBA_VERSION} \
        cifs-utils=${CIFSUTILS_VERSION} \
        curl=${CURL_VERSION} \
        gosu=${GOSU_VERSION}
