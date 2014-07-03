from time import sleep
from fabric.api import env, task
from fabric.operations import run, sudo


@task
def start():
    """Start the database service."""
    sudo("service dse start")


@task
def stop():
    """Stop the database service."""
    sudo("service dse stop", warn_only=True)


@task
def delete_data():
    """Delete the database data."""
    sudo("rm -rf %s" % db_data_dir())
    sudo("rm -rf %s" % db_saved_caches_dir())
    sudo("rm -rf %s" % db_commitlog_dir())


@task
def wait_until_ready():
    """Wait until the database is ready to handle requests."""

    # Create a script that basically just tests if we can connect and then
    # disconnect
    sudo("echo 'exit;' > /tmp/test_availability.cql3")
    cqlsh = "cqlsh -3 -f /tmp/test_availability.cql3"

    # Keep trying to run the script until it is successful
    if run(cqlsh, warn_only=True).failed:
        sleep(1)

        while run(cqlsh, warn_only=True).failed:
            sleep(1)


@task
def upgradesstables():
    """Run the nodetool upgradesstables process."""
    sudo("nodetool upgradesstables")


@task
def drain():
    """Drain the commitlog of the database."""
    sudo("nodetool drain")


def db_data_dir():
    return getattr(env, 'db_data_dir', '/data/cassandra')


def db_saved_caches_dir():
    return getattr(env, 'db_saved_caches_dir', '/var/lib/cassandra/saved_caches')


def db_commitlog_dir():
    return getattr(env, 'db_commitlog_dir', '/var/lib/cassandra/commitlog')
