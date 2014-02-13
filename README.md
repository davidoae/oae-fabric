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

    upgrade                  Upgrade all hilary servers and nginx to the version configured in puppet.
    upgrade_hilary_host      Upgrade the hilary servers to the version configured in puppet. This will:
    hilary.clean             Remove all the code from the deployed OAE hilary directory and its code backup directory.
    hilary.start             Start the hilary service.
    hilary.stop              Stop the hilary service.
    hilary.version           Determine the installed version of hilary.
    hilary.wait_until_ready  Wait until the application server is ready to handle requests.
    puppet.run               Immediately start a puppet run.
    puppet.start             Start the puppet agent service.
    puppet.stop              Stop puppet and optionally any active puppet runs.
    ui.clean                 Remove all the code from the deployed OAE ui directory.
    ui.version               Determine the installed version of the ui.

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
