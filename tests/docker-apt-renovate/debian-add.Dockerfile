FROM debian:13.2@sha256:c71b05eac0b20adb4cdcc9f7b052227efd7da381ad10bb92f972e8eae7c6cdc9

# renovate: suite=trixie depName=samba
ENV SAMBA_VERSION="2:4.22.6+dfsg-0+deb13u1"
# renovate: suite=trixie depName=cifs-utils
ENV CIFSUTILS_VERSION="2:7.4-1"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        samba=${SAMBA_VERSION} \
        cifs-utils=${CIFSUTILS_VERSION} \
        # Also tests comments \
        # Some unnecessary package: ffmpeg \
        # Also tests multiple on one line doesn't result in an empty line \
        # curl also tests multiple versions. Had warning when using API, html implementation does this fine. \
        # gosu also tests "and others" \
        curl gosu \  # Error: [unpinned] 'curl' is unpinned |AND| Error: [unpinned] 'gosu' is unpinned
    && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
    && apt-get clean

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        samba=${SAMBA_VERSION} \
        cifs-utils=${CIFSUTILS_VERSION} \
        curl  # Error: [unpinned] 'curl' is unpinned

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        samba=${SAMBA_VERSION} \
        cifs-utils=${CIFSUTILS_VERSION} \
        curl gosu  # Error: [unpinned] 'curl' is unpinned |AND| Error: [unpinned] 'gosu' is unpinned
