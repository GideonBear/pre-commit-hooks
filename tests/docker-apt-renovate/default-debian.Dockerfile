FROM atdr.meo.ws/archiveteam/warrior-dockerfile:latest@sha256:0404579c23edf10f722d6efc02d026721936ffd3531e303b8f9c071cc8de4788

RUN apt-get update \
    && apt-get install -y --no-install-recommends samba cifs-utils \  # Warning: assuming Debian 'stable' (currently 'trixie'). Use an image with the Debian codename in the tag (like python:3.14-bookworm), or put a comment after the `FROM` line, like `# docker-apt-renovate: FROM debian:trixie`, to make the Debian version explicit. |AND| Error: [unpinned] 'samba' is unpinned |AND| Error: [unpinned] 'cifs-utils' is unpinned
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
