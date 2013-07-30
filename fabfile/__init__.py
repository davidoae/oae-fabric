from fabric.api import task
from fabric.tasks import execute
import hilary
import puppet
import ui


@task
def upgrade(force_hilary_clean=False, force_ui_clean=False):
    """Upgrade the hilary servers to the version configured in puppet. This will:

        1.  Forcefully stop puppet and any runs that are currently happening
        2.  Stop the hilary service
        3.  Back up the hilary app dir to /tmp/hilary_backup
        4.  Back up the ui app dir to /tmp/ui_backup
        5.  Run puppet, which should notice the missing directories and repopulate them with the
            configured (updated) version of the packages

    Keyword parameters:
    force_hilary_clean  --  Whether or not to force the removal of the configured hilary directory
                            even if it doesn't exist, doesn't look right or a backup is failed to
                            be made
    force_ui_clean      --  Same as force_hilary_clean, except for the configured ui directory
    """
    execute(puppet.stop, force=True)
    execute(hilary.stop)
    execute(hilary.clean, force=force_hilary_clean)
    execute(ui.clean, force=force_ui_clean)
    execute(puppet.run, force=True)


@task
def purge_clean_backup():
    """Clean out any code backups that may have been made for hilary and the ui."""
    execute(hilary.purge_clean_backup)
    execute(ui.purge_clean_backup)
