from fabric.api import task
from fabric.operations import sudo


@task
def start():
    """Start the Redis service."""
    sudo("service redis-server start")


@task
def stop():
    """Stop the Redis service."""
    sudo("service redis-server stop")


@task
def delete_data():
    """Delete the Redis data."""
    sudo("redis-cli flushall")
