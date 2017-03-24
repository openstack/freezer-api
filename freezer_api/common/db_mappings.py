"""
Copyright 2015 Hewlett-Packard
(c) Copyright 2016 Hewlett Packard Enterprise Development Company LP

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


clients_mapping = {
    "properties": {
        "client": {
            "properties": {
                "client_id": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "config_id": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "description": {
                    "type": "string"
                },
                "hostname": {
                    "type": "string"
                }
            }
        },
        "user_id": {
            "index": "not_analyzed",
            "type": "string"
        },
        "project_id": {
            "index": "not_analyzed",
            "type": "string"
        },
        "uuid": {
            "index": "not_analyzed",
            "type": "string"
        }
    }
}

backups_mapping = {
    "properties": {
        "backup_id": {
            "index": "not_analyzed",
            "type": "string"
        },
        "backup_metadata": {
            "properties": {
                "action": {
                    "type": "string"
                },
                "always_level": {
                    "type": "boolean"
                },
                "backup_media": {
                    "type": "string"
                },
                "backup_name": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "backup_session": {
                    "type": "long"
                },
                "backup_size_compressed": {
                    "type": "long"
                },
                "backup_size_uncompressed": {
                    "type": "long"
                },
                "broken_links": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "cli": {
                    "type": "string"
                },
                "client_os": {
                    "type": "string"
                },
                "client_version": {
                    "type": "string"
                },
                "compression": {
                    "type": "string"
                },
                "log_file": {
                    "type": "string"
                },
                "proxy": {
                    "type": "string"
                },
                "ssh_key": {
                    "type": "string"
                },
                "ssh_username": {
                    "type": "string"
                },
                "ssh_host": {
                    "type": "string"
                },
                "ssh_port": {
                    "type": "long"
                },
                "storage": {
                    "type": "string"
                },
                "compression_alg": {
                    "type": "string"
                },
                "container": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "container_segments": {
                    "type": "string"
                },
                "curr_backup_level": {
                    "type": "string"
                },
                "current_level": {
                    "type": "string"
                },
                "dry_run": {
                    "type": "boolean"
                },
                "encrypted": {
                    "type": "boolean"
                },
                "excluded_files": {
                    "type": "string"
                },
                "fs_real_path": {
                    "type": "string"
                },
                "host_name": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "hostname": {
                    "type": "string"
                },
                "level": {
                    "type": "long"
                },
                "max_level": {
                    "type": "long"
                },
                "meta_data_file": {
                    "type": "string"
                },
                "mode": {
                    "type": "string"
                },
                "no_incremental": {
                    "type": "boolean"
                },
                "overwrite": {
                    "type": "boolean"
                },
                "path_to_backup": {
                    "type": "string"
                },
                "time_stamp": {
                    "type": "string"
                },
                "timestamp": {
                    "type": "long"
                },
                "total_backup_session_size": {
                    "type": "long"
                },
                "total_broken_links": {
                    "type": "long"
                },
                "total_directories": {
                    "type": "long"
                },
                "total_fs_files": {
                    "type": "long"
                },
                "version": {
                    "type": "string"
                },
                "vol_snap_path": {
                    "type": "string"
                },
                "os_auth_version": {
                    "type": "string"
                },
                "consistency_checksum": {
                    "type": "string"
                }
            }
        },
        "user_id": {
            "index": "not_analyzed",
            "type": "string"
        },
        "user_name": {
            "type": "string"
        },
        "client_id": {
            "index": "not_analyzed",
            "type": "string"
        },
        "job_id": {
            "index": "not_analyzed",
            "type": "string"
        },
        "project_id": {
            "index": "not_analyzed",
            "type": "string"
        }
    }
}

jobs_mapping = {
    "properties": {
        "client_id": {
            "index": "not_analyzed",
            "type": "string"
        },
        "description": {
            "type": "string"
        },
        "job_actions": {
            "properties": {
                "action_id": {
                    "type": "string"
                },
                "user_id": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "project_id": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "freezer_action": {
                    "properties": {
                        "action": {
                            "type": "string"
                        },
                        "backup_name": {
                            "type": "string"
                        },
                        "container": {
                            "type": "string"
                        },
                        "hostname": {
                            "type": "string"
                        },
                        "snapshot": {
                            "type": "boolean"
                        },
                        "storage": {
                            "type": "string"
                        },
                        "dry_run": {
                            "type": "boolean"
                        },
                        "log_file": {
                            "type": "string"
                        },
                        "lvm_auto_snap": {
                            "type": "string"
                        },
                        "lvm_dirmount": {
                            "type": "string"
                        },
                        "lvm_snapname": {
                            "type": "string"
                        },
                        "lvm_snapsize": {
                            "type": "string"
                        },
                        "max_level": {
                            "type": "long"
                        },
                        "max_priority": {
                            "type": "boolean"
                        },
                        "max_segment_size": {
                            "type": "long"
                        },
                        "mode": {
                            "type": "string"
                        },
                        "mysql_conf": {
                            "type": "string"
                        },
                        "path_to_backup": {
                            "type": "string"
                        },
                        "remove_older_than": {
                            "type": "long"
                        },
                        "remove_older_then": {
                            "type": "long"
                        },
                        "restore_abs_path": {
                            "type": "string"
                        },
                        "restore_from_host": {
                            "type": "string"
                        },
                        "ssh_host": {
                            "type": "string"
                        },
                        "ssh_port": {
                            "type": "long"
                        },
                        "ssh_key": {
                            "index": "not_analyzed",
                            "type": "string"
                        },
                        "ssh_username": {
                            "type": "string"
                        },
                        "proxy": {
                            "type": "string"
                        },
                        "no_incremental": {
                            "type": "boolean"
                        },
                        "overwrite": {
                            "type": "boolean"
                        }
                    }
                },
                "mandatory": {
                    "type": "boolean"
                },
                "max_retries": {
                    "type": "long"
                },
                "max_retries_interval": {
                    "type": "long"
                }
            }
        },
        "job_event": {
            "type": "string"
        },
        "job_id": {
            "index": "not_analyzed",
            "type": "string"
        },
        "job_schedule": {
            "properties": {
                "event": {
                    "type": "string"
                },
                "result": {
                    "type": "string"
                },
                "schedule_day_of_week": {
                    "type": "string"
                },
                "schedule_hour": {
                    "type": "string"
                },
                "schedule_interval": {
                    "type": "string"
                },
                "schedule_minute": {
                    "type": "string"
                },
                "schedule_start_date": {
                    "format": "dateOptionalTime",
                    "type": "date"
                },
                "status": {
                    "type": "string"
                },
                "time_created": {
                    "type": "long"
                },
                "time_ended": {
                    "type": "long"
                },
                "time_started": {
                    "type": "long"
                },
                "current_pid": {
                    "type": "long"
                }
            }
        },
        "session_id": {
            "type": "string",
            "index": "not_analyzed"
        },
        "session_tag": {
            "type": "long"
        },
        "user_id": {
            "index": "not_analyzed",
            "type": "string"
        },
        "project_id": {
            "index": "not_analyzed",
            "type": "string"
        }
    }
}


def get_mappings():
    return {
        "jobs": jobs_mapping,
        "backups": backups_mapping,
        "clients": clients_mapping
    }
