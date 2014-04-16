from time import sleep
from fabric.api import task
from fabric.operations import run, sudo


@task
def start():
    """Start the etherpad service."""
    sudo("service dse start")


@task
def stop():
    """Stop the etherpad service."""
    sudo("service dse stop", warn_only=True)


@task
def wait_until_ready():
    """Wait until the database is ready to handle requests."""

    # Create a script that basically just tests if we can connect and then
    # disconnect
    sudo("echo 'exit;' > /tmp/test_availability.cql3")
    cqlsh = "cqlsh -3 -f /tmp/test_availability.cql3"

    # Keep trying to run the script until it is successful
    if not run(cqlsh, warn_only=True).code == 0:
        sleep(1)

        while not run(cqlsh, warn_only=True).code == 0:
            sleep(1)


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
    wait_until_ready()
    upgradesstables()
