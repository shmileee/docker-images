FROM {{ cookiecutter.base_image }}

ARG VCS_REF
ARG BUILD_DATE

# Metadata
LABEL maintainer="{{ cookiecutter.maintainer_name }} <{{ cookiecutter.maintainer_email }}>" \
      org.label-schema.url="{{ cookiecutter.repo_url }}/images/{{ cookiecutter.image_type.split('::') | first | trim }}/{{ cookiecutter.image_slug }}/" \
      org.label-schema.build-date=${BUILD_DATE} \
      org.label-schema.vcs-url="{{ cookiecutter.vcs_url }}" \
      org.label-schema.vcs-ref=${VCS_REF} \
      org.label-schema.vcs-type="Git" \
      org.label-schema.docker.dockerfile="Dockerfile" \
      org.label-schema.docker.cmd="docker run -it --name {{ cookiecutter.image_slug }} {{ cookiecutter.image_slug }}" \
      org.label-schema.description="{{ cookiecutter.image_description }}" \
      org.label-schema.usage="{{ cookiecutter.repo_url }}/images/{{ cookiecutter.image_type.split('::') | first | trim }}/{{ cookiecutter.image_slug }}/README.md" \
      org.label-schema.schema-version="1.0" \
      com.shmileee.image-type="{{ cookiecutter.image_type.split('::') | first | trim }}"

ARG sometool_version=1.0
ENV SOMETOOL_VERSION ${sometool_version}

{% if "python" in cookiecutter.base_image -%}
RUN set -eux ; \
    apk add --no-cache \
        dependency1 \
        dependency2 ; \
    pip install \
        "sometool==${SOMETOOL_VERSION}" ; \
    \
    dependency1 --version ; \
    dependency2 --version ; \
    some-tool --version ; \
    \
    rm -rf ~/.cache
{% else -%}
RUN set -eux ; \
    wget -q -O /usr/local/bin/some-tool https://github.com/some-user/some-tool/releases/download/${SOMETOOL_VERSION}/some-tool-linux-amd64 ; \
    chmod -v 755 /usr/local/bin/some-tool
{%- endif %}

CMD ["some-tool", "--version"]
