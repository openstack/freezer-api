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


def check_client_capabilities(job_actions, client):
    # Check if the client has the capabilities to execute the job.
    # Using job_actions instead of the full job document for compatibility
    # with both create and update API endpoint handlers.
    capabilities = ["action", "mode", "storage", "engine"]
    client = client["client"]
    for action in job_actions:
        for capability in capabilities:
            if "freezer_action" not in action:
                raise exceptions.BadDataFormat(
                    "job_actions: missing 'freezer_action' in job_actions"
                    "list item")
            option = action["freezer_action"].get(capability, None)
            # if option is not set, we don't need to check
            if not option:
                continue
            if option not in client.get(f"supported_{capability}s"):
                raise exceptions.UnprocessableEntity(
                    f"Client does not support {capability}: {option}")
