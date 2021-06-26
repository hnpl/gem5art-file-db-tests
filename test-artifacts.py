#!/usr/bin/env python3

from uuid import UUID

from gem5art.artifact import Artifact

Artifact.registerArtifact(
    name = f'test-artifact',
    typ = 'kernel',
    path = f'test-file.txt',
    cwd = './',
    command = 'echo "This is a test file" > test-file.txt',
    inputs = [],
    documentation = f"This is made to test things"
)

