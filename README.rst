===========
Freezer API
===========

TOC
===

#. Installation
#. Devstack Plugin
#. Concepts and definitions
#. API registration
#. API routes
#. Backup metadata structure
#. Freezer Client document structure
#. Jobs
#. Actions
#. Sessions
#. Known Issues

Installation
============

Install freezer-api
-------------------

.. code-block::

  # git clone https://git.openstack.org/openstack/freezer-api.git
  # cd freezer-api
  # pip install ./

edit config file
----------------

.. code-block::

  # sudo cp etc/freezer/freezer-api.conf /etc/freezer/freezer-api.conf
  # sudo cp etc/freezer/freezer-paste.ini /etc/freezer/freezer-paste.ini
  # sudo vi /etc/freezer/freezer-api.conf
  # sudo vi /etc/freezer/freezer-paste.ini

setup/configure the db
----------------------

The currently supported db is Elasticsearch. In case you are using a dedicated instance
of the server, you'll need to start it. Depending on the OS flavor it might be a:

.. code-block::

  # service elasticsearch start

or, on systemd

.. code-block::

  # systemctl start elasticsearch

Elasticsearch needs to know what type of data each document's field contains.
This information is contained in the `mapping`, or schema definition.
Elasticsearch will use dynamic mapping to try to guess the field type from
the basic datatypes available in JSON, but some field's properties have to be
explicitly declared to tune the indexing engine.
To do that, use the freezer-manage command:
::

  # freezer-manage db sync

You should have updated your configuration files before doing this step.
freezer-manage has the following options:

* To create the db mappings use the following command::

  # freezer-manage db sync

* To update the db mappings using the following command. Update means that you
  might have some mappings and you want to update it with a more recent ones 
  ::

  # freezer-manage db update

* To remove the db mappings using the following command ::

  # freezer-manage db remove

* To print the db mappings using the following command ::

  # freezer-manage db show

* To update your settings (number of replicas) all what you need to do is to
  change its value in the configuration file and then run the following command ::

  # freezer-manage db update-settings

If you provided an invalid number of replicas that will cause problems later on,
so it's highly recommended to make sure that you are using the correct number
of replicas. For more info click here `Elasticsearch_Replicas_instructions <https://www.elastic.co/guide/en/elasticsearch/guide/current/replica-shards.html>`_

* To get information about optional additional parameters::

  # freezer-manage -h

* If you want to add any additional parameter like --yes or --erase, they should
  be before the db option. Check the following examples:

Wrong Example::

   # freezer-manage db sync -y -e

Correct Example::

   # freezer-manage -y -e db sync

run simple instance
-------------------

.. code-block::

  # freezer-api

examples running using uwsgi
----------------------------

.. code-block::

  # uwsgi --http :9090 --need-app --master --module freezer_api.cmd.wsgi:application

  # uwsgi --https :9090,foobar.crt,foobar.key --need-app --master --module freezer_api.cmd.wsgi:application


example running freezer-api with apache2
----------------------------------------

.. code-block::

    # sudo vi /etc/apache2/sites-enabled/freezer-api.conf

    <VirtualHost ...>
        WSGIDaemonProcess freezer-api processes=2 threads=2 user=freezer
        WSGIProcessGroup freezer-api
        WSGIApplicationGroup freezer-api
        WSGIScriptAlias / /opt/stack/freezer_api/cmd/wsgi.py

        ErrorLog /var/log/freezer-api/freezer-api.log
        CustomLog /var/log/freezer-api/freezer-api_access.log combined
        LogLevel info

        <Directory /opt/stack/freezer_api>
          Options Indexes FollowSymLinks MultiViews
          Require all granted
          AllowOverride None
          Order allow,deny
          allow from all
          LimitRequestBody 102400
        </Directory>
    </VirtualHost>

Devstack Plugin
===============

Edit local.conf
---------------

To configure the Freezer API with DevStack, you will need to enable the
freezer-api plugin by adding one line to the [[local|localrc]] section
of your local.conf file:

.. code-block:: 

    enable_plugin freezer-api <GITURL> [GITREF]

where

.. code-block:: 

    <GITURL> is the URL of a freezer-api repository
    [GITREF] is an optional git ref (branch/ref/tag).  The default is master.

For example

.. code-block::

    enable_plugin freezer-api https://git.openstack.org/openstack/freezer-api.git master

Plugin Options
---------------

The plugin makes use of apache2 by default.
To use the *uwsgi* server set the following environment variable

.. code-block:: 

    export FREEZER_API_SERVER_TYPE=uwsgi

The default port is *9090*. To configure the api to listen on a different port
set the variable `FREEZER_API_PORT`.
For example to make use of port 19090 use

.. code-block::

    export FREEZER_API_PORT=19090

For more information, see `openstack_devstack_plugins_install <http://docs.openstack.org/developer/devstack/plugins.html>`_

Concepts and definitions
===========================

*hostname* is _probably_ going to be the host fqdn.

*backup_id*
defined as `container_hostname_backupname_timestamp_level` uniquely
identifies a backup

*backup_set*
defined as `container_hostname_backupname` identifies a group of related
backups which share the same container,hostname and backupname


API registration
===================

.. code-block::

    # openstack user create --domain default --password-prompt freezer
    # openstack role add --project service --user freezer admin

    # openstack service create --name freezer --description "Freezer Backup Service" backup

    # openstack endpoint create --region RegionOne backup public http://freezer_api_publicurl:port
    # openstack endpoint create --region RegionOne backup internal http://freezer_api_internalurl:port
    # openstack endpoint create --region RegionOne backup admin http://freezer_api_adminurl:port


API routes
==========

General
-------

.. code-block:: 

    GET /       List API version
    GET /v1     JSON Home document, see http://tools.ietf.org/html/draft-nottingham-json-home-03

Backup metadata
---------------

.. code-block::

    GET    /v1/backups(?limit,offset)  Lists backups
    POST   /v1/backups                 Creates backup entry

    GET    /v1/backups/{backup_id}     Get backup details
    DELETE /v1/backups/{backup_id}     Deletes the specified backup

Freezer clients management
--------------------------

.. code-block::

    GET    /v1/clients(?limit,offset)       Lists registered clients
    POST   /v1/clients                      Creates client entry

    GET    /v1/clients/{freezerc_id}     Get client details
    UPDATE /v1/clients/{freezerc_id}     Updates the specified client information
    DELETE /v1/clients/{freezerc_id}     Deletes the specified client information

Freezer jobs management
-----------------------

.. code-block::

    GET    /v1/jobs(?limit,offset)     Lists registered jobs
    POST   /v1/jobs                    Creates job entry

    GET    /v1/jobs/{jobs_id}          Get job details
    POST   /v1/jobs/{jobs_id}          creates or replaces a job entry using the specified job_id
    DELETE /v1/jobs/{jobs_id}          Deletes the specified job information
    PATCH  /v1/jobs/{jobs_id}          Updates part of the document

Freezer actions management
--------------------------

.. code-block::

    GET    /v1/actions(?limit,offset)  Lists registered action
    POST   /v1/actions                 Creates action entry

    GET    /v1/actions/{actions_id}    Get action details
    POST   /v1/actions/{actions_id}    creates or replaces a action entry using the specified action_id
    DELETE /v1/actions/{actions_id}    Deletes the specified action information
    PATCH  /v1/actions/{actions_id}    Updates part of the action document

Freezer sessions management
---------------------------

.. code-block::

    GET    /v1/sessions(?limit,offset)  Lists registered session
    POST   /v1/sessions                 Creates session entry

    GET    /v1/sessions/{sessions_id}    Get session details
    POST   /v1/sessions/{sessions_id}    creates or replaces a session entry using the specified session_id
    DELETE /v1/sessions/{sessions_id}    Deletes the specified session information
    PATCH  /v1/sessions/{sessions_id}    Updates part of the session document

    POST   /v1/sessions/{sessions_id}/action           requests actions (e.g. start/end) upon a specific session

    PUT    /v1/sessions/{sessions_id}/jobs/{job_id}    adds the job to the session
    DELETE /v1/sessions/{sessions_id}/jobs/{job_id}    adds the job to the session

Backup metadata structure
============================

.. note:: 
   sizes are in MB

.. code-block::

    backup_metadata:=
    {
      "container": string,
      "host_name": string,      # fqdn, client has to provide consistent information here !
      "backup_name": string,
      "time_stamp": int,
      "level": int,
      "max_level": int,
      "mode" : string,            (fs mongo mysql)
      "fs_real_path": string,
      "vol_snap_path": string,
      "total_broken_links" : int,
      "total_fs_files" : int,
      "total_directories" : int,
      "backup_size_uncompressed" : int,
      "backup_size_compressed" : int,
      "compression_alg": string,            (gzip bzip xz)
      "encrypted": bool,
      "client_os": string
      "broken_links" : [string, string, string],
      "excluded_files" : [string, string, string]
      "cli": string,         equivalent cli used when executing the backup ?
      "version": string
    }


The api wraps backup_metadata dictionary with some additional information.
It stores and returns the information provided in this form

.. code-block:: 

    {
      "backup_id": string         #  container_hostname_backupname_timestamp_level
      "user_id": string,          # owner of the backup metadata (OS X-User-Id, keystone provided)
      "user_name": string         # owner of the backup metadata (OS X-User-Name, keystone provided)

      "backup_metadata": {        #--- actual backup_metadata provided
        "container": string,
        "host_name": string,
        "backup_name": string,
        "timestamp": int,
        ...
      }
    }


Freezer Client document structure
====================================

Identifies a freezer client for the purpose of sending action

client_info document contains information relevant for client identification

.. code-block::

    client_info:=
    {
      "client_id": string   actually a concatenation "tenant-id_hostname"
      "hostname": string
      "description": string
      "uuid":
    }


client_type document embeds the client_info and adds user_id

.. code-block::

    client_type :=
    {
      "client" : client_info document,
      "user_id": string,    # owner of the information (OS X-User-Id, keystone provided, added by api)
    }


Jobs
=======

A job describes a single action to be executed by a freezer client, for example a backup, or a restore.
It contains the necessary information as if they were provided on the command line.

A job is stored in the api together with some metadata information such as:
job_id, user_id, client_id, status, scheduling information etc

Scheduling information enables future/recurrent execution of jobs

.. code-block:: 

    +---------------------+
    | Job                 |
    +---------------------+   job_actions   +--------------+
    |                     +---------------->|  job_action  |
    |  +job_id            | 0..*            +--------------+  freezer_action
    |  +client_id         |                 | +mandatory   |-------------+
    |  +user_id           |                 | +retries     |             |  +----------------+
    |  +description       |  job_schedule   +--------------+             +->| freezer_action |
    |                     +---------------+                                 +----------------+
    |                     |               |   +-------------------+
    +---------------------+               +-->| job schedule dict |
                                              +-------------------+


job document structure

.. code-block::

    "job": {
      "job_action":   { parameters for freezer to execute a specific action }
      "job_schedule": { scheduling information }
      "job_id":       string
      "client_id":    string
      "user_id":      string
      "description":  string
    }

    "job_actions":
        [
            {
                "freezer_action" :
                    {
                        "action" :      string
                        "mode" :        string
                        "src_file" :    string
                        "backup_name" : string
                        "container" :   string
                        ...
                    },
                "mandatory": False,
                "max_retries": 3,
                "max_retry_interval": 60
            },
            {
                "freezer_action" :
                    {
                        ...
                    },
                "mandatory": False,
                "max_retries": 3,
                "max_retry_interval": 60

            }
        ]

    "job_schedule": {
      "time_created":    int  (timestamp)
      "time_started":    int  (timestamp)
      "time_ended":      int  (timestamp)
      "status":          string  ["stop", "scheduled", "running", "aborting", "removed"]
      "event":           string  ["", "stop", "start", "abort", "remove"]
      "result":          string  ["", "success", "fail", "aborted"]

      SCHEDULING TIME INFORMATION
    }


Scheduling Time Information
-------------------------------

Three types of scheduling can be identified

  * date - used for single run jobs
  * interval - periodic jobs, providing an interval value
  * cron-like jobs

Each type has specific parameters which can be given.

date scheduling
----------------

.. code-block::

  "schedule_date":      : datetime isoformat

interval scheduling
-------------------------

.. code-block::

  "schedule_interval"   : "continuous", "N weeks" / "N days" / "N hours" / "N minutes" / "N seconds"

  "schedule_start_date" : datetime isoformat
  "schedule_end_date"   : datetime isoformat

cron-like scheduling
--------------------

.. code-block::

  "schedule_year"       : 4 digit year
  "schedule_month"      : 1-12
  "schedule_day"        : 1-31
  "schedule_week"       : 1-53
  "schedule_day_of_week": 0-6 or string mon,tue,wed,thu,fri,sat,sun
  "schedule_hour"       : 0-23
  "schedule_minute"     : 0-59
  "schedule_second"     : 0-59

  "schedule_start_date" : datetime isoformat
  "schedule_end_date"   : datetime isoformat

Job examples
------------

example backup freezer_action

.. code-block::

    "freezer_action": {
      "action" : "backup"
      "mode" : "fs"
      "src_file" : "/home/tylerdurden/project_mayhem"
      "backup_name" : "project_mayhem_backup"
      "container" : "my_backup_container"
      "max_backup_level" : int
      "always_backup_level": int
      "restart_always_backup": int
      "no_incremental" : bool
      "encrypt_pass_file" : private_key_file
      "log_file" : "/var/log/freezer.log"
      "hostname" : false
      "max_cpu_priority" : false
    }

example restore freezer_action

.. code-block::

    "freezer_action": {
      "action": "restore"
      "restore-abs-path": "/home/tylerdurden/project_mayhem"
      "container" : "my_backup_container"
      "backup-name": "project_mayhem_backup"
      "restore-from-host": "another_host"
      "max_cpu_priority": true
    }


example scheduled backup job.
job will be executed once at the provided datetime

.. code-block::

    "job": {
        "job_actions":
            [
                {
                    "freezer_action":
                        {
                            "action" : "backup",
                            "mode" : "fs",
                            "src_file" : "/home/tylerdurden/project_mayhem",
                            "backup_name" : "project_mayhem_backup",
                            "container" : "my_backup_container",
                        }
                    "exit_status": "fail|success"
                    "max_retries": int,
                    "max_retries_interval": secs,
                    "mandatory": bool
                },
                {
                    action
                    ...
                },
                {
                    action
                    ...
                }
            ],
        "job_schedule":
            {
                "time_created": 1234,
                "time_started": 1234,
                "time_ended":   0,
                "status":  "stop | scheduled | running",
                "schedule_date": "2015-06-02T16:20:00",
            }
        "job_id": "blabla",
        "client_id": "blabla",
        "user_id": "blabla",
        "description": "scheduled one shot",
    }


    "job": {
        "job_actions":
            [ ... ],
        "job_schedule":
            {
                "time_created": 1234,
                "time_started": 1234,
                "time_ended":   0,

                "status":  "stop",
                "event": "start"
                "schedule_interval" : "1 days"
                "schedule_start_date" : "2015-06-02T16:20:00"
            },
        "job_id": "4822e482fcbb439189a1ad616ac0a72f",
        "client_id": "26b4ea367ac64702868653912e9428cc_freezer.mydomain.myid",
        "user_id": "35a322dfb2b14f40bc53a29a14309021",
        "description": "daily backup",
    }


multiple scheduling choices allowed

.. code-block::

    "job": {
        "job_actions":
            [ ... ],
        "job_schedule":
            {
                "time_created": 1234,
                "time_started": 1234,
                "time_ended":   0,
                "status":  "scheduled"
                "schedule_month" : "1-6, 9-12"
                "schedule_day" : "mon, wed, fri"
                "schedule_hour": "03"
                "schedule_minute": "25"
            }
        "job_id": "blabla",
        "client_id": "blabla",
        "user_id": "blabla",
        "description": "daily backup",
    }


Finished job with result

.. code-block::

    "job": {
        "job_actions": [ ... ],
        "job_schedule":
            {
                "time_created": 1234,
                "time_started": 1234,
                "time_ended":   4321,
                "status":  "stop",
                "event": "",
                "result": "success",
                "schedule_time": "2015-06-02T16:20:00"
            },
        "job_id": "blabla",
        "client_id": "blabla",
        "user_id": "blabla",
        "description": "one shot job",
    }


Actions default values
----------------------

It is possible to define properties that span across multiple actions
This allow not to rewrite values that might be the same in multiple actions.
If properties are specifically set in one action, then the specified value is the one used.

Example

.. code-block::

    "job": {
        "action_defaults": {
            "log_file": "/tmp/freezer_tmp_log",
            "container": "my_backup_container"
        },
        "job_actions": [{
            "freezer_action": {
                "action": "backup",
                "mode": "fs",
                "src_file": "/home/user1/file",
                "backup_name": "user1_backup"
            }
        }, {
            "freezer_action": {
                "action": "backup",
                "mode": "fs",
                "src_file": "/home/user2/file",
                "backup_name": "user2_backup"
            }
        }, {
            "freezer_action": {
                "action": "backup",
                "mode": "fs",
                "src_file": "/home/user3/file",
                "backup_name": "user2_backup",
                "log_file": "/home/user3/specific_log_file"
            }
        }],
        "description": "scheduled one shot"
    }


Is Equivalent to

.. code-block::

    "job": {
        "job_actions": [{
            "freezer_action": {
                "action": "backup",
                "mode": "fs",
                "src_file": "/home/user1/file",
                "backup_name": "user1_backup",
                "log_file": "/tmp/freezer_tmp_log",
                "container": "my_backup_container"
            }
        }, {
            "freezer_action": {
                "action": "backup",
                "mode": "fs",
                "src_file": "/home/user2/file",
                "backup_name": "user2_backup",
                "log_file": "/tmp/freezer_tmp_log",
                "container": "my_backup_container"
            }
        }, {
            "freezer_action": {
                "action": "backup",
                "mode": "fs",
                "src_file": "/home/user3/file",
                "backup_name": "user2_backup",
                "log_file": "/home/user3/specific_log_file",
                "container": "my_backup_container"
            }
        }],
        "description": "scheduled one shot"
    }


Actions
=======

Actions are stored only to facilitate the assembling of different actions into jobs in the web UI.
They are not directly used by the scheduler.
They are stored in this structure

.. code-block::

  {
      "freezer_action": {
        "action": string,
        "backup_name": string,
        ....
      },
      "mandatory": bool,
      "max_retries": int,
      "max_retries_interval": int

      "action_id": string,
      "user_id": string
  }


Sessions
========

A session is a group of jobs which share the same scheduling time. A session is identified
by its **session_id** and has a numeric tag (**session_tag**) which is incremented each time that a new session
is started.
The purpose of the *session_tag* is that of identifying a group of jobs which have been executed
together and which therefore represent a snapshot of a distributed system.

When a job is added to a session, the scheduling time of the session is copied into the
job data structure, so that any job belonging to the same session will start at the same time.


Session Data Structure
-----------------------

.. code-block::

  session =
  {
    "session_id": string,
    "session_tag": int,
    "description": string,
    "hold_off": int (seconds),
    "schedule": { scheduling information, same as jobs },
    "jobs": { 'job_id_1': {
                "client_id": string,
                "status": string,
                "result": string
                "time_started": int  (timestamp),
                "time_ended":   int  (timestamp),
              },
              'job_id_2': {
                "client_id": string,
                "status": string,
                "result": string
                "time_started": int  (timestamp),
                "time_ended":   int  (timestamp),
              }
            }
    "time_start": int timestamp,
    "time_end": int timestamp,
    "time_started": int  (timestamp),
    "time_ended":   int  (timestamp),
    "status": string "completed" "running",
    "result": string "success" "fail",
    "user_id": string
  }

Session actions
---------------

When the freezer scheduler running on a node wants to start a session,
it sends a POST request to the following endpoint:

.. code-block::

    POST   /v1/sessions/{sessions_id}/action

The body of the request bears the action and parameters

Session START action
---------------------

.. code-block::

    {
        "start": {
            "job_id": "JOB_ID_HERE",
            "current_tag": 22
        }
    }

Example of a successful response

.. code-block::

    {
        'result': 'success',
        'session_tag': 23
    }

Session STOP action
--------------------

.. code-block::

    {
        "end": {
            "job_id": "JOB_ID_HERE",
            "current_tag": 23,
            "result": "success|fail"
        }
    }

Session-Job association
------------------------

.. code-block::

    PUT    /v1/sessions/{sessions_id}/jobs/{job_id}    adds the job to the session
    DELETE /v1/sessions/{sessions_id}/jobs/{job_id}    adds the job to the session

Known Issues
=============

Versions of falcon < 0.1.8
---------------------------

Versions of `falcon <https://falconframework.org/>`_ prior to 0.1.8 (to be precise,
before `this commit <https://github.com/falconry/falcon/commit/8805eb400e62f74ef548a39a597a0ac5948cd57e>`_)
do not have support for error handlers, which are used internally by freezer-api
to specify the outcomes of various actions.

The absence of this error handling support means that freezer-api **will not start**
on systems running the following, otherwise supported stable versions of
falcon:

* 0.1.6
* 0.1.7

falcon 0.1.8, which was released on Jan 14, 2014, and all newer versions support
this functionality.
