FROM python:3.8-alpine

ARG VCS_REF
ARG BUILD_DATE

# Metadata
LABEL maintainer="Oleksandr Ponomarov <ponomarov.aleksandr@gmail.com>" \
      org.label-schema.url="https://github.com/shmileee/docker-images/images/base/pre-commit/" \
      org.label-schema.build-date=${BUILD_DATE} \
      org.label-schema.vcs-url="git@github.com:shmileee/docker-images.git" \
      org.label-schema.vcs-ref=${VCS_REF} \
      org.label-schema.vcs-type="Git" \
      org.label-schema.docker.dockerfile="Dockerfile" \
      org.label-schema.docker.cmd="docker run -it --name pre-commit pre-commit" \
      org.label-schema.description="pre-commit hooks" \
      org.label-schema.usage="https://github.com/shmileee/docker-images/images/base/pre-commit/README.md" \
      org.label-schema.schema-version="1.0" \
      com.shmileee.image-type="base"

WORKDIR /project

ARG pre_commit_version="2.*"
ENV PRE_COMMIT_VERSION ${pre_commit_version}

RUN set -eux ; \
    apk add --no-cache \
        bash \
        curl \
        git \
        openssl \
        make \
        musl-dev \
        go \
        shellcheck ; \
    pip install \
        "pre-commit==${PRE_COMMIT_VERSION}" ; \
    wget -O \
    /usr/local/bin/hadolint \
    https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Linux-x86_64 ; \
    chmod 755 /usr/local/bin/hadolint ;\
    bash --version ; \
    git --version ; \
    python --version ; \
    pip --version ; \
    pre-commit --version ; \
    hadolint --version ; \
    \
    rm -rf ~/.cache

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash

# Configure Go

ENV GOROOT /usr/lib/go
ENV GOPATH /go
ENV PATH /go/bin:$PATH

RUN mkdir -p ${GOPATH}/src ${GOPATH}/bin

CMD ["pre-commit", "--version"]
