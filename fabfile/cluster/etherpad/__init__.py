from fabric.api import runs_once, settings, task
from fabric.tasks import execute
from .. import hosts as cluster_hosts, util as cluster_util
from ... import etherpad, puppet

__all__ = ["reboot", "upgrade", "upgrade_host"]


@runs_once
@task
def reboot():
    """Reboot all the etherpad servers."""

    with settings(hosts=cluster_hosts.etherpad()):
        execute(etherpad.stop)
        execute(etherpad.start)


@runs_once
@task
def upgrade():
    """Upgrade all Etherpad servers to the version configured in puppet.

       This will:

        1.  Perform a git pull on the puppet node to get the latest
            configuration
        2.  On each etherpad host:
              a. Forcefully stop puppet on the etherpad hosts and cancel any
                 runs that are currently happening
              b. Stop the etherpad services
              c. Back up the etherpad dir to /tmp/etherpad_backup
              d. Run puppet, which should notice the missing directory and
                 repopulate it with the configured (updated) version of the
                 package
    """

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

        1.  Forcefully stop puppet and any runs that are currently happening
        2.  Stop the etherpad service
        3.  Back up the hilary app dir to /tmp/hilary_backup
        4.  Back up the ui app dir to /tmp/ui_backup
        5.  Run puppet, which should notice the missing directories and
            repopulate them with the configured (updated) version of the
            packages
    """

    with settings(parallel=(parallel != "False")):
        execute(upgrade_host_internal)


def upgrade_host_internal():
    puppet.stop(force=True)
    etherpad.stop()
    etherpad.clean()
    puppet.run(force=False)
    puppet.start()
