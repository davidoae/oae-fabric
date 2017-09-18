from fabric.api import env, task
from fabric.operations import run


@task
def start():
    """Start the etherpad service."""
    run("service etherpad start")


@task
def stop():
    """Stop the etherpad service."""
    run("service etherpad stop", warn_only=True)


@task
def clean():
    """Remove all the code from the deployed etherpad directory and its code backup directory."""
    run("rm -rf /tmp/etherpad_backup", warn_only=True)

    # Ditch the etherpad directory, only if it exists
    if not run("test -d %s" % etherpad_dir(), warn_only=True).failed:
        run("mv %s /tmp/etherpad_backup" % etherpad_dir())


@task
def version():
    """Determine the installed version of etherpad."""
    run("cat %s/build-info.json" % etherpad_dir())


def etherpad_dir():
    return getattr(env, 'etherpad_dir', '/opt/etherpad')
