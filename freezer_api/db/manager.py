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

import sys

from oslo_log import log
from oslo_utils import importutils
from stevedore import driver

LOG = log.getLogger(__name__)


_DB_DRIVER_NAMESPACE = "freezer.db.backends"


def _load_class_by_alias_or_classname(namespace, name):
    """Load class using stevedore alias or the class name
    :param namespace: namespace where the alias is defined
    :param name: alias or class name of the class to be loaded
    :returns: class if calls can be loaded
    :raises ImportError if class cannot be loaded
    """

    if not name:
        LOG.error("Alias or class name is not set")
        raise ImportError("Class not found.")
    try:
        # Try to resolve class by alias
        mgr = driver.DriverManager(
            namespace, name, warn_on_missing_entrypoint=False)
        class_to_load = mgr.driver
    except RuntimeError:
        e1_info = sys.exc_info()
        # Fallback to class name
        try:
            class_to_load = importutils.import_class(name)
        except (ImportError, ValueError):
            LOG.error("Error loading class by alias",
                      exc_info=e1_info)
            LOG.error("Error loading class by class name",
                      exc_info=True)
            raise ImportError("Class not found.")
    return class_to_load


def get_db_driver(name, backend):
    """
    Loads database driver
    :param name: name of the database driver.
    :return: Instance of the driver class
    """
    driver_class = _load_class_by_alias_or_classname(_DB_DRIVER_NAMESPACE,
                                                     name)
    return driver_class(backend=backend)
