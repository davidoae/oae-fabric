from time import sleep
from fabric.api import env, task
from fabric.context_managers import shell_env
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
def kill():
    """Kill -9 all Java processes on the system."""
    sudo("killall -9 java", warn_only=True)


@task
def delete_data():
    """Delete the database data."""
    sudo("rm -rf %s" % db_data_dir())
    sudo("rm -rf %s" % db_saved_caches_dir())
    sudo("rm -rf %s" % db_commitlog_dir())


@task
def install_duplicity():
    """Install duplicity"""
    sudo("apt-get install -y duplicity python-pip")
    sudo("pip install boto")


@task
def restore_backups():
    """Restore the backups from S3 with duplicity"""
    with shell_env(AWS_ACCESS_KEY_ID=backups_aws_key_id(), AWS_SECRET_ACCESS_KEY=backups_aws_secret_access_key()):
        encrypt_key = backups_encrypt_key()
        bucket_name = backups_bucket_name()
        sudo("echo duplicity --s3-use-new-style --encrypt-key=%s restore s3+http://%s/%s/cassandra /data/cassandra/data" % (encrypt_key, bucket_name, env.host))


@task
def wait_until_ready():
    """Wait until the database is ready to handle requests."""

    # Create a script that basically just tests if we can connect and then
    # disconnect
    sudo("echo 'exit;' > /tmp/test_availability.cql3")
    cqlsh = "cqlsh -f /tmp/test_availability.cql3"

    # Keep trying to run the script until it is successful
    if run(cqlsh, warn_only=True).failed:
        sleep(1)

        while run(cqlsh, warn_only=True).failed:
            sleep(1)

    # Even after cqlsh is successful, we need to wait a while before the
    # server is available for queries
    sleep(15)


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


def backups_bucket_name():
    return getattr(env, 'backups_bucket_name', 'oae-cassandra-backup')

def backups_aws_key_id():
    return getattr(env, 'backups_aws_key_id', '')

def backups_aws_secret_access_key():
    return getattr(env, 'backups_aws_secret_access_key', '')

def backups_encrypt_key():
    return getattr(env, 'backups_encrypt_key', '')
