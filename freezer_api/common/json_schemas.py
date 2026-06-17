"""
Copyright 2015 Hewlett-Packard

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

fqdn_regex = "([a-zA-Z\\d]|[a-zA-Z\\d][a-zA-Z\\d\\-]{0,61}[a-zA-Z\\d])" \
             "(\\.([a-zA-Z\\d]|[a-zA-Z\\d][a-zA-Z\\d\\-]{0,61}[a-zA-Z\\d]))*"
# Allow alphanumeric, underscore and minus
project_regex = r"(?:([\w\-]+)\_)?"
client_id_regex = r"^{project}{host}$".format(project=project_regex,
                                              host=fqdn_regex)

SUPPORTED_ACTIONS = ['backup', 'restore', 'info', 'admin', 'exec']
SUPPORTED_MODES = ['fs', 'mongo', 'mysql', 'sqlserver', 'cinder',
                   'glance', 'cindernative', 'nova']
SUPPORTED_STORAGES = ['local', 'swift', 'ssh', 's3', 'ftp', 'ftps']
SUPPORTED_ENGINES = ['tar', 'rsync', 'rsyncv2', 'nova', 'osbrick',
                     'glance']

freezer_action_properties = {
    "action": {
        "id": "action",
        "type": "string",
        "enum": SUPPORTED_ACTIONS,
        "description": "The action type."
    },
    "mode": {
        "id": "mode",
        "type": ["string", "null"],
        "enum": SUPPORTED_MODES + [None],
        "description": "The mode of the backup/restore operation."
    },
    "path_to_backup": {
        "id": "path_to_backup",
        "type": ["string", "null"],
        "description": "The absolute file/directory path to backup."
    },
    "backup_name": {
        "id": "backup_name",
        "type": ["string", "null"],
        "description": "The name of the backup."
    },
    "container": {
        "id": "container",
        "type": ["string", "null"],
        "description": (
            "The swift or S3 container name where the "
            "backup is stored."
        )
    },
    "restore_abs_path": {
        "id": "restore_abs_path",
        "type": ["string", "null"],
        "description": (
            "The absolute path on the client machine where "
            "the backup will be restored."
        )
    },
}

schedule_properties = {
    "time_created": {
        "id": "time_created",
        "type": "integer",
        "description": "The epoch timestamp when the resource was created."
    },
    "time_started": {
        "id": "time_started",
        "type": "integer",
        "description": "The epoch timestamp when the execution started."
    },
    "time_ended": {
        "id": "time_ended",
        "type": "integer",
        "description": "The epoch timestamp when the execution ended."
    },
    "event": {
        "id": "event",
        "type": "string",
        "enum": ["", "stop", "start", "abort", "remove"],
        "description": "An event trigger to control execution."
    },
    "status": {
        "id": "status",
        "type": "string",
        "enum": ["", "completed", "stop", "scheduled",
                 "running", "aborting", "removed"],
        "description": "The status of the scheduled resource."
    },
    "result": {
        "id": "result",
        "type": "string",
        "enum": ["", "success", "fail", "aborted"],
        "description": "The result status of the execution."
    },
    "schedule_date": {
        "id": "schedule_date",
        "type": "string",
        "pattern": r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])"
                   r"-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9])"
                   r":([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-]"
                   r"(?:2[0-3]|[01][0-9]):[0-5][0-9])?$",
        "description": (
            "The date and time when the schedule starts. Must match "
            "ISO 8601 date-time format (e.g., ``YYYY-MM-DDThh:mm:ss``)."
        )
    },
    "schedule_interval": {
        "id": "schedule_interval",
        "type": "string",
        "pattern": r"^(continuous|(\d+ +(weeks|days|"
                   r"hours|minutes|seconds)))$",
        "description": (
            "The execution interval. Must match interval format "
            "(e.g., ``continuous``, ``5 minutes``, ``2 hours``, "
            "``1 days``)."
        )
    },
    "schedule_start_date": {
        "id": "schedule_start_date",
        "type": "string",
        "pattern": r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])"
                   r"-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):"
                   r"([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-]"
                   r"(?:2[0-3]|[01][0-9]):[0-5][0-9])?$",
        "description": (
            "The date and time when the schedule starts. Must match "
            "ISO 8601 date-time format (e.g., ``YYYY-MM-DDThh:mm:ss``)."
        )
    },
    "schedule_end_date": {
        "id": "schedule_end_date",
        "type": "string",
        "pattern": r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])"
                   r"-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9])"
                   r":([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-]"
                   r"(?:2[0-3]|[01][0-9]):[0-5][0-9])?$",
        "description": (
            "The date and time when the schedule ends. Must match "
            "ISO 8601 date-time format (e.g., ``YYYY-MM-DDThh:mm:ss``)."
        )
    },
    "schedule_year": {
        "id": "schedule_year",
        "type": "string",
        "pattern": r"^\d{4}$",
        "description": (
            "The schedule year. Must match a 4-digit year format "
            "(e.g., ``YYYY``)."
        )
    },
    "schedule_month": {
        "id": "schedule_month",
        "type": "string",
        "description": "The schedule_month property."
    },
    "schedule_day": {
        "id": "schedule_day",
        "type": "string",
        "description": "The schedule_day property."
    },
    "schedule_week": {
        "id": "schedule_week",
        "type": "string",
        "description": "The schedule_week property."
    },
    "schedule_day_of_week": {
        "id": "schedule_day_of_week",
        "type": "string"
    },
    "schedule_hour": {
        "id": "schedule_hour",
        "type": "string"
    },
    "schedule_minute": {
        "id": "schedule_minute",
        "type": "string"
    },
    "schedule_second": {
        "id": "schedule_second",
        "type": "string"
    },
    "current_pid": {
        "id": "current_pid",
        "type": "integer",
        "description": "The OS process ID of the running execution."
    }
}

job_schema = {
    "id": "/",
    "type": "object",
    "definitions": {
        "freezer_action": {
            "properties": freezer_action_properties,
            "additionalProperties": True
        },
        "job_action": {
            "properties": {
                "freezer_action": {
                    "$ref": "#/definitions/freezer_action"
                },
                "max_retries": {
                    "type": "integer",
                    "description": (
                        "The maximum number of retries in case of "
                        "execution failure."
                    )
                },
                "max_retries_interval": {
                    "type": "integer",
                    "description": (
                        "The interval (in seconds) to wait between retries."
                    )
                },
                "mandatory": {
                    "type": "boolean",
                    "description": (
                        "Whether the action is mandatory for the "
                        "job execution."
                    )
                }
            },
            "additionalProperties": True
        },
        "job_action_list": {
            "items": {
                "$ref": "#/definitions/job_action"
            }
        },
        "user_credentials": {
            "properties": {
                "trust_id": {
                    "id": "trust_id",
                    "type": "string",
                    "description": (
                        "The OpenStack trust ID used for client "
                        "authentication."
                    )
                },
                "trustor_user_id": {
                    "id": "trustor_user_id",
                    "pattern": r"^[\w-]+$",
                    "type": "string",
                    "description": "The OpenStack user ID of the trustor."
                },
            },
            "additionalProperties": True,
            "required": [
                "trust_id",
                "trustor_user_id",
            ]
        },
    },
    "properties": {
        "job_actions": {
            "$ref": "#/definitions/job_action_list"
        },
        "job_schedule": {
            "id": "job_schedule",
            "type": "object",
            "properties": schedule_properties,
            "additionalProperties": False,
        },
        "job_id": {
            "id": "job_id",
            "pattern": r"^[\w-]+$",
            "type": "string"
        },
        "client_id": {
            "id": "client_id",
            "pattern": client_id_regex,
            "type": "string"
        },
        "session_id": {
            "id": "session_id",
            "pattern": r"^[\w-]*$",
            "type": ["string", "null"]
        },
        "session_tag": {
            "id": "session_tag",
            "type": "integer"
        },
        "session_name": {
            "id": "session_name",
            "type": ["string", "null"]
        },
        "user_id": {
            "id": "user_id",
            "pattern": r"^[\w-]+$",
            "type": "string"
        },
        "project_id": {
            "id": "project_id",
            "pattern": r"^[\w-]+$",
            "type": "string"
        },
        "description": {
            "id": "description",
            "type": ["string", "null"]
        },
        "_version": {
            "id": "_version",
            "type": "integer"
        },
        "action_defaults": {
            "$ref": "#/definitions/freezer_action"
        },
        "user_credentials": {
            "$ref": "#/definitions/user_credentials"
        },
    },
    "additionalProperties": False,
    "required": [
        "job_actions",
        "job_schedule",
        "job_id",
        "client_id",
        "user_id"
    ]
}

job_patch_schema = {
    "id": "/",
    "type": "object",
    "definitions": {
        "freezer_action": {
            "properties": freezer_action_properties,
            "additionalProperties": True
        },
        "job_action": {
            "properties": {
                "freezer_action": {
                    "$ref": "#/definitions/freezer_action"
                },
                "max_retries": {
                    "type": "integer"
                },
                "max_retries_interval": {
                    "type": "integer"
                },
                "mandatory": {
                    "type": "boolean"
                }
            },
            "additionalProperties": True
        },
        "job_action_list": {
            "items": {
                "$ref": "#/definitions/job_action"
            }
        }
    },
    "properties": {
        "job_actions": {
            "$ref": "#/definitions/job_action_list"
        },
        "job_schedule": {
            "id": "job_schedule",
            "type": "object",
            "properties": schedule_properties,
            "additionalProperties": False,
        },
        "job_id": {
            "id": "job_id",
            "pattern": r"^[\w-]+$",
            "type": "string"
        },
        "client_id": {
            "id": "client_id",
            "pattern": client_id_regex,
            "type": "string"
        },
        "session_id": {
            "id": "session_id",
            "pattern": r"^[\w-]*$",
            "type": ["string", "null"]
        },
        "session_tag": {
            "id": "session_tag",
            "type": "integer"
        },
        "session_name": {
            "id": "session_name",
            "type": ["string", "null"]
        },
        "user_id": {
            "id": "user_id",
            "pattern": r"^[\w-]+$",
            "type": "string"
        },
        "project_id": {
            "id": "project_id",
            "pattern": r"^[\w-]+$",
            "type": "string"
        },
        "description": {
            "id": "description",
            "type": ["string", "null"]
        },
        "_version": {
            "id": "_version",
            "type": "integer"
        },
        "action_defaults": {
            "$ref": "#/definitions/freezer_action"
        }
    },
    "additionalProperties": False
}


additional_action_properties = {
    "action_id": {
        "id": "action_id",
        "pattern": r"^[\w-]+$",
        "type": "string"
    },
    "user_id": {
        "id": "user_id",
        "pattern": r"^[\w-]+$",
        "type": "string"
    },
    "project_id": {
        "id": "project_id",
        "pattern": r"^[\w-]+$",
        "type": "string"
    }
}


tmp_prop = freezer_action_properties.items()
tmp_add_prop = additional_action_properties.items()
joined_properties = {}
joined_properties.update(tmp_prop)
joined_properties.update(tmp_add_prop)


action_schema = {
    "id": "/",
    "type": "object",
    "properties": joined_properties,
    "additionalProperties": True,
    "required": [
        "action_id",
        "user_id",
        "freezer_action"
    ]
}

action_patch_schema = {
    "id": "/",
    "type": "object",
    "properties": joined_properties,
    "additionalProperties": True
}

session_schema = {
    "id": "/",
    "type": "object",
    "properties": {
        "schedule": {
            "id": "schedule",
            "type": "object",
            "properties": schedule_properties,
            "additionalProperties": False,
        },
        "session_id": {
            "id": "session_id",
            "pattern": r"^[\w-]+$",
            "type": "string"
        },
        "user_id": {
            "id": "user_id",
            "pattern": r"^[\w-]+$",
            "type": "string"
        },
        "project_id": {
            "id": "project_id",
            "pattern": r"^[\w-]+$",
            "type": "string"
        },
        "session_tag": {
            "id": "session_tag",
            "type": "integer"
        },
        "time_started": {
            "id": "time_started",
            "type": "integer"
        },
        "time_ended": {
            "id": "time_ended",
            "type": "integer"
        },
    },
    "additionalProperties": True,
    "required": [
        "session_id",
        "session_tag",
        "user_id",
        "schedule"
    ]
}

session_patch_schema = {
    "id": "/",
    "type": "object",
    "properties": {
        "schedule": {
            "id": "schedule",
            "type": "object",
            "properties": schedule_properties,
            "additionalProperties": False,
        },
        "session_id": {
            "id": "session_id",
            "pattern": r"^[\w-]+$",
            "type": "string"
        },
        "user_id": {
            "id": "user_id",
            "pattern": r"^[\w-]+$",
            "type": "string"
        },
        "project_id": {
            "id": "project_id",
            "pattern": r"^[\w-]+$",
            "type": "string"
        },
        "session_tag": {
            "id": "session_tag",
            "type": "integer"
        },
        "time_started": {
            "id": "time_started",
            "type": "integer"
        },
        "time_ended": {
            "id": "time_ended",
            "type": "integer"
        },
    },
    "additionalProperties": True
}

client_info = {
    "client_id": {
        "id": "client_id",
        "pattern": client_id_regex,
        "type": "string",
        "description": (
            "The client ID. Must match client ID format "
            "(e.g., ``[project_id_]hostname``)."
        )
    },
    "hostname": {
        "id": "hostname",
        "pattern": fqdn_regex,
        "type": "string",
        "description": "The hostname of the client machine."
    },
    "description": {
        "id": "description",
        "type": "string",
        "description": "A user-defined description of the resource."
    },
    "uuid": {
        "id": "uuid",
        "type": "string"
    },
    "supported_actions": {
        "id": "supported_actions",
        "type": "array",
        "items": {
            "type": "string",
            "enum": SUPPORTED_ACTIONS,
        },
        "description": "List of actions supported by this client."
    },
    "supported_modes": {
        "id": "supported_modes",
        "type": "array",
        "items": {
            "type": "string",
            "enum": SUPPORTED_MODES,
        },
        "description": "List of modes supported by this client."
    },
    "supported_storages": {
        "id": "supported_storages",
        "type": "array",
        "items": {
            "type": "string",
            "enum": SUPPORTED_STORAGES,
        },
        "description": "List of storages supported by this client."
    },
    "supported_engines": {
        "id": "supported_engines",
        "type": "array",
        "items": {
            "type": "string",
            "enum": SUPPORTED_ENGINES,
        },
        "description": "List of engines supported by this client."
    },
    "is_central": {
        "id": "is_central",
        "type": "boolean",
        "description": "Whether the client is registered as a central client."
    },
}

client_schema = {
    "id": "/",
    "type": "object",
    "properties": {
        "client": {
            "id": "client",
            "type": "object",
            "properties": client_info,
            "additionalProperties": True,
            "required": [
                "client_id"
            ]
        },
        "user_id": {
            "id": "user_id",
            "pattern": r"^[\w-]+$",
            "type": "string"
        },
        "project_id": {
            "id": "project_id",
            "pattern": r"^[\w-]+$",
            "type": "string"
        }
    },
    "additionalProperties": True,
    "required": [
        "client",
        "user_id"
    ]
}
