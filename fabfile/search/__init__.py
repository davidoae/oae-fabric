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
def delete_index(index_name="oae"):
    """Removes an ElasticSearch index."""
    curl("DELETE", "http://localhost:9200/%s" % index_name, False)


@task
def wait_until_ready():
    """Wait until search is ready to handle requests."""

    # Keep requesting until ElasticSearch returns a 200 response
    if not curl("GET", "http://localhost:9200/") == '200':
        sleep(1)

        while not curl("GET", "http://localhost:9200/") == '200':
            sleep(1)


@task
def wait_until_stopped():
    """Wait until search has been fully stopped."""

    # Keep running service status until it starts failing
    if not sudo("service elasticsearch status", warn_only=True).failed:
        sleep(1)

        while not sudo("service elasticsearch status", warn_only=True).failed:
            sleep(1)


def curl(method, url, warn_only=True):
    """Generate a curl command to perform an HTTP method against a URL. The
    standard output result will be the HTTP status code. This method will
    return the Fabric run execution object."""
    cmd = "curl -s -w \"%%{http_code}\" -o /dev/null -X%s %s" % (method, url)
    return run(cmd, warn_only=warn_only)
