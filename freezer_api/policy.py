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

import functools

from oslo_config import cfg
from oslo_policy import opts
from oslo_policy import policy

from freezer_api.common import exceptions
from freezer_api.common import policies

# TODO(gmann): Remove setting the default value of config policy_file
# once oslo_policy change the default value to 'policy.yaml'.
# https://github.com/openstack/oslo.policy/blob/a626ad12fe5a3abd49d70e3e5b95589d279ab578/oslo_policy/opts.py#L49
DEFAULT_POLICY_FILE = 'policy.yaml'
opts.set_defaults(cfg.CONF, DEFAULT_POLICY_FILE)

ENFORCER = None


def setup_policy(conf):
    global ENFORCER

    if not ENFORCER:
        ENFORCER = policy.Enforcer(conf)
        ENFORCER.register_defaults(policies.list_rules())
        ENFORCER.load_rules()


def enforce(rule):

    def decorator(func):
        @functools.wraps(func)
        def handler(*args, **kwargs):
            ctx = args[1].env['freezer.context']
            ENFORCER.enforce(rule, {}, ctx.to_dict(), do_raise=True,
                             exc=exceptions.AccessForbidden)
            return func(*args, **kwargs)
        return handler

    return decorator
