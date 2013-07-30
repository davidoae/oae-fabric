
## OAE Fabric

Deployment.. well, upgrade.. tools for Apereo OAE.

## Getting started

### Install Fabric

1. Install python and pip: `sudo apt-get install build-essentials python-dev python-pip`
2. Install fabric: `pip install fabric --upgrade`

### Clone this repository

```
~$ git clone https://github.com/mrvisser/oae-fabric.git
~$ cd oae-fabric
```

### A bit of configuration

**Create ~/.fabricrc:**
```
hilary_dir=/opt/oae
ui_dir=/opt/3akai-ux
```

## What you can do

**All the tasks:**
```
~/oae-fabric$ fab --list
Available commands:

    purge_clean_backup         Clean out any code backups that may have been made for hilary and the ui.
    upgrade                    Upgrade the hilary servers to the version configured in puppet. This will:
    hilary.clean               Remove all the code from the deployed OAE ui directory.
    hilary.purge_clean_backup  Remove the backup directory created as a result of cleaning.
    hilary.start               Start the hilary service.
    hilary.stop                Stop the hilary service.
    hilary.version             Determine the installed version of hilary.
    puppet.run                 Immediately start a puppet run.
    puppet.start               Start the puppet agent service.
    puppet.stop                Stop puppet and optionally any active puppet runs.
    ui.clean                   Remove all the code from the deployed OAE ui directory.
    ui.purge_clean_backup      Remove the backup directory created as a result of cleaning.
    ui.version                 Determine the installed version of the ui.
```

**Upgrade a single server:**
```
~/oae-fabric$ fab upgrade -H app0
```

## Setup Notes

1. This depends on the fact that you have a puppet installation deploying release tarballs to the app / activity / pp servers. The upgrade process essentially:
    ** Delete the `/opt/3akai-ux` and `/opt/oae` directories
    ** Run puppet -- puppet will notice the directories aren't there and will deploy the new version. It will deploy whichever release is current in the puppet deployment, so ensure you first upgrade the release version in puppet.
2. All commands are invoked with `sudo` with whatever target user you authenticate as. This means that authenticating with `root` won't work. You must log in as a user with sudo privileges
3. This process will stop the app servers during the deployment process. Phase the ugprades among servers

## License

Copyright 2013 Apereo Foundation (AF) Licensed under the
Educational Community License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may
obtain a copy of the License at

    http://opensource.org/licenses/ECL-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS"
BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. See the License for the specific language governing
permissions and limitations under the License.
