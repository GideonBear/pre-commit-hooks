FROM atdr.meo.ws/archiveteam/warrior-dockerfile:latest@sha256:0404579c23edf10f722d6efc02d026721936ffd3531e303b8f9c071cc8de4788
# docker-apt-renovate: FROM debian:forky

# renovate: suite=forky depName=samba
ENV SAMBA_VERSION="2:4.23.4+dfsg-1"
# renovate: suite=forky depName=cifs-utils
ENV CIFSUTILS_VERSION="2:7.4-1"
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        samba=${SAMBA_VERSION} \
        cifs-utils=${CIFSUTILS_VERSION} \
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
