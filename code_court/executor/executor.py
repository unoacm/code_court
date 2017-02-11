#!/usr/bin/env python

import docker

EXECUTOR_IMAGE_NAME = "code-court-executor"

docker_client = docker.from_env()

out = docker_client.containers.run(EXECUTOR_IMAGE_NAME, "echo hello")
