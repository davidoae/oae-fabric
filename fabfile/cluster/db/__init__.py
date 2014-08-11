from time import sleep
from fabric.api import runs_once, settings, task
from fabric.operations import prompt
from fabric.tasks import execute
from .. import hosts as cluster_hosts, util as cluster_util
from ... import db, hilary, puppet

__all__ = ["upgrade", "upgrade_host", "restore_backups"]  # , "delete_data"]


@runs_once
@task
def upgrade():
    """Runs through a general upgrade procedure for a set of Cassandra nodes.

        This will:

            1.  Ask for a password with which to sudo. All servers must have
                the same sudo passowrd
            2.  Perform a git pull on the puppet node to get the latest
                configuration
            3.  Run puppet on each db node
            4.  On each db node sequentially:
                    a. Run nodetool drain
                    b. Restart dse
                    c. Run nodetool upgradesstables
    """
    cluster_util.ensure_sudo_pass()

    # Stop puppet on the db nodes
    with settings(hosts=cluster_hosts.db(), parallel=True):
        execute(puppet.stop, force=True)

    # Stop puppet on the monitor node
    with settings(hosts=[cluster_hosts.monitor()]):
        execute(puppet.stop)

    # Pull the updated puppet configuration
    with settings(hosts=[cluster_hosts.puppet()], parallel=True):
        execute(puppet.git_update)

    # Upgrade each db node sequentially
    with settings(hosts=cluster_hosts.db(), parallel=False):
        execute(upgrade_host_internal)

    # Start puppet on the db nodes
    with settings(hosts=cluster_hosts.db(), parallel=True):
        execute(puppet.start)

     # Start puppet on the monitor node
    with settings(hosts=[cluster_hosts.monitor()]):
        execute(puppet.run)
        execute(puppet.start)


@runs_once
@task
def upgrade_host():
    """Run through the general upgrade procedure for a Cassandra node, assuming
    puppet has already been updated.

        This will:

            1.  Ask for a password with which to sudo
            2.  Forcefully stop any current puppet runs
            3.  Run puppet on the node
            4.  Run nodetool drain
            5.  Restart dse
            6.  Run nodetool upgradesstables
    """
    cluster_util.ensure_sudo_pass()

    execute(puppet.stop, force=True)
    execute(upgrade_host_internal)
    execute(puppet.start)

@runs_once
@task
def restore_backups():
    """Run through the S3 backup restore procedure

        This will:

            1.  Ask for a password with which to sudo
            2.  Ask for the AWS public and secret key
            3.  Ask for the public key id that was used to encrypt the backups
            2.  Ensure the necessary duplicity tooling is installed
            3.  Forcefully stop any current puppet runs
            4.  Stop dse
            5.  Remove everything under /data/cassandra
    """
    cluster_util.ensure_sudo_pass()

    prompt("The AWS key ID:", key="backups_aws_key_id")
    prompt("The AWS secret access key:", key="backups_aws_secret_access_key")
    prompt("The AWS encrypt key:", key="backups_encrypt_key")

    # Stop puppet and DSE on the db nodes
    with settings(hosts=cluster_hosts.db(), parallel=True):
        execute(puppet.stop, force=True)
        execute(db.stop)

    with settings(hosts=cluster_hosts.db(), parallel=True):
        execute(restore_backups_internal)


def upgrade_host_internal():
    db.drain()
    db.stop()
    puppet.run()
    db.start()
    db.wait_until_ready()
    db.upgradesstables()


def hilary_wait_until_ready_internal():
    while not hilary.wait_until_ready(max_retries=15):
        hilary.stop()
        hilary.start()

def restore_backups_internal():
    db.delete_data()
    db.restore_backups()
    db.start()
    db.wait_until_ready()
    puppet.start()
