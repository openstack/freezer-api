"""
(c) Copyright 2014,2015 Hewlett-Packard Development Company, L.P.
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

import sys

import falcon
from oslo_config import cfg
from oslo_log import log
from paste import deploy
from paste import httpserver

from freezer_api.api.common import middleware
from freezer_api.api.common import utils
from freezer_api.api import v1
from freezer_api.api import v2
from freezer_api.common import _i18n
from freezer_api.common import config
from freezer_api.common import exceptions as freezer_api_exc
from freezer_api.db import manager
from freezer_api import policy


CONF = cfg.CONF
_LOG = log.getLogger(__name__)


def configure_app(app, db=None):
    """Build routes and exception handlers

    :param app: falcon WSGI app
    :param db: Database engine (ElasticSearch)
    :return:
    """
    db_driver = manager.get_db_driver(CONF.storage.driver,
                                      backend=CONF.storage.backend)
    db = db_driver.get_api()

    # setup freezer policy
    policy.setup_policy(CONF)

    for exception_class in freezer_api_exc.exception_handlers_catalog:
        app.add_error_handler(exception_class, exception_class.handle)

    endpoint_catalog = [
        ('', v1.public_endpoints(db))
    ]
    for version_path, endpoints in endpoint_catalog:
        for route, resource in endpoints:
            app.add_route(version_path + route, resource)

    return app


def build_app_v1():
    """Building routes and forming the root freezer-api app

    This uses the 'middleware' named argument to specify middleware for falcon
    instead of the 'before' and 'after' hooks that were removed after 0.3.0
    (both approaches were available for versions 0.2.0 - 0.3.0)

    :return: falcon WSGI app
    """
    # injecting FreezerContext & hooks
    middleware_list = [utils.FuncMiddleware(hook) for hook in
                       utils.before_hooks()]
    middleware_list.append(middleware.RequireJSON())
    middleware_list.append(middleware.JSONTranslator())

    # The signature of falcon.API() differs between versions, suppress pylint:
    # pylint: disable=unexpected-keyword-arg
    app = falcon.API(middleware=middleware_list)
    # Set options to keep behavior compatible to pre-2.0.0 falcon
    app.req_options.auto_parse_qs_csv = True
    app.req_options.keep_blank_qs_values = False
    app.req_options.strip_url_path_trailing_slash = True

    app = configure_app(app)
    return app


def build_app_v2():
    """Building routes and forming the root freezer-api app
    This uses the 'middleware' named argument to specify middleware for falcon
    instead of the 'before' and 'after' hooks that were removed after 0.3.0
    (both approaches were available for versions 0.2.0 - 0.3.0)
    :return: falcon WSGI app
    """
    # injecting FreezerContext & hooks
    middleware_list = [utils.FuncMiddleware(hook) for hook in
                       utils.before_hooks()]
    middleware_list.append(middleware.RequireJSON())
    middleware_list.append(middleware.JSONTranslator())

    app = falcon.API(middleware=middleware_list)
    db_driver = manager.get_db_driver(CONF.storage.driver,
                                      backend=CONF.storage.backend)
    db = db_driver.get_api()

    # Set options to keep behavior compatible to pre-2.0.0 falcon
    app.req_options.auto_parse_qs_csv = True
    app.req_options.keep_blank_qs_values = False
    app.req_options.strip_url_path_trailing_slash = True

    # setup freezer policy
    policy.setup_policy(CONF)

    for exception_class in freezer_api_exc.exception_handlers_catalog:
        app.add_error_handler(exception_class, exception_class.handle)

    endpoint_catalog = [
        ('', v2.public_endpoints(db))
    ]
    for version_path, endpoints in endpoint_catalog:
        for route, resource in endpoints:
            app.add_route(version_path + route, resource)

    return app


def main():
    # setup opts
    config.parse_args(args=sys.argv[1:])
    config.setup_logging()
    paste_conf = config.find_paste_config()

    # quick simple server for testing purposes or simple scenarios
    ip = CONF.get('bind_host', '0.0.0.0')
    port = CONF.get('bind_port', 9090)
    try:
        httpserver.serve(
            application=deploy.loadapp('config:%s' % paste_conf, name='main'),
            host=ip,
            port=port)
        message = (_i18n._('Server listening on %(ip)s:%(port)s') %
                   {'ip': ip, 'port': port})
        _LOG.info(message)
        print(message)
    except KeyboardInterrupt:
        print(_i18n._("Thank You ! \nBye."))
        sys.exit(0)


if __name__ == '__main__':
    main()
