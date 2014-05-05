from time import sleep
from fabric.api import task
from fabric.operations import run, sudo


@task
def start():
    """Start the search service."""
    sudo("service elasticsearch start", warn_only=True)
    wait_until_ready()


@task
def stop():
    """Stop the search service."""
    sudo("service elasticsearch stop", warn_only=True)
    wait_until_stopped()


@task
def restart():
    """Restart the search service."""
    stop()
    start()


@task
def wait_until_ready():
    """Wait until search is ready to handle requests."""

    curl = "curl -s -w \"%{http_code}\" -o /dev/null http://localhost:9200/"

    # Keep requesting until ElasticSearch returns a 200 response
    if not run(curl, warn_only=True) == '200':
        sleep(1)

        while not run(curl, warn_only=True) == '200':
            sleep(1)


@task
def wait_until_stopped():
    """Wait until search has been fully stopped."""

    # Keep running service status until it starts failing
    if not sudo("service elasticsearch status", warn_only=True).failed:
        sleep(1)

        while not sudo("service elasticsearch status", warn_only=True).failed:
            sleep(1)
