from fabric.api import env, runs_once, settings, task
from fabric.tasks import execute
from .. import hosts as cluster_hosts, util as cluster_util
from ... import hilary, puppet, ui

__all__ = ["upgrade", "upgrade_host"]


@runs_once
@task
def reboot():
    """Perform a rolling reboot of all the Hilary nodes across the cluster."""
    cluster_util.ensure_sudo_pass()

    pp = cluster_hosts.pp()
    activity = cluster_hosts.activity()
    app = cluster_hosts.app()

    # Reboot one node first to make sure it comes up successfully
    with settings(hosts=pp[0:1]):
        execute(reboot_host_internal)

    # Reboot all but half the application nodes and make sure they come up
    # successfully
    with settings(hosts=pp[1:] + activity + app[:len(app) / 2], parallel=True):
        execute(reboot_host_internal)

    # If there was more than one app node, reboot the other half of the app
    # nodes
    if len(app) > 1:
        with settings(hosts=app[len(app) / 2:], parallel=True):
            execute(reboot_host_internal)


@runs_once
@task
def upgrade():
    """Upgrade all hilary servers and nginx to the version configured in
    puppet.

       This will:

        1.  Ask for a password with which to sudo. All servers must have the
            same sudo passowrd.
        2.  Stop puppet on the web node. This must be done before the latest
            puppet configuration is pulled from git because the moment that
            happens, puppet could run on the web node and update its UI files
            before the app servers are prepared
        3.  Perform a git pull on the puppet node to get the latest
            configuration
        4.  Run the hilary upgrade task on the first PP node in the list. If
            the PP node does not come back up successfully, that task will be
            stuck in a loop waiting for the Hilary server to become healthy.
        5.  Run the hilary upgrade task in parallel on:
                * The remainder of the PP nodes
                * All the activity nodes
                * HALF of the app server nodes
        6.  Run puppet on the web node.
                * Note that between step #6 and #7, half of the app servers are
                  running on a different set of UI files than the web server.
                  Once those app servers are shut down, the state of the UI
                  code versioning is consistent again
        7.  Run the hilary upgrade task in parallel on the remainder of the
            Hilary nodes, which entails shutting down the Hilary server early
            in the process
        8.  Start puppet on the web node
    """
    cluster_util.ensure_sudo_pass()

    pp = cluster_hosts.pp()
    activity = cluster_hosts.activity()
    app = cluster_hosts.app()

    # Stop puppet on the web node
    with settings(hosts=[cluster_hosts.web()]):
        execute(puppet.stop, force=True)

    # Pull the updated puppet data
    with settings(hosts=[cluster_hosts.puppet()]):
        execute(puppet.git_update)

    # Upgrade one PP node and see if it comes back up
    with settings(hosts=pp[0:1], parallel=True):
        execute(upgrade_host_internal)

    # Do the rest of the PP nodes, and only half of the app nodes
    with settings(hosts=pp[1:] + activity + app[:len(app) / 2], parallel=True):
        execute(upgrade_host_internal)

    # Upgrade the web node
    with settings(hosts=[cluster_hosts.web()]):
        execute(puppet.run)

    # If there was more than one app node, upgrade the other half of the app
    # nodes
    if len(app) > 1:
        with settings(hosts=app[len(app) / 2:], parallel=True):
            execute(upgrade_host_internal)


@runs_once
@task
def upgrade_host(parallel=True):
    """Upgrade the hilary servers to the version configured in puppet.

       This will:

        1.  Ask for a password with which to sudo. All servers must have the
            same sudo passowrd.
        2.  Forcefully stop puppet and any runs that are currently happening
        3.  Stop the hilary service
        4.  Back up the hilary app dir to /tmp/hilary_backup
        5.  Back up the ui app dir to /tmp/ui_backup
        6.  Run puppet, which should notice the missing directories and
            repopulate them with the configured (updated) version of the
            packages
    """
    cluster_util.ensure_sudo_pass()

    if parallel != "False":
        env.parallel = True
    else:
        env.parallel = False

    execute(upgrade_host_internal)


def upgrade_host_internal():
    puppet.stop(force=True)
    hilary.stop()
    hilary.clean()
    ui.clean()
    puppet.run(force=False)
    puppet.start()
    hilary.wait_until_ready()


def reboot_host_internal():
    hilary.stop()
    hilary.start()
    hilary.wait_until_ready()
