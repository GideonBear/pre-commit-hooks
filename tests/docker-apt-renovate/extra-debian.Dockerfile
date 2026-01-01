FROM python:3.14.2-slim-trixie@sha256:e8a1ad81a9fef9dc56372fb49b50818cac71f5fae238b21d7738d73ccae8f803

RUN apt-get update \
    && apt-get install -y --no-install-recommends samba cifs-utils \  # Error: [unpinned] 'samba' is unpinned |AND| Error: [unpinned] 'cifs-utils' is unpinned
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
