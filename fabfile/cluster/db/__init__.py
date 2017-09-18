from time import sleep
from fabric.api import env, runs_once, settings, task
from fabric.operations import prompt
from fabric.tasks import execute
from getpass import getpass
from .. import hosts as cluster_hosts, util as cluster_util
from ... import db, hilary, puppet

__all__ = ["upgrade", "upgrade_host", "restore_backups"]  # , "delete_data"]


@runs_once
@task
def upgrade():
    """Runs through a general upgrade procedure for a set of Cassandra nodes.

        This will:

            1.  Perform a git pull on the puppet node to get the latest
                configuration
            2.  Run puppet on each db node
            3.  On each db node sequentially:
                    a. Run nodetool drain
                    b. Restart dse
                    c. Run nodetool upgradesstables
    """

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

            1.  Forcefully stop any current puppet runs
            2.  Run puppet on the node
            3.  Run nodetool drain
            4.  Restart dse
            5.  Run nodetool upgradesstables
    """

    execute(puppet.stop, force=True)
    execute(upgrade_host_internal)
    execute(puppet.start)

@runs_once
@task
def restore_backups():
    """Run through the S3 backup restore procedure

        This will:

            1.  Ask for the AWS public and secret key
            2.  Ask for the public key id that was used to encrypt the backups
            3.  Ensure the necessary duplicity tooling is installed
            4.  Forcefully stop any current puppet runs
            5.  Stop dse
            6.  Remove everything under /data/cassandra
    """

    prompt("The AWS key ID:", key="backups_aws_key_id")
    env.backups_aws_secret_access_key = getpass('The AWS secret access key: ')
    prompt("The GPG encrypt key:", key="backups_encrypt_key")
    env.backups_encrypt_passphrase = getpass('The gnuPG passphrase: ')
    prompt("The S3 bucket:", key="backups_bucket_name")

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
