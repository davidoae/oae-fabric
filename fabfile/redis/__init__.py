from fabric.api import task
from fabric.operations import run


@task
def start():
    """Start the Redis service."""
    run("service redis-server start")


@task
def stop():
    """Stop the Redis service."""
    run("service redis-server stop")


@task
def delete_data():
    """Delete the Redis data."""
    run("redis-cli flushall")
