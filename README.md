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

**Optionally create ~/.fabricrc:**
```
hilary_dir=/opt/oae
ui_dir=/opt/3akai-ux
hilary_check_host=localhost
hilary_check_host_header=admin.oaeproject.org
hilary_check_port=2000
```

All values specified in the example are default values if the configuration property is not specified.

## What you can do

**All the tasks:**
```
~/oae-fabric$ fab --list
Available commands:

    cluster.db.upgrade             Runs through a general upgrade procedure for a set of Cassandra nodes.
    cluster.db.upgrade_host        Run through the general upgrade procedure for a Cassandra node, assuming
    cluster.etherpad.reboot        Reboot all the etherpad servers.
    cluster.etherpad.upgrade       Upgrade all Etherpad servers to the version configured in puppet.
    cluster.etherpad.upgrade_host  Upgrade the etherpad servers to the version configured in puppet.
    cluster.oae.reboot             Perform a rolling reboot of all the Hilary nodes across the cluster.
    cluster.oae.upgrade            Upgrade all hilary servers and nginx to the version configured in
    cluster.oae.upgrade_host       Upgrade the hilary servers to the version configured in puppet.
    cluster.search.upgrade         Runs through a general upgrade procedure for all known search nodes.
    cluster.search.upgrade_host    Run through the general upgrade procedure for a search node, assuming
    db.drain                       Drain the commitlog of the database.
    db.start                       Start the database service.
    db.stop                        Stop the database service.
    db.upgradesstables             Run the nodetool upgradesstables process.
    db.wait_until_ready            Wait until the database is ready to handle requests.
    etherpad.clean                 Remove all the code from the deployed etherpad directory and its code backup directory.
    etherpad.start                 Start the etherpad service.
    etherpad.stop                  Stop the etherpad service.
    etherpad.version               Determine the installed version of etherpad.
    hilary.clean                   Remove all the code from the deployed OAE hilary directory and its code backup directory.
    hilary.start                   Start the hilary service.
    hilary.stop                    Stop the hilary service.
    hilary.version                 Determine the installed version of hilary.
    hilary.wait_until_ready        Wait until the application server is ready to handle requests.
    puppet.git_update              Pull the updated code from git.
    puppet.run                     Immediately start a puppet run.
    puppet.start                   Start the puppet agent service.
    puppet.stop                    Stop puppet and optionally any active puppet runs.
    search.restart                 Restart the search service.
    search.start                   Start the search service.
    search.stop                    Stop the search service.
    search.wait_until_ready        Wait until search is ready to handle requests.
    search.wait_until_stopped      Wait until search has been fully stopped.
    ui.clean                       Remove all the code from the deployed OAE ui directory.
    ui.version                     Determine the installed version of the ui.

```

**Upgrade all servers in a safe way as per your oae_env.py file:**
```
~/oae-fabric$ fab upgrade
```

**Upgrade a specific list of hilary servers in parallel:**
```
~/oae-fabric$ fab upgrade_hilary_host -H app0,app1 -P
```

## Setup Notes

1. This depends on the assumption that you have a puppet installation deploying release tarballs to the app / activity / pp servers. The upgrade process essentially:
    ** Delete the `/opt/3akai-ux` and `/opt/oae` directories
    ** Run puppet -- puppet will notice the directories aren't there and will deploy the new version. It will deploy whichever release is current in the puppet deployment, so ensure you first upgrade the release version in puppet.
2. All commands are invoked with `sudo` with whatever target user you authenticate as. This means that authenticating with `root` won't work. You must log in as a user with sudo privileges
3. This process will stop the app servers during the deployment process. Phase the ugprades among servers

## License

Copyright 2014 Apereo Foundation (AF) Licensed under the
Educational Community License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may
obtain a copy of the License at

    http://opensource.org/licenses/ECL-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS"
BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. See the License for the specific language governing
permissions and limitations under the License.
