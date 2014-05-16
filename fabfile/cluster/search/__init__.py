from fabric.api import env, runs_once, settings, task
from fabric.tasks import execute
from .. import hosts as cluster_hosts, util as cluster_util
from ... import puppet, search, hilary

__all__ = ["upgrade", "upgrade_host"]


@runs_once
@task
def upgrade(refresh_data=False, uninstall=True):
    """Runs through a general upgrade procedure for all known search nodes.

        This will:

            1.  Ask for a password with which to sudo. All servers must have
                the same sudo passowrd
            2.  Stop puppet on the search nodes
            3.  Perform a git pull on the puppet node to get the latest
                configuration
            4.  If `refresh_data` was `True`, delete the search index
            5.  Unless `uninstall` was `False`, uninstall ElasticSearch
            6.  Do a full search cluster shut down
            7.  Run puppet on each search node
            8.  Bring the cluster back up
            9.  If refresh_data was `True`, restart an app node to recreate the
                search index
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

    # Uninstall ElasticSearch if the option has not been disabled
    if uninstall:
        with settings(hosts=cluster_hosts.search(), parallel=True):
            execute(search.uninstall)

    # Bring the full cluster down. We bring the full cluster down as a rule
    # since ElasticSearch has gossip, sometimes upgrades can require that all
    # nodes come back gossiping on the same version
    with settings(hosts=cluster_hosts.search(), parallel=True):
        execute(search.stop)

    # Run puppet on the search nodes and ensure they come back up
    with settings(hosts=cluster_hosts.search(), parallel=True):
        execute(puppet.run, force=False)
        execute(search.start)

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
def upgrade_host(refresh_data=False, uninstall=True, hilary_reboot_host="pp0"):
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

    # Stop puppet on the search node
    execute(puppet.stop, force=True)

    # If we're deleting the data, clear the index
    if refresh_data:
        execute(search.delete_index, index_name=search_index_name())

    # Uninstall ElasticSearch if the option has not been disabled
    if uninstall:
        with settings(hosts=cluster_hosts.search(), parallel=True):
            execute(search.uninstall)

    # Bring the search node down
    execute(search.stop)

    # Run puppet on the search node
    execute(puppet.run, force=False)

    # Ensure the node is running again
    execute(search.start)

    # If we refreshed the data, reboot a hilary node so it can
    # create the schema again
    if refresh_data:
        with settings(hosts=[hilary_reboot_host]):
            execute(hilary.stop)
            execute(hilary.start)
            execute(hilary.wait_until_ready)

    # Start puppet on the search node again
    execute(puppet.start)


def search_index_name():
    return getattr(env, 'search_index_name', 'oae')
