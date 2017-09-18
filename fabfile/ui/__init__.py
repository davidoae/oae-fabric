from fabric.api import env, task
from fabric.operations import run


@task
def clean():
    """Remove all the code from the deployed OAE ui directory."""
    run("rm -rf /tmp/ui_backup", warn_only=True)

    # Ditch the ui directory, only if it exists
    if not run("test -d %s" % ui_dir(), warn_only=True).failed:
        run("mv %s /tmp/ui_backup" % ui_dir())


@task
def version():
    """Determine the installed version of the ui."""
    run("cat %s/build-info.json" % ui_dir())


def ui_dir():
    return getattr(env, 'ui_dir', '/opt/3akai-ux')
