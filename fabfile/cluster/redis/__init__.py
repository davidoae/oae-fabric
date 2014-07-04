from fabric.api import runs_once, settings, task
from fabric.tasks import execute
from .. import hosts as cluster_hosts, util as cluster_util
from ... import redis

__all__ = ["delete_data"]


@runs_once
@task
def delete_data():
    """Delete all data from the redis cache."""
    cluster_util.ensure_sudo_pass()

    # Delete the queues
    with settings(hosts=cluster_hosts.cache()[0]):
        execute(redis.delete_data)

    if len(cluster_hosts.activity_cache() > 0):
        with settings(hosts=cluster_hosts.activity_cache()[0]):
            execute(redis.delete_data)
