from fabric.api import runs_once, settings, task
from fabric.tasks import execute
from .. import hosts as cluster_hosts, util as cluster_util
from ... import etherpad, puppet

__all__ = ["upgrade", "upgrade_host"]


@runs_once
@task
def reboot():
    """Reboot all the etherpad servers."""
    cluster_util.ensure_sudo_pass()

    with settings(hosts=cluster_hosts.etherpad()):
        execute(etherpad.stop)
        execute(etherpad.start)


@runs_once
@task
def upgrade():
    """Upgrade all Etherpad servers to the version configured in puppet.

       This will:

        1.  Ask for a password with which to sudo. All servers must have the
            same sudo passowrd
        2.  Perform a git pull on the puppet node to get the latest
            configuration
        3.  On each etherpad host:
              a. Forcefully stop puppet on the etherpad hosts and cancel any
                 runs that are currently happening
              b. Stop the etherpad services
              c. Back up the etherpad dir to /tmp/etherpad_backup
              d. Run puppet, which should notice the missing directory and
                 repopulate it with the configured (updated) version of the
                 package
    """
    cluster_util.ensure_sudo_pass()

    # Pull the updated puppet data
    with settings(hosts=[cluster_hosts.puppet()]):
        execute(puppet.git_update)

    # Run all etherpad upgrades in parallel
    with settings(hosts=cluster_hosts.etherpad(), parallel=True):
        execute(upgrade_host_internal)


@runs_once
@task
def upgrade_host(parallel=True):
    """Upgrade the etherpad servers to the version configured in puppet.

       This will:

        1.  Ask for a password with which to sudo. All servers must have the
            same sudo passowrd.
        2.  Forcefully stop puppet and any runs that are currently happening
        3.  Stop the etherpad service
        4.  Back up the hilary app dir to /tmp/hilary_backup
        5.  Back up the ui app dir to /tmp/ui_backup
        6.  Run puppet, which should notice the missing directories and
            repopulate them with the configured (updated) version of the
            packages
    """
    cluster_util.ensure_sudo_pass()

    with settings(parallel=(parallel != "False")):
        execute(upgrade_host_internal)


def upgrade_host_internal():
    puppet.stop(force=True)
    etherpad.stop()
    etherpad.clean()
    puppet.run(force=False)
    puppet.start()
