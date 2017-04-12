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

from __future__ import print_function

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
from freezer_api import policy
from freezer_api.storage import driver


CONF = cfg.CONF
_LOG = log.getLogger(__name__)


def configure_app(app, db=None):
    """Build routes and exception handlers

    :param app: falcon WSGI app
    :param db: Database engine (ElasticSearch)
    :return:
    """
    if not db:
        db = driver.get_db(
            driver='freezer_api.storage.elastic.ElasticSearchEngine'
        )

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


def build_app_v0():
    """Instantiate the root freezer-api app

    Old versions of falcon (< 0.2.0) don't have a named 'middleware' argument.
    This was introduced in version 0.2.0b1, so before that we need to instead
    provide "before" hooks (request processing) and "after" hooks (response
    processing).

    :return: falcon WSGI app
    """

    # injecting FreezerContext & hooks
    before_hooks = utils.before_hooks() + [
        middleware.RequireJSON().as_before_hook()]
    after_hooks = [middleware.JSONTranslator().as_after_hook()]
    # The signature of falcon.API() differs between versions, suppress pylint:
    # pylint: disable=unexpected-keyword-arg
    app = falcon.API(before=before_hooks, after=after_hooks)

    app = configure_app(app)
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
    db = driver.get_db()

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
