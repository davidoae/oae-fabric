from fabric.api import cd, env, runs_once, sudo, task
from fabric.tasks import execute
from getpass import getpass
import hilary
import oae_env
import puppet
import ui


if len(env.hosts) == 0:
    env.hosts = ["localhost"]


@runs_once
@task
def upgrade():
    """Upgrade all hilary servers and nginx to the version configured in puppet.

       This will:

        1.  Ask for a password with which to sudo. All servers must have the same sudo passowrd.
        2.  Stop puppet on the web node. This must be done before the latest puppet configuration
            is pulled from git because the moment that happens, puppet could run on the web node
            and update its UI files before the app servers are prepared
        3.  Perform a git pull on the puppet node to get the latest configuration
        4.  Run the hilary upgrade task on the first PP node in the list. If the PP node does not come
            back up successfully, that task will be stuck in a loop waiting for the Hilary server
            to become healthy.
        5.  Run the hilary upgrade task in parallel on:
                * The remainder of the PP nodes
                * All the activity nodes
                * HALF of the app server nodes
        6.  Run puppet on the web node.
                * Note that between step #6 and #7, half of the app servers are running on a different
                  set of UI files than the web server. Once those app servers are shut down, the state
                  of the UI code versioning is consistent again
        7.  Run the hilary upgrade task in parallel on the remainder of the Hilary nodes, which entails
            shutting down the Hilary server early in the process
        8.  Start puppet on the web node
    """
    ensure_sudo_pass()

    pp = oae_env.pp_hosts()
    activity = oae_env.activity_hosts()
    app = oae_env.app_hosts()

    # Stop puppet on the web node
    env.hosts = [oae_env.web_host()]
    execute(puppet.stop, force=True)

    # Pull the updated puppet data
    env.hosts = [oae_env.puppet_host()]
    with cd('/etc/puppet/puppet-hilary'):
        sudo('git pull')

    # Run all batches of host upgrades in parallel
    env.parallel = True

    env.hosts = pp[0:1]
    execute(upgrade_hilary_host_internal)

    # Do the rest of the PP nodes, and only half of the app nodes
    env.hosts = pp[1:] + activity + app[:len(app) / 2]
    execute(upgrade_hilary_host_internal)

    # Upgrade the web node
    env.hosts = [oae_env.web_host()]
    execute(puppet.run)

    # If there was more than one app node, upgrade the other half of the app nodes
    if len(app) > 1:
        env.hosts = app[len(app) / 2:]
        execute(upgrade_hilary_host_internal)

    # Enable puppet on the web node
    env.hosts = [oae_env.web_host()]
    execute(puppet.start)


@runs_once
@task
def upgrade_hilary_host(parallel=True):
    """Upgrade the hilary servers to the version configured in puppet.

       This will:

        1.  Forcefully stop puppet and any runs that are currently happening
        2.  Stop the hilary service
        3.  Back up the hilary app dir to /tmp/hilary_backup
        4.  Back up the ui app dir to /tmp/ui_backup
        5.  Run puppet, which should notice the missing directories and repopulate them with the
            configured (updated) version of the packages
    """
    ensure_sudo_pass()

    if parallel != "False":
        env.parallel = True
    else:
        env.parallel = False

    execute(upgrade_hilary_host_internal)


def upgrade_hilary_host_internal():
    puppet.stop(force=True)
    hilary.stop()
    hilary.clean()
    ui.clean()
    puppet.run(force=False)
    puppet.start()
    hilary.wait_until_ready()


def ensure_sudo_pass():
    if env.password == None:
        env.password = getpass('Enter sudo password: ')
