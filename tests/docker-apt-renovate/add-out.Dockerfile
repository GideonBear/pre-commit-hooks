FROM debian:13.2@sha256:c71b05eac0b20adb4cdcc9f7b052227efd7da381ad10bb92f972e8eae7c6cdc9

# renovate: suite=trixie depName=samba
ENV SAMBA_VERSION="2:4.22.6+dfsg-0+deb13u1"
# renovate: suite=trixie depName=cifs-utils
ENV CIFSUTILS_VERSION="2:7.4-1"

# renovate: suite=trixie depName=curl
ENV CURL_VERSION="8.14.1-2+deb13u2"
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        samba=${SAMBA_VERSION} \
        cifs-utils=${CIFSUTILS_VERSION} \
        curl=${CURL_VERSION} \
    && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
    && apt-get clean \
    && mkdir /mnt/remotedir \
    && chmod 777 /mnt/remotedir \
    && touch /etc/win-credentials \
    && chown root /etc/win-credentials \
    && chmod 600 /etc/win-credentials

COPY entrypoint.sh /usr/bin
RUN chmod +x /usr/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]
