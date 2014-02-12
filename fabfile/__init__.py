from fabric.api import runs_once, task
from fabric.tasks import execute
import hilary
import puppet
import ui


@task
@runs_once
def upgrade():
    """Upgrade the hilary servers to the version configured in puppet. This will:

        1.  Forcefully stop puppet and any runs that are currently happening
        2.  Stop the hilary service
        3.  Back up the hilary app dir to /tmp/hilary_backup
        4.  Back up the ui app dir to /tmp/ui_backup
        5.  Run puppet, which should notice the missing directories and repopulate them with the
            configured (updated) version of the packages
    """
    execute(puppet.stop, force=True)
    execute(hilary.stop)
    execute(hilary.clean)
    execute(ui.clean)
    execute(puppet.run, force=False)
    execute(puppet.start)
