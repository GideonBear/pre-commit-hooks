FROM debian:14.0@sha256:foo

# renovate: suite=forky depName=samba
ENV SAMBA_VERSION="2:4.23.4+dfsg-1"
# renovate: suite=forky depName=cifs-utils
ENV CIFSUTILS_VERSION="2:7.4-1"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        samba=${SAMBA_VERSION} \
        cifs-utils=${CIFSUTILS_VERSION} \
    && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
    && apt-get clean

COPY entrypoint.sh /usr/bin
RUN chmod +x /usr/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]
