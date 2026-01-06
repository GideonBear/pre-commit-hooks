FROM atdr.meo.ws/archiveteam/warrior-dockerfile:latest@sha256:0404579c23edf10f722d6efc02d026721936ffd3531e303b8f9c071cc8de4788
# docker-apt-renovate: FROM debian:forky

RUN apt-get update \
    && apt-get install -y --no-install-recommends samba cifs-utils \  # Error: [unpinned] 'samba' is unpinned |AND| Error: [unpinned] 'cifs-utils' is unpinned
    && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
    && apt-get clean

COPY entrypoint.sh /usr/bin
RUN chmod +x /usr/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]
