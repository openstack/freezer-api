"""
(c) Copyright 2015-2016 Hewlett-Packard Enterprise Company L.P.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os

from keystonemiddleware import opts
from oslo_config import cfg
from oslo_log import log
from oslo_policy import opts as policy_opts
from oslo_policy import policy

from freezer_api import __version__ as FREEZER_API_VERSION

CONF = cfg.CONF

AUTH_GROUP, AUTH_OPTS = opts.list_auth_token_opts()[0]

paste_deploy = [
    cfg.StrOpt('config_file', default='freezer-paste.ini',
               help='Name of the paste configuration file that defines '
                    'the available pipelines.'),
]

_DB_DRIVERS = [
    cfg.StrOpt("backend",
               help="Database backend section name. This section will "
                    "be loaded by the proper driver to connect to "
                    "the database."
               ),
    cfg.StrOpt('driver',
               # default='freezer_api.storage.elastic.ElasticSearchEngine',
               default='elasticsearch',
               help="Database driver to be used."
               )
]


def api_common_opts():

    _COMMON = [
        cfg.IPOpt('bind-host',
                  default='0.0.0.0',
                  dest='bind_host',
                  help='IP address to listen on. Default is 0.0.0.0'),
        cfg.PortOpt('bind-port',
                    default=9090,
                    dest='bind_port',
                    help='Port number to listen on. Default is 9090'
                    ),
        cfg.BoolOpt('enable_v1_api',
                    default=False,
                    help="""Default False, That is the v2 Freezer API
                    will be deployed. When this option is set
                    to ``True``, Freezer-api service will respond
                    to requests on registered endpoints conforming
                    to the v1 OpenStack Freezer api.
                    The v1 OpenStack Freezer API functions
                    as follows:
                        * Multi-tenancy is not supported under this
                         api version.
                        * Everything is user based.
                        * Freezer api v1 supports Oslo.db.
                        * Use elasticsearch db with v1 api version
                    The v2 OpenStack Freezer API functions
                    as follows:
                        * Multi-tenancy is supported under this api version.
                        * Freezer api v2 supports Oslo.db.
                        * Recommended to use oslo.db with api v2
                    Possible values:
                        * True
                        * False
                    """)
    ]

    return _COMMON


def register_db_drivers_opt():
    """Register storage configuration options"""
    # storage backend options to be registered

    opt_group = cfg.OptGroup(name='storage',
                             title='Freezer Database drivers')
    CONF.register_group(opt_group)
    CONF.register_opts(_DB_DRIVERS, group=opt_group)


def parse_args(args=[]):
    CONF.register_cli_opts(api_common_opts())
    register_db_drivers_opt()
    # register paste configuration
    paste_grp = cfg.OptGroup('paste_deploy',
                             'Paste Configuration')
    CONF.register_group(paste_grp)
    CONF.register_opts(paste_deploy, group=paste_grp)
    log.register_options(CONF)
    default_config_files = cfg.find_config_files('freezer', 'freezer-api')
    CONF(args=args,
         project='freezer-api',
         default_config_files=default_config_files,
         version=FREEZER_API_VERSION
         )
    policy.Enforcer(CONF)


def setup_logging():
    _DEFAULT_LOG_LEVELS = ['amqp=WARN', 'amqplib=WARN', 'boto=WARN',
                           'stevedore=WARN', 'oslo_log=INFO',
                           'iso8601=WARN', 'elasticsearch=WARN',
                           'requests.packages.urllib3.connectionpool=WARN',
                           'urllib3.connectionpool=WARN', 'websocket=WARN',
                           'keystonemiddleware=WARN', 'routes.middleware=WARN']
    _DEFAULT_LOGGING_CONTEXT_FORMAT = ('%(asctime)s.%(msecs)03d %(process)d '
                                       '%(levelname)s %(name)s [%(request_id)s'
                                       ' %(user_identity)s] %(instance)s '
                                       '%(message)s')
    log.set_defaults(_DEFAULT_LOGGING_CONTEXT_FORMAT, _DEFAULT_LOG_LEVELS)
    log.setup(CONF, 'freezer-api', version=FREEZER_API_VERSION)


def find_paste_config():
    """Find freezer's paste.deploy configuration file.
    freezer's paste.deploy configuration file is specified in the
    ``[paste_deploy]`` section of the main freezer-api configuration file,
    ``freezer-api.conf``.
    For example::
        [paste_deploy]
        config_file = freezer-paste.ini
    :returns: The selected configuration filename
    :raises: exception.ConfigFileNotFound
    """
    if CONF.paste_deploy.config_file:
        paste_config = CONF.paste_deploy.config_file
        if not os.path.isabs(paste_config):
            paste_config = CONF.find_file(paste_config)
    elif CONF.config_file:
        paste_config = CONF.config_file[0]
    else:
        # this provides backwards compatibility for keystone.conf files that
        # still have the entire paste configuration included, rather than just
        # a [paste_deploy] configuration section referring to an external file
        paste_config = CONF.find_file('freezer-api.conf')
    if not paste_config or not os.path.exists(paste_config):
        raise Exception('paste configuration file {0} not found !'.
                        format(paste_config))
    return paste_config


def list_opts():
    _OPTS = {
        None: api_common_opts(),
        'paste_deploy': paste_deploy,
        AUTH_GROUP: AUTH_OPTS
    }
    # update the current list of opts with db backend drivers opts
    _OPTS.update({"storage": _DB_DRIVERS})
    return _OPTS.items()


def set_lib_defaults():
    """Update default value for configuration options from other namespace.

    Example, oslo lib config options. This is needed for
    config generator tool to pick these default value changes.
    https://docs.openstack.org/oslo.config/latest/cli/
    generator.html#modifying-defaults-from-other-namespaces
    """

    # TODO(gmann): Remove setting the default value of config policy_file
    # once oslo_policy change the default value to 'policy.yaml'.
    # https://github.com/openstack/oslo.policy/blob/a626ad12fe5a3abd49d70e3e5b95589d279ab578/oslo_policy/opts.py#L49
    policy_opts.set_defaults(CONF, 'policy.yaml')
