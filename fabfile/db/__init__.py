from fabric.api import task
from fabric.operations import sudo


@task
def start():
    """Start the etherpad service."""
    sudo("service dse start")


@task
def stop():
    """Stop the etherpad service."""
    sudo("service dse stop", warn_only=True)


@task
def drain():
    """Drain the commitlog of the database."""
    sudo("nodetool drain")


@task
def upgradesstables():
    """Upgrade the SSTables of the database."""
    sudo("nodetool upgradesstables")


@task
def upgrade_reboot():
    """Perform a reboot of the database for purposes of performing a version
    upgrade."""
    drain()
    stop()
    start()
    upgradesstables()
