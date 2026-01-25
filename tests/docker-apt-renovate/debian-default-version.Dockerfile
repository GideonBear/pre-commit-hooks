FROM atdr.meo.ws/archiveteam/warrior-dockerfile:latest@sha256:0404579c23edf10f722d6efc02d026721936ffd3531e303b8f9c071cc8de4788

# renovate: suite=trixie depName=samba
ENV SAMBA_VERSION="2:4.22.6+dfsg-0+deb13u1"
RUN apt-get update \
    && apt-get install -y --no-install-recommends samba cifs-utils \  # Error: the hook doesn't know what version of Debian this is. Use an image with the Debian codename in the tag (like python:3.14-trixie), or put a comment after the `FROM` line, like `# docker-apt-renovate: FROM debian:trixie`, to make the Debian version explicit.
    && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
    && apt-get clean

COPY entrypoint.sh /usr/bin
RUN chmod +x /usr/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]
