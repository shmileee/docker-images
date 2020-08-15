#!/usr/bin/env python3
#
# build.py
# Script to build multiple Docker images.
#
##

import datetime
import glob
import json
import os
import sys
import subprocess

import requests
import yaml

DEBUG = os.getenv("DEBUG")
DRY_RUN = os.getenv("DRY_RUN")

DOCKER_API_URL = "https://hub.docker.com/v2"
DOCKER_REPOSITORY = os.getenv("DOCKER_REPOSITORY", "docker.io/shmileee")
DOCKER_LOGIN = os.getenv("DOCKER_LOGIN", "shmileee")
DOCKER_PASSWORD = os.getenv("DOCKER_PASSWORD", "")

IMAGES_DIR = os.getenv("IMAGES_DIR", "images")
IMAGE = os.getenv("IMAGE", "all")
ENABLE_PUSH = os.getenv("ENABLE_PUSH")

DEFAULTS = {
    "dockerfile": "Dockerfile",
    "specfile": "buildspec.yml",
    "readme": "README.md",
}


class bcolors:
    NORMAL = "\033[0m"
    BLUE = "\033[1;94m"
    GREEN = "\033[1;92m"
    YELLOW = "\033[1;93m"
    RED = "\033[1;91m"


class cd:
    """Context manager for changing the current working directory."""

    def __init__(self, new_path):
        self.new_path = os.path.expanduser(new_path)

    def __enter__(self):
        self.saved_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)


def show_debug(message: str) -> None:
    """Show a debug message."""
    if DEBUG:
        print(f"{bcolors.BLUE}[DEBG] {message}{bcolors.NORMAL}")


def show_info(message: str) -> None:
    """Show an information message."""
    print(f"{bcolors.GREEN}[INFO] {message}{bcolors.NORMAL}")


def show_warn(message: str) -> None:
    """Show a warning message."""
    print(f"{bcolors.YELLOW}[WARN] {message}{bcolors.NORMAL}", file=sys.stderr)


def show_error(message: str, **kwargs) -> None:
    """Show an error message."""
    print(f"{bcolors.RED}[ERROR] {message}{bcolors.NORMAL}", file=sys.stderr)

    if kwargs.get("exit"):
        sys.exit(1)


def get_image_dirs(image_name: str) -> list:
    """Return a list of all image directories."""
    glob_path = "*" if image_name == "all" else image_name

    glob_result = glob.glob(os.path.join(os.getcwd(), IMAGES_DIR, glob_path))

    image_dirs = [i for i in glob_result if os.path.isdir(i)]

    return sorted(image_dirs)


def run_cmd(command: list) -> None:
    """Run `command` using `subprocess.Popen()`."""
    show_info(f"Command: {' '.join(command)}")

    if DRY_RUN:
        show_info("Dry run mode enabled - won't run")
    else:
        try:
            proc = subprocess.Popen(command, stdout=subprocess.PIPE)
            stdout = proc.communicate()[0]
        except Exception as exc:
            show_error(exc, exit=1)
        finally:
            return stdout.decode("utf-8").rstrip("\n")


def push_image(image: str) -> None:
    if not ENABLE_PUSH:
        show_info("Not pushing - ENABLE_PUSH not set")
        return

    run_cmd(["docker", "image", "push", image])


def build_image(image_spec: dict, build_dir: str) -> None:
    """Build a Docker image in `build_dir` based on `image_spec`."""
    image_name = image_spec["name"]
    vcs_ref = run_cmd(["git", "rev-parse", "--short", "HEAD"])
    build_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    for tag in image_spec.get("tags"):
        tag_name = tag["name"]
        tag_aliases = tag.get("aliases", [])
        build_args = tag.get("build_args", [])
        dockerfile = tag.get("dockerfile", DEFAULTS["dockerfile"])
        readme = tag.get("readme", DEFAULTS["readme"])

        image_repo = f"{DOCKER_REPOSITORY}/{image_name}"
        image_fullname = f"{image_repo}:{tag_name}"

        docker_build_cmd = [
            "docker",
            "image",
            "build",
            "--rm",
            "--force-rm",
            f"--file={dockerfile}",
            f"--build-arg=VCS_REF={vcs_ref}",
            f"--build-arg=BUILD_DATE={build_date}",
            f"--tag={image_fullname}",
            ".",
        ]

        for build_arg in build_args:
            docker_build_cmd.append(f"--build-arg={build_arg}")

        show_info(f"Entering directory {build_dir}")
        show_info(f"Image: {image_fullname}")

        with cd(build_dir):
            run_cmd(docker_build_cmd)
            push_image(image_fullname)
            update_readme(image_name=image_name, readme_path=readme)

            for tag_alias in tag_aliases:
                image_alias_name = f"{image_repo}:{tag_alias}"

                show_info(f"Tag alias: {image_alias_name}")

                docker_tag_cmd = [
                    "docker",
                    "image",
                    "tag",
                    image_fullname,
                    image_alias_name,
                ]

                run_cmd(docker_tag_cmd)
                push_image(image_alias_name)


def load_specfile(filepath: str) -> dict:
    """Parse a spec file and return its data as a dict."""
    buildspec = {}

    with open(filepath, "r") as spec_file:
        show_debug(f"Using file {filepath}")

        try:
            buildspec = yaml.safe_load(spec_file)
        except yaml.YAMLError as exc:
            show_error(exc, exit=1)

        show_debug(f"Buildspec: {buildspec}")

    return buildspec


def build_all_images(image_dirs: list) -> None:
    """Build all images found in `image_dirs`."""
    show_debug(f"Searching directories: {image_dirs}")

    specfile = DEFAULTS["specfile"]

    for image_dir in image_dirs:
        spec_filepath = os.path.join(image_dir, specfile)

        if not os.path.exists(spec_filepath):
            show_info(f"Ignoring {image_dir} - file {specfile} not found")
            continue

        buildspec = load_specfile(spec_filepath)

        for image in buildspec["images"]:
            build_image(image_spec=image, build_dir=image_dir)


def get_docker_token() -> str:
    """Retrieve DockerHub token."""
    r = requests.post(
        f"{DOCKER_API_URL}/users/login",
        data={"username": DOCKER_LOGIN, "password": DOCKER_PASSWORD},
    )

    return r.json()["token"]


def update_readme(image_name: str, readme_path: str) -> str:
    """Update README section on DockerHub."""
    show_info(f"Updating README seciton for {image_name}")

    repo = DOCKER_REPOSITORY.split("/")[-1]
    uri = f"{DOCKER_API_URL}/repositories/{repo}/{image_name}/"

    with open(readme_path) as fd:
        readme_content = fd.read()

    token = get_docker_token()
    _ = requests.patch(
        uri,
        data=json.dumps({"full_description": readme_content}),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"JWT {token}",
        },
    )


def main():
    """Entrypoint function."""
    image_dirs = get_image_dirs(image_name=IMAGE)

    if len(image_dirs) == 0:
        show_info(f"No image directories found in '{IMAGES_DIR}/' - exiting")
        sys.exit(0)

    build_all_images(image_dirs)


if __name__ == "__main__":
    main()
