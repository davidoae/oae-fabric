from fabric.api import env, task
from fabric.operations import sudo


@task
def clean():
    """Remove all the code from the deployed OAE ui directory."""
    sudo("rm -rf /tmp/ui_backup", warn_only=True)

    # Ditch the ui directory, only if it exists
    if not sudo("test -d %s" % env.ui_dir, warn_only=True).failed:
        sudo("mv %s /tmp/ui_backup" % env.ui_dir)


@task
def version():
    """Determine the installed version of the ui."""
    sudo("cat /opt/3akai-ux/build-info.json")
