"""
(c) Copyright 2014,2015 Hewlett-Packard Development Company, L.P.

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

from freezer_api.storage import elastic

from oslo_config import cfg
from oslo_log import log
from oslo_utils import importutils


CONF = cfg.CONF
LOG = log.getLogger(__name__)


# storage backend options to be registered
_OPTS = [
    cfg.StrOpt("backend",
               help="Databse backend section name. This section "
                    "will be loaded by the proper driver to connect to "
                    "the database."
               ),
    cfg.StrOpt('driver',
               default='freezer_api.storage.elastic.ElasticSearchEngine',
               help="Database driver to be used."
               )
]


def register_storage_opts():
    """Register storage configuration options"""
    opt_group = cfg.OptGroup(name='storage',
                             title='Freezer Storage Engine')
    CONF.register_group(opt_group)
    CONF.register_opts(_OPTS, group=opt_group)


def get_db(driver=None):
    """Automatically loads the database driver to be used."""
    storage = CONF.get('storage')
    if not driver:
        driver = storage['driver']
    driver_instance = importutils.import_object(
        driver,
        backend=storage['backend']
    )

    return driver_instance


def get_storage_opts():
    """Returns a dict that contains list of options for db backend"""
    opts = {"storage": _OPTS}
    opts.update(_get_elastic_opts())
    return opts


def _get_elastic_opts(backend=None):
    """Return Opts for elasticsearch driver"""
    if not backend:
        backend = "elasticsearch"
    es = elastic.ElasticSearchEngine(backend=backend)
    return {backend: es.get_opts()}
