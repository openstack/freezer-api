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

import sys

from oslo_config import cfg
from oslo_log import log

from freezer_api import __version__ as FREEZER_API_VERSION
from freezer_api.storage import driver
from keystonemiddleware import opts

CONF = cfg.CONF


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
                    )
    ]

    return _COMMON


def parse_args():
    CONF.register_cli_opts(api_common_opts())
    driver.register_elk_opts()
    log.register_options(CONF)
    default_config_files = cfg.find_config_files('freezer', 'freezer-api')
    CONF(args=sys.argv[1:],
         project='freezer-api',
         default_config_files=default_config_files,
         version=FREEZER_API_VERSION
         )


def setup_logging():
    _DEFAULT_LOG_LEVELS = ['amqp=WARN', 'amqplib=WARN', 'boto=WARN',
                           'qpid=WARN', 'stevedore=WARN','oslo_log=INFO',
                           'iso8601=WARN',
                           'requests.packages.urllib3.connectionpool=WARN',
                           'urllib3.connectionpool=WARN', 'websocket=WARN',
                           'keystonemiddleware=WARN', 'routes.middleware=WARN']
    _DEFAULT_LOGGING_CONTEXT_FORMAT = ('%(asctime)s.%(msecs)03d %(process)d '
                                       '%(levelname)s %(name)s [%(request_id)s '
                                       '%(user_identity)s] %(instance)s '
                                       '%(message)s')
    log.set_defaults(_DEFAULT_LOGGING_CONTEXT_FORMAT, _DEFAULT_LOG_LEVELS)
    log.setup(CONF, 'freezer-api', version=FREEZER_API_VERSION)


def list_opts():
    _OPTS = {
        None: api_common_opts(),
        'storage': driver.get_elk_opts(),
        opts.auth_token_opts[0][0]: opts.auth_token_opts[0][1]
    }
    return _OPTS.items()

