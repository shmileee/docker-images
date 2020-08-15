# {{ cookiecutter.image_pretty_name }}

{{ cookiecutter.image_description }}

Documentation: {{ cookiecutter.repo_url }}/images/{{ cookiecutter.image_type.split('::') | first | trim }}/{{ cookiecutter.image_slug }}/README.md

## Usage

```sh
docker run -it --name {{ cookiecutter.image_slug }} {{ cookiecutter.image_slug }}
```
