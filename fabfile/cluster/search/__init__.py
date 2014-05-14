from fabric.api import env, runs_once, settings, task
from fabric.tasks import execute
from .. import hosts as cluster_hosts, util as cluster_util
from ... import puppet, search, hilary

__all__ = ["upgrade", "upgrade_host"]


@runs_once
@task
def upgrade(refresh_data=False):
    """Runs through a general upgrade procedure for all known search nodes.

        This will:

            1.  Ask for a password with which to sudo. All servers must have
                the same sudo passowrd
            2.  Stop puppet on the search nodes
            3.  Perform a git pull on the puppet node to get the latest
                configuration
            4.  Delete the search index, if specified to refresh_data
            5.  Do a full search cluster shut down
            5.  Run puppet on each search node
            6.  Bring the cluster back up
            7.  Restart an app node so the search mapping can be restored (can be skipped by setting restart_app_node to `False`)
    """
    cluster_util.ensure_sudo_pass()

    # Stop puppet on the search nodes
    with settings(hosts=cluster_hosts.search(), parallel=True):
        execute(puppet.stop, force=True)

    # Pull the updated puppet configuration
    with settings(hosts=[cluster_hosts.puppet()], parallel=True):
        execute(puppet.git_update)

    # If we're deleting the data, clear index
    if refresh_data:
        with settings(hosts=[cluster_hosts.search()[0]]):
            execute(search.delete_index, index_name=search_index_name())

    # Do a full search cluster reboot. We bring the full cluster down as a rule
    # since ElasticSearch has gossip, sometimes upgrades can require that we
    # reboot it
    with settings(hosts=cluster_hosts.search(), parallel=True):
        execute(search.stop)

    # Run puppet on the search nodes
    with settings(hosts=cluster_hosts.search(), parallel=True):
        execute(puppet.run, force=False)

    # If we deleted the search index, bounce an app server so it will recreate
    # the index and its mappings
    if refresh_data:
        with settings(hosts=[cluster_hosts.app()[0]]):
            execute(hilary.stop)
            execute(hilary.start)
            execute(hilary.wait_until_ready)

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


def search_index_name():
    return getattr(env, 'search_index_name', 'oae')
