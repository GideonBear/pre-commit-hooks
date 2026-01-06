FROM debian:14.0@sha256:foo

# renovate: suite=trixie depName=samba  # Error: [wrong-suite] suite set to `trixie`, while FROM image suggests suite `forky`
ENV SAMBA_VERSION="2:4.22.6+dfsg-0+deb13u1"
# renovate: suite=trixie depName=cifs-utils  # Error: [wrong-suite] suite set to `trixie`, while FROM image suggests suite `forky`
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
