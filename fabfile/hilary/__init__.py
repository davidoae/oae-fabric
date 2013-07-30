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
def clean(force=False):
    """Remove all the code from the deployed OAE ui directory.

    Keyword arguments:
    force --    Whether or not to continue even if the configure 3akai-ux directory does not appear
                to be the correct 3akai-ux directory
    """

    if not sudo("test -d /tmp/hilary_backup", warn_only=True).failed:
        print "Directory /tmp/hilary_backup exists from a previous upgrade. Purge it first with \"fab hilary.purge_clean_backup\""
        raise SystemExit()

    # Assert that the 3akai-ux directory is of expected structure. Only continue if we specified to
    # force
    sudo("test -f %s/app.js" % env.hilary_dir, warn_only=force)

    # Remove the directory if we passed the sanity check
    sudo("mv %s /tmp/hilary_backup" % env.hilary_dir, warn_only=force)


@task
def purge_clean_backup():
    """Remove the backup directory created as a result of cleaning."""
    sudo("rm -rf /tmp/hilary_backup", warn_only=True)


@task
def version():
    """Determine the installed version of hilary."""
    sudo("cat /opt/oae/build-info.json")
