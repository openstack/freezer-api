"""
(c) Copyright 2016 Hewlett-Packard Enterprise Development Company, L.P.

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
import falcon
from paste import deploy
from pkg_resources import parse_version

from freezer_api.cmd.api import build_app_v0
from freezer_api.cmd.api import build_app_v1
from freezer_api.common import config


# Define the minimum version of falcon at which we can use the "new" invocation
# style for middleware (aka v1), i.e. the "middleware" named argument for
# falcon.API.
FALCON_MINVERSION_MIDDLEWARE = parse_version('0.2.0b1')


def freezer_app_factory(global_conf, **local_conf):
    current_version = parse_version(
        falcon.__version__ if hasattr(falcon, '__version__') else falcon.version)

    # Check the currently installed version of falcon in order to invoke it
    # correctly.
    if current_version < FALCON_MINVERSION_MIDDLEWARE:
        return build_app_v0()
    else:
        return build_app_v1()


def initialize_app(conf=None, name='main'):
    try:
        config.parse_args()
        config.setup_logging()
    except Exception as e:
        pass
    conf = config.find_paste_config()
    app = deploy.loadapp('config:%s' % conf, name=name)
    return app

