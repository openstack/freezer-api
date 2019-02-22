"""
(c) Copyright 2015-2016 Hewlett-Packard Enterprise Development Company, L.P.

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
from __future__ import print_function
import sys

from oslo_config import cfg
from oslo_log import log
from oslo_serialization import jsonutils as json

from freezer_api import __version__ as FREEZER_API_VERSION
from freezer_api.common import config
from freezer_api.db import manager


CONF = cfg.CONF
LOG = log.getLogger(__name__)


DEFAULT_INDEX = 'freezer'
DEFAULT_REPLICAS = 0


def add_db_opts(subparser):
    parser = subparser.add_parser('db')
    parser.add_argument(
        'options',
        choices=['sync', 'update', 'remove', 'show', 'update-settings'],
        help='Create/update/delete freezer-api mappings in DB backend.'
    )


def parse_config():
    DB_INIT = [
        cfg.SubCommandOpt('db',
                          dest='db',
                          title='DB Options',
                          handler=add_db_opts
                          )
    ]
    # register database backend drivers
    config.register_db_drivers_opt()
    # register database cli options
    CONF.register_cli_opts(DB_INIT)
    # register logging opts
    log.register_options(CONF)
    default_config_files = cfg.find_config_files('freezer', 'freezer-api')
    CONF(args=sys.argv[1:],
         project='freezer-api',
         default_config_files=default_config_files,
         version=FREEZER_API_VERSION
         )


def main():
    parse_config()
    config.setup_logging()

    if not CONF.db:
        CONF.print_help()
        sys.exit(0)

    try:
        db_driver = manager.get_db_driver(CONF.storage.driver,
                                          backend=CONF.storage.backend)
        if CONF.db.options.lower() == 'sync':
            db_driver.db_sync()
        elif CONF.db.options.lower() == 'update':
            db_driver.db_sync()
        elif CONF.db.options.lower() == 'remove':
            db_driver.db_remove()
        elif CONF.db.options.lower() == 'show':
            db_tables = db_driver.db_show()
            if db_tables:
                print(json.dumps(db_tables))
            else:
                print("No Tables/Mappings found!")
        else:
            raise Exception('Option {0} not found !'.format(CONF.db.options))
    except Exception as e:
        LOG.error(e)
        print(e)


if __name__ == '__main__':
    sys.exit(main())
