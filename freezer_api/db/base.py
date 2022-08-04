"""
(c) Copyright 2014,2015 Hewlett-Packard Development Company, L.P.
(C) Copyright 2016-2018 Hewlett Packard Enterprise Development Company LP
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

import abc
from oslo_config import cfg
from oslo_log import log

CONF = cfg.CONF
LOG = log.getLogger(__name__)


class DBDriver(metaclass=abc.ABCMeta):

    _OPTS = [
        cfg.StrOpt('host',
                   required=True,
                   default='0.0.0.0',
                   help="Database host"),
        cfg.StrOpt("username",
                   help="Database username"),
        cfg.StrOpt("password",
                   help="Database Password")
    ]

    def __init__(self, backend, is_created=False):
        if not is_created:
            grp = cfg.OptGroup(backend)
            CONF.register_group(grp)
            CONF.register_opts(self._OPTS, grp)
        self.conf = CONF.get(backend)
        self.backend = backend

    def connect(self):
        pass

    @property
    @abc.abstractmethod
    def name(self):
        """Name of the database driver"""
        pass

    def get_instance(self):
        pass
