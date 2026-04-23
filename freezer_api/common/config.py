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
from oslo_policy import policy

from freezer_api import __version__ as FREEZER_API_VERSION

CONF = cfg.CONF
LOG = log.getLogger(__name__)

AUTH_GROUP, AUTH_OPTS = opts.list_auth_token_opts()[0]

paste_deploy = [
    cfg.StrOpt('config_file', default='freezer-paste.ini',
               help='Name of the paste configuration file that defines '
                    'the available pipelines.'),
]

_DB_DRIVERS = [
    cfg.StrOpt("backend",
               default='sqlalchemy',
               help="Database backend section name. This section will "
                    "be loaded by the proper driver to connect to "
                    "the database.",
               deprecated_for_removal=True,
               deprecated_reason="Elasticsearch DB storage is deprecated "
                                 "and will be removed in the next release. "
                                 "The only supported storage driver is "
                                 "SQLAlchemy.",
               deprecated_since="2026.2",
               ),
    cfg.StrOpt('driver',
               default='sqlalchemy',
               help="Database driver to be used.",
               deprecated_for_removal=True,
               deprecated_reason="Elasticsearch DB storage is deprecated "
                                 "and will be removed in the next release. "
                                 "The only supported storage driver is "
                                 "SQLAlchemy.",
               deprecated_since="2026.2",
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
                    help="""Default False, the v2 Freezer API will be deployed.
                    When this option is set
                    to ``True``, Freezer-API service will respond
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
                    """)
    ]

    return _COMMON


def centralized_scheduler_opts():
    """Return a list of centralized scheduler options."""
    options = [
        cfg.BoolOpt('enabled',
                    default=True,
                    help="""Default True.
                    When this option is set to ``True``, Freezer-API
                    enables centralized scheduler mode and
                    trusts will be created for jobs which are associated with
                    clients created with `is_central` property.
                    Setting option to ``False`` will disable trust creation
                    by API.
                    """),
        cfg.BoolOpt('enforce_trusts',
                    default=False,
                    help="""Default False.
                    When this option is set to ``True``, Freezer-API
                    will always create keystone trusts for jobs regardless
                    of the client type. If False (default), trusts are
                    created only for central clients.
                    """),
        cfg.StrOpt('service_user',
                   deprecated_for_removal=True,
                   deprecated_reason='Use auth_section instead to derive ID',
                   help="""Required in centralized scheduler mode.
                   ID or name of the service user (trustee) that will be used
                   to create trusts for delegated authorization.
                   """),
        cfg.StrOpt('service_user_domain',
                   default='default',
                   deprecated_for_removal=True,
                   deprecated_reason='Use auth_section instead to derive ID',
                   help="""Required if "service_user" is a name.
                   ID or Name of the domain where "service_user" is
                   located.
                   """),
        cfg.StrOpt('auth_section',
                   default='keystone_authtoken',
                   help="""Config section where scheduler auth plugin options
                   are defined. Defaults to 'keystone_authtoken', using the
                   ID of the service account configured there as the trustee.
                   """),
        cfg.ListOpt('trusts_delegated_roles',
                    default=['member'],
                    help=("""Subset of trustor roles to be delegated to
                    freezer. If left unset, all roles of a user will be
                    delegated to freezer when creating a job.""")),
    ]
    return options


def register_centralized_scheduler_opts():
    """Register centralized scheduler options."""
    opt_group = cfg.OptGroup(name='centralized_scheduler',
                             title='Centralized scheduler Options')
    CONF.register_group(opt_group)
    CONF.register_opts(centralized_scheduler_opts(), group=opt_group)


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
    register_centralized_scheduler_opts()
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

    For example:
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


def get_keystone_endpoint():
    try:
        # Prefer auth_url over www_authenticate_uri for internal service
        # to service communication
        auth_uri = getattr(CONF.keystone_authtoken, 'auth_url',
                           CONF.keystone_authtoken.www_authenticate_uri)
    except cfg.NoSuchOptError:
        LOG.error('Keystone API endpoint not provided. Set '
                  'auth_url or www_authenticate_uri in section '
                  '[keystone_authtoken] of the configuration file.')
        raise
    return auth_uri


def get_keystone_cert_options():
    cacert = CONF.keystone_authtoken.cafile
    insecure = CONF.keystone_authtoken.insecure
    cert = CONF.keystone_authtoken.certfile
    key = CONF.keystone_authtoken.keyfile
    if insecure:
        verify = False
    else:
        verify = cacert or True
    if cert and key:
        cert = (cert, key)
    return {'verify': verify, 'cert': cert}
