FROM releaseargus/argus:0.26.3.0@sha256:4f3ae64ad26e22f62a237277ef6e82229ff833adba77def32694e7b1db964a7a  # Error: [weird-version] version contains more than three parts (major.minor.patch.???)
FROM releaseargus/argus:0.26.3@sha256:4f3ae64ad26e22f62a237277ef6e82229ff833adba77def32694e7b1db964a7a
FROM releaseargus/argus:0.26@sha256:4f3ae64ad26e22f62a237277ef6e82229ff833adba77def32694e7b1db964a7a  # Error: [major-minor] version contains only two parts (major.minor). Can the version be pinned further?
FROM releaseargus/argus:0@sha256:4f3ae64ad26e22f62a237277ef6e82229ff833adba77def32694e7b1db964a7a  # Error: [major] version contains only one part (major). Can the version be pinned further?

FROM releaseargus/argus:0.26.3-alpine@sha256:4f3ae64ad26e22f62a237277ef6e82229ff833adba77def32694e7b1db964a7a
FROM releaseargus/argus:0.26-alpine@sha256:4f3ae64ad26e22f62a237277ef6e82229ff833adba77def32694e7b1db964a7a  # Error: [major-minor] version contains only two parts (major.minor). Can the version be pinned further?
FROM releaseargus/argus:0-alpine@sha256:4f3ae64ad26e22f62a237277ef6e82229ff833adba77def32694e7b1db964a7a  # Error: [major] version contains only one part (major). Can the version be pinned further?

FROM releaseargus/argus:latest@sha256:4f3ae64ad26e22f62a237277ef6e82229ff833adba77def32694e7b1db964a7a  # Error: [latest] uses dynamic tag 'latest' instead of pinned version
FROM releaseargus/argus:stable@sha256:4f3ae64ad26e22f62a237277ef6e82229ff833adba77def32694e7b1db964a7a  # Error: [stable] uses dynamic tag 'stable' instead of pinned version
FROM releaseargus/argus:dev@sha256:4f3ae64ad26e22f62a237277ef6e82229ff833adba77def32694e7b1db964a7a  # Error: [mutable-rev] used revision is not a version. Can you use a tag instead?

FROM releaseargus/argus:0.26.3  # Error: no '@'
FROM releaseargus/argus:0.26  # Error: no '@'
FROM releaseargus/argus:0  # Error: no '@'
FROM releaseargus/argus:latest  # Error: no '@'

FROM releaseargus/argus@sha256:4f3ae64ad26e22f62a237277ef6e82229ff833adba77def32694e7b1db964a7a  # Error: no ':' in leading part
FROM releaseargus/argus:0.26.3@4f3ae64ad26e22f62a237277ef6e82229ff833adba77def32694e7b1db964a7a  # Error: invalid digest (doesn't start with 'sha256:')
FROM releaseargus/argus:0.26.3@sha256:4f3ae64ad26e22f62a237277ef6e82229ff833adba77def32694e7b1db964a7  # Error: invalid sha256 digest ('4f3ae64ad26e22f62a237277ef6e82229ff833adba77def32694e7b1db964a7')

FROM lukaszlach/docker-tc:latest@sha256:faefaa9230b77acc95acceff073791c682339676e2de129f5221abb206d1e310

# Multiple dashes
FROM python:3.14.2-slim-bookworm@sha256:404ca55875fc24a64f0a09e9ec7d405d725109aec04c9bf0991798fd45c7b898
FROM python:3.14.2-slim-bookworm@sha256:404ca55875fc24a64f0a09e9ec7d405d725109aec04c9bf0991798fd45c7b89  # Error: invalid sha256 digest ('404ca55875fc24a64f0a09e9ec7d405d725109aec04c9bf0991798fd45c7b89')
