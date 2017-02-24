from time import sleep
from fabric.api import cd, task
from fabric.operations import sudo
from fabric.tasks import execute


@task
def stop(force=True):
    """Stop puppet and optionally any active puppet runs.

    Keyword arguments:
    force --    Whether or not we should force-stop any currently active puppet
                runs (Default: True)
    """

    # Stop the service
    sudo('service puppet stop')

    # Stopping the service will only stop new runs from happening. If we're
    # forcing a stop, we want to quite and in-progress runs as well
    if force:

        # pgrep puppet -c returns the number of puppet processes that are
        # running. If it isn't 0, we need to pkill them
        if not sudo('pgrep puppet -c', warn_only=True).startswith("0"):
            sudo('pkill puppet', warn_only=True)
            sleep(10)

            # If 5 seconds wasn't enough to kill the active runs, continue
            # pkill'ing and waiting 1 second each iteration
            while not sudo('pgrep puppet -c', warn_only=True).startswith("0"):
                print 'Puppet is still running, trying to kill it again'
                sudo('pkill puppet', warn_only=True)
                sleep(5)

        # Ensure that lock file is removed so puppet can be run
        sudo('rm /var/lib/puppet/state/agent_catalog_run.lock', warn_only=True)


@task
def start():
    """Start the puppet agent service."""
    sudo('service puppet start')


@task
def run(force=True):
    """Immediately start a puppet run.

    Keyword arguments:
    force --    Whether or not we should force-stop any currently active puppet
                runs. Useful to ensure we get a run from the very beginning.
    """

    # If we're forcing a run, we want it to run right now from the store. Kill
    # and running puppet processes to achieve this
    if force:
        execute(stop, force=True)

    # Start an adhoc puppet run
    sudo('puppet agent --onetime --verbose --no-daemonize', warn_only=True)

    # Start puppet back up if we forcefully stopped it
    if force:
        sudo('service puppet start')


@task
def git_update():
    """Pull the updated code from git."""

    with cd('/etc/puppet/puppet-hilary'):
        sudo('git pull')
