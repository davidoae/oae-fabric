from fabric.api import env, task
from fabric.operations import sudo


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
    if not sudo("test -d %s" % env.hilary_dir, warn_only=True).failed:
        sudo("mv %s /tmp/hilary_backup" % env.hilary_dir)


@task
def version():
    """Determine the installed version of hilary."""
    sudo("cat /opt/oae/build-info.json")
