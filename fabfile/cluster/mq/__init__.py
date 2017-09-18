from fabric.api import runs_once, settings, task
from fabric.tasks import execute
from .. import hosts as cluster_hosts, util as cluster_util
from ... import mq, hilary

__all__ = ["delete_data"]


@runs_once
@task
def delete_data():
    """Delete all task queues and contained messages from the MQ instance."""

    # Delete the queues
    with settings(hosts=cluster_hosts.mq()[0]):
        execute(mq.delete_data)

    # Ensure the queues are recreated by bouncing a hilary server
    with settings(hosts=[cluster_hosts.app()[0]]):
        execute(hilary.stop)
        execute(hilary.start)
        execute(hilary.wait_until_ready)
