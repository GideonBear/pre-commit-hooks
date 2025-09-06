# docker-image-pin

Based on https://nickcunningh.am/blog/how-to-automate-version-updates-for-your-self-hosted-docker-containers-with-gitea-renovate-and-komodo
```yml
# bad - don't do this
image: gitea/gitea
image: gitea/gitea:latest

# ok - better than nothing, but not specific enough for renovate to do it's job
image: gitea/gitea:1
image: gitea/gitea:1.23

# good - the @sha256 pins latest to a specific build digest, but obfuscates the real version of the image
image: gitea/gitea:latest@sha256:01bb6f98fb9e256554d59c85b9f1cb39f3da68202910ea0909d61c6b449c207d

# better - pins the image to a clear and specific image version
image: gitea/gitea:1.23.6

# best - pins the image to a specific version AND digest, makes the specific version immutable
image: gitea/gitea:1.23.6@sha256:01bb6f98fb9e256554d59c85b9f1cb39f3da68202910ea0909d61c6b449c207d
```
