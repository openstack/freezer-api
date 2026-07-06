# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from freezer_api.common import exceptions


def check_client_capabilities(freezer_actions: list[dict], client):
    # Check whether the client can execute every action of the job.
    # Takes the list of ``freezer_action`` definitions (not the full job
    # document) so it works the same for create, update and replace handlers.
    capabilities = ["action", "mode", "storage", "engine"]
    client = client["client"]
    for freezer_action in freezer_actions:
        if not freezer_action:
            continue
        for capability in capabilities:
            option = freezer_action.get(capability, None)
            # if option is not set, we don't need to check
            if not option:
                continue
            if option not in client.get(f"supported_{capability}s"):
                raise exceptions.UnprocessableEntity(
                    f"Client {client['client_id']} does not support "
                    f"{capability}: {option}")
