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
        "dtolnay/rust-toolchain": "master",
    },
}

infos = {
    "docker": {},
    "gha": {
        # This action has a branch for each possible Rust version
        # (stable, nightly, 1.80, etc.), and does not use normal versioning.
        # Normal use includes
        # `dtolnay/rust-toolchain@stable` and `dtolnay/rust-toolchain@1.88`.
        # However we do not want to allow this. You should simply specify
        # `with: toolchain: 1.80`, and use a sha pointing to the `master` branch.
        "dtolnay/rust-toolchain": (
            "This action uses special versioning. Specify the Rust toolchain version "
            "using `with: toolchain: <version>` instead, and pin the action to the "
            "latest commit in `master`. See "
            "https://github.com/dtolnay/rust-toolchain#install-rust-toolchain for more "
            "information."
        ),
        "taiki-e/install-action": (
            "This action uses special versioning. Specify the"
            "tool using `with: tool: <tool>` instead, and pin the action to the latest"
            "version. See https://github.com/taiki-e/install-action#example-workflow"
            "for more information."
        ),
    },
}
