# Docker Images

My collection of Docker images.

## Where are the `Dockerfile`s?

TL;DR:

```sh
find images/ -name 'Dockerfile*' | sort
```

This repository has the following image directories:

- [`images/base/`](images/base/): images derived from external images.  
  Example: `base/pre-commit` is built from `python:3-alpine`.

- [`images/child/`](images/child/): images derived from other images in this repository.  
  Example: `child/molecule` is built from `base/ansible`.

## Where are the images?

All images are [automatically](https://github.com/shmileee/docker-images/actions)
(and regularly) pushed to [Docker Hub](https://hub.docker.com/u/shmileee).

## Building

### Using the build script

Install the script requirements:

```sh
pip install -r builder/requirements.txt
```

Run it:

```sh
# Build all base images
IMAGES_DIR=images/base ./builder/build.py

# Build only the Ansible base image
IMAGES_DIR=images/base IMAGE=ansible ./builder/build.py
```

See the [`build.py` source](builder/build.py) for more options.

### Using `make`

Try the `*-images` targets. Example:

```sh
make base-images
make base-images IMAGE=pre-commit

make child-images

make all-images
```

Run `make help` for all available commands.

## Adding a new image

To add a new image to this repository:

1. Install [Cookiecutter](https://cookiecutter.readthedocs.io/).

2. Run `make new-image` and answer some basic questions.

3. There's no step 3.

## Credits

This repository had been forked from [flaudisio/docker-images](https://github.com/flaudisio/docker-images).
All the credits go to it's original author.

## License

[MIT](LICENSE).
