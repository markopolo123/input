# Chapter 1

The supplied Dockerfile:

```Dockerfile
FROM alpine

ENV POETRY_VERSION=1.1.13 \
HOME=/home/user \
PATH="${HOME}/.local/bin:${PATH}" \
PORT=8080

RUN addgroup user &&\
adduser -S -G user -h $HOME user &&\
apk add --no-cache \
curl \
python3-dev \
gcc \
libressl-dev \
musl-dev \
libffi-dev &&\
curl -sSL https://install.python-poetry.org |\
python3 - --version $POETRY_VERSION &&\
mkdir /home/user/.ssh

COPY app/ /app/
COPY ssh-keys/id_rsa /home/user/.ssh/id_rsa

RUN cd /app && poetry install --no-dev --no-root --no-interaction --no-ansi

USER user

ENTRYPOINT ["poetry", "run"]

CMD ["uvicorn", "--host=0.0.0.0", "--port=$PORT", "--workers=$UVICORN_WORKERS"]
```

## Reviewing the Dockerfile

Thoughts from first read:

* The image built from this Dockerfile is not **immutable**
* The image includes build dependencies
* Poetry may not be needed in the final image
* The image contains a SSH key; directly copying the SSH key is a problem
* Use of Alpine; it *may* be better to use a different base image
* Worker management - set to 1 by default

## Improving the Dockerfile

### Removing Poetry from the Image

Poetry may be removed from the image by using a multi-stage build or by swapping
to `pip` for the final image. This is a matter of preference or use case and
might be that poetry is required due to ways of working, technology choices or
other reasons.

Here is a generic example of using pip in combination with a `pyproject.toml`

file:

```Dockerfile
# syntax = docker/dockerfile:1.3
ARG RUNTIME_VERSION=3.11
FROM python:${RUNTIME_VERSION}-slim-bookworm AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml README.md .
COPY app ./app

RUN --mount=type=secret,id=PIP_INDEX_URL \
    export PIP_INDEX_URL=$(cat /run/secrets/PIP_INDEX_URL) && \
    python${RUNTIME_VERSION} -m pip install -e . && \
    python${RUNTIME_VERSION} -m pip install -e app && \
    python${RUNTIME_VERSION} -m pip cache purge
```

An example of building the above image (including use of a private pip index):

```bash
export CODEARTIFACT_AUTH_TOKEN=$(aws-vault exec dev -- aws codeartifact \
get-authorization-token  --domain somecompany --domain-owner 1234567890 \
| jq -r .authorizationToken)

export PIP_INDEX_URL="https://aws:${CODEARTIFACT_AUTH_TOKEN}\@somecompany-\
1234567890.d.codeartifact.eu-west-2.amazonaws.com/pypi/somecompany/simple/"

docker build -t local-test --secret id=PIP_INDEX_URL,env=PIP_INDEX_URL .

```

### Making the Image Immutable

Pinning the image to a specific version of Alpine Linux can help make the image
more predictable and reproducible. Note that upstream image tags are arbitrary
and may change at any time. If possible, use base images that are maintained by
your organization.

Additionally, it may be important to pin dependencies within the image to
specific versions to ensure that the image is reproducible.

If sticking with alpine and APK, pin package versions in **apk add**. Instead of
`apk add <package>` use `apk add <package>=<version>`

If an SSH key is needed for build time and we can't change that, we have a
few options.

* Multi Stage Build
* BuildKit, Secrets and SSH

### Multi Stage Build

This can alsohelp us with producing a smaller image as well as avoiding us
including the SSH key in the final image (if that key is only required for
building the image). Depending on the use case it may also make builds faster
too.

```Dockerfile
# syntax=docker/dockerfile:1
FROM golang:1.23
WORKDIR /src
COPY <<EOF ./main.go
package main

import "fmt"

func main() {
  fmt.Println("hello, world")
}
EOF
RUN go build -o /bin/hello ./main.go

FROM scratch
COPY --from=0 /bin/hello /bin/hello
CMD ["/bin/hello"]
```

An example build command:

```bash
docker build -t hello .
```

### Buildkit, Secrets and SSH

If you need to pass in secrets, docker buildkit can help with that. More details
[here](https://docs.docker.com/reference/cli/docker/buildx/build/#ssh)

An example Dockerfile:

```Dockerfile
# syntax = docker/dockerfile:1.3
FROM alpine
RUN apk add --no-cache openssh-client
RUN mkdir -p -m 0700 ~/.ssh && ssh-keyscan gitlab.com >> ~/.ssh/known_hosts
RUN --mount=type=ssh ssh -q -T git@gitlab.com 2>&1 | tee /hello
```

And an example build command to pass through our SSH agent:

```bash
docker buildx build --ssh default=$SSH_AUTH_SOCK .
```

Note this would work locally just fine, but in a CI pipeline (especially on
hosted runners) we may require a different approach.

## $UVICORN_WORKERS

Depending on how this image is ulimately used, it may be better to set this to a
default env var of **1**. For instance, if deploying into K8S it may be
desirable to have K8S manage the number of workers via HPA or similar. This will
help with predictable scaling and resource management.
