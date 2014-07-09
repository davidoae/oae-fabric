from fabric.api import task
from fabric.operations import sudo


@task
def update():
    """Update the aptitude cache."""
    sudo("apt-get update")
