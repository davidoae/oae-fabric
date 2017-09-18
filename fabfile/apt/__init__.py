from fabric.api import task
from fabric.operations import run


@task
def update():
    """Update the aptitude cache."""
    run("apt-get update")
