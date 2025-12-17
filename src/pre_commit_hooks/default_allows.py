from __future__ import annotations


# TODO(GideonBear): populate these automatically from top X docker images and GH actions
default_allows = {
    "docker": {
        "debian": "major-minor",
        "postgres": "major-minor",
        "erikvl87/languagetool": "major-minor",
        "atdr.meo.ws/archiveteam/warrior-dockerfile": "latest",
        "lukaszlach/docker-tc": "latest",
    },
    "gha": {
        # This action has a branch for each possible Rust version
        # (stable, nightly, 1.80, etc.), and does not use normal versioning.
        # Normal use includes
        # `dtolnay/rust-toolchain@stable` and `dtolnay/rust-toolchain@1.88`.
        # Let's give this a pass, even from the digest, to avoid making it
        # too confusing.
        "dtolnay/rust-toolchain": "no-digest-mutable-rev",
    },
}
