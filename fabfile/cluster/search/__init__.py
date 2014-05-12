from fabric.api import runs_once, settings, task
from fabric.tasks import execute
from .. import hosts as cluster_hosts, util as cluster_util
from ... import puppet, search

__all__ = ["upgrade", "upgrade_host"]


@runs_once
@task
def upgrade():
    """Runs through a general upgrade procedure for all known search nodes.

        This will:

            1.  Ask for a password with which to sudo. All servers must have
                the same sudo passowrd
            2.  Perform a git pull on the puppet node to get the latest
                configuration
            3.  Run puppet on each search node
            4.  Do a full restart of all the search servers
    """
    cluster_util.ensure_sudo_pass()

    # Stop puppet on the search nodes
    with settings(hosts=cluster_hosts.search(), parallel=True):
        execute(puppet.stop, force=True)

    # Pull the updated puppet configuration
    with settings(hosts=[cluster_hosts.puppet()], parallel=True):
        execute(puppet.git_update)

    # Remove the ES index
    with settings(hosts=cluster_hosts.search(), parallel=True):
        execute(search.clear_data, force=False)

    # Run puppet on the search nodes
    with settings(hosts=cluster_hosts.search(), parallel=True):
        execute(puppet.run, force=False)

    # Do a full search cluster reboot. We bring the full cluster
    # down as a rule since ES has gossip and sometimes requires it
    with settings(hosts=cluster_hosts.search(), parallel=True):
        execute(search.stop)
        execute(search.start)

    # Start puppet on the search nodes
    with settings(hosts=cluster_hosts.search(), parallel=True):
        execute(puppet.start)


@runs_once
@task
def upgrade_host():
    """Run through the general upgrade procedure for a search node, assuming
    puppet has already been updated.

        This will:

            1.  Ask for a password with which to sudo
            2.  Forcefully stop any current puppet runs
            3.  Run puppet
            5.  Restart elasticsearch
            6.  Start puppet
    """
    cluster_util.ensure_sudo_pass()

    execute(puppet.stop, force=True)
    execute(puppet.run, force=False)
    execute(search.restart)
    execute(puppet.start)
