from time import sleep
from fabric.api import env, task
from fabric.operations import run, sudo


@task
def start():
    """Start the hilary service."""
    sudo("service hilary start")


@task
def stop():
    """Stop the hilary service."""
    sudo("service hilary stop", warn_only=True)


@task
def clean():
    """Remove all the code from the deployed OAE hilary directory and its code backup directory."""
    sudo("rm -rf /tmp/hilary_backup", warn_only=True)

    # Ditch the hilary directory, only if it exists
    if not sudo("test -d %s" % hilary_dir(), warn_only=True).failed:
        sudo("mv %s /tmp/hilary_backup" % hilary_dir())


@task
def version():
    """Determine the installed version of hilary."""
    sudo("cat %s/build-info.json" % hilary_dir())


@task
def wait_until_ready():
    """Wait until the application server is ready to handle requests."""

    curl = "curl -s -w \"%%{http_code}\" -H\"Host: %s\" -o /dev/null http://%s:%s/api/me" % (check_host_header(), check_host(), check_port())

    # See if /api/me returns the proper output
    if not run(curl) == '200':
        sleep(1)

        while not run(curl) == '200':
            sleep(1)


def hilary_dir():
    return getattr(env, 'hilary_dir', '/opt/oae')


def check_host():
    return getattr(env, 'hilary_check_host', 'localhost')


def check_host_header():
    return getattr(env, 'hilary_check_host_header', 'admin.oaeproject.org')


def check_port():
    return getattr(env, 'hilary_check_port', '2000')
