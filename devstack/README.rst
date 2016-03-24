This directory contains the Freezer-API DevStack plugin.

To configure the Freezer API with DevStack, you will need to
enable this plugin by adding one line to the [[local|localrc]]
section of your local.conf file.

To enable the plugin, add a line of the form::

    enable_plugin freezer-api <GITURL> [GITREF]

where::

    <GITURL> is the URL of a freezer-api repository
    [GITREF] is an optional git ref (branch/ref/tag).  The default is master.

For example::

    enable_plugin freezer-api https://git.openstack.org/openstack/freezer-api master


The plugin makes use of apache2 by default.
To use the uwsgi server set the following environment variable:

export FREEZER_API_SERVER_TYPE=uwsgi

The default port is 9090. To configure the api to listen on a different port
set the variable FREEZER_API_PORT.
For example to make use of port 19090 use:

export FREEZER_API_PORT=19090

For more information, see:
 http://docs.openstack.org/developer/devstack/plugins.html
