from fabric.api import env, task
from fabric.operations import sudo


@task
def clean(force=False):
    """Remove all the code from the deployed OAE ui directory.

    Keyword arguments:
    force --    Whether or not to continue even if the configure 3akai-ux directory does not appear
                to be the correct 3akai-ux directory
    """

    if not sudo("test -d /tmp/ui_backup", warn_only=True).failed:
        print "Directory /tmp/ui_backup exists from a previous upgrade. Purge it first with \"fab ui.purge_clean_backup\""
        raise SystemExit()

    # Assert that the 3akai-ux directory is of expected structure. Only continue if we specified to
    # force
    sudo("test -d %s/optimized" % env.ui_dir, warn_only=force)
    sudo("test -d %s/original" % env.ui_dir, warn_only=force)

    # Remove the directory if we passed the sanity check
    sudo("mv %s /tmp/ui_backup" % env.ui_dir, warn_only=force)


@task
def purge_clean_backup():
    """Remove the backup directory created as a result of cleaning."""
    sudo("rm -rf /tmp/ui_backup", warn_only=True)


@task
def version():
    """Determine the installed version of the ui."""
    sudo("cat /opt/3akai-ux/build-info.json")
