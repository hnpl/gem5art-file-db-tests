import os
import sys
from uuid import UUID
from itertools import starmap
from itertools import product

from gem5art.artifact import Artifact
from gem5art.run import gem5Run

experiments_repo = Artifact.registerArtifact(
    command = 'git clone https://gem5.googlesource.com/public/gem5',
    typ = 'git repo',
    name = 'parsec-test-repo',
    path =  './',
    cwd = '../',
    documentation = 'main repo to run parsec tests with gem5'
)

gem5_repo = Artifact.registerArtifact(
    command = '''
        git clone https://gem5.googlesource.com/public/gem5;
        cd gem5;
        git checkout v21.0.1.0;
    ''',
    typ = 'git repo',
    name = 'gem5',
    path =  'gem5/',
    cwd = './',
    documentation = 'cloned gem5 from the google repository and checked out the v21.0.1.0 version'
)

m5_binary = Artifact.registerArtifact(
    command = 'scons build/x86/out/m5',
    typ = 'binary',
    name = 'm5',
    path =  'gem5/util/m5/build/x86/out/m5',
    cwd = 'gem5/util/m5',
    inputs = [gem5_repo,],
    documentation = 'm5 utility'
)

disk_image = Artifact.registerArtifact(
    command = 'wget http://dist.gem5.org/dist/v20-1/images/x86/ubuntu-18-04/parsec.img.gz; tar xf parsec.img.gz',
    typ = 'disk image',
    name = 'parsec-disk-image',
    cwd = './',
    path = 'parsec.img',
    inputs = [],
    documentation = 'Disk-image using Ubuntu 18.04 with m5 binary and PARSEC installed.',
    supported_gem5_versions = ["v20-1", "v21-0"]
)

gem5_binary = Artifact.registerArtifact(
    command = 'scons build/X86/gem5.fast -j12',
    typ = 'gem5 binary',
    name = 'gem5',
    cwd = 'gem5/',
    path =  'gem5/build/X86/gem5.fast',
    inputs = [gem5_repo,],
    documentation = 'gem5 binary',
    extra = {'abc': 'def'}
)

linux_binary = Artifact.registerArtifact(
    name = 'vmlinux-4.19.83',
    typ = 'kernel',
    path = 'vmlinux-4.19.83',
    cwd = './',
    command = '''
    wget http://dist.gem5.org/dist/v20-1/kernels/x86/static/vmlinux-4.19.83;
    ''',
    inputs = [experiments_repo],
    documentation = "kernel binary for v4.19.83"
)


if __name__ == "__main__":
    benchmarks = ['canneal', 'facesim']

    sizes = ['simsmall']
    cpus = ['kvm']

    def createRun(bench, size, cpu):
        if cpu == 'timing' and size != 'simsmall':
            return 
        return gem5Run.createFSRun(
            'parsec classic memory tests with gem5-21.0.1.0',
            'gem5/build/X86/gem5.fast',
            'configs/run_parsec.py',
            f'''results/run_parsec/{bench}/{size}/{cpu}''',
            gem5_binary, gem5_repo, experiments_repo,
            'vmlinux-4.19.83',
            'parsec',
            linux_binary, disk_image,
            cpu, bench, size, '1',
            timeout = 24*60*60 #24 hours
            )
    # For the cross product of tests, create a run object.
    runs = starmap(createRun, product(benchmarks, sizes, cpus))
    # Run all of these experiments in parallel
    for run in runs:
        run.run()
