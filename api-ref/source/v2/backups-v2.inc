=================
Backups (backups)
=================

Backups allow users to record their backups and metadata information about
those backups and when backups were taken. It holds the backup information.


List backups(v2)
================

.. rest_method::  GET /v2/{project_id}/backups

Lists backups.

This operation lists backups for the project. The backups are sorted
alphabetically by name.

Normal response codes: 200

Error response codes:

- Unauthorized (401)
- Forbidden (403)


Query Parameters
-----------------

.. rest_parameters:: parameters.yaml

  - project_id: project_id_path

Request Parameters
-------------------

.. rest_parameters:: parameters.yaml

  - limit: limit
  - marker: marker
  - search: search_option

Response Parameters
-------------------

.. rest_parameters:: parameters.yaml

  - backups: backups


Request Example
---------------

.. literalinclude:: samples/backup-list-request.json
   :language: javascript

Response Example
----------------

.. literalinclude:: samples/backup-list-response.json
   :language: javascript


Show backups(v2)
================

.. rest_method::  GET /v2/{project_id}/backups/{backup_id}

Shows a backups.

This operation shows a certain backup. The backup details.

Normal response codes: 200

Error response codes:

- Unauthorized (401)
- Forbidden (403)


Query Parameters
-----------------

.. rest_parameters:: parameters.yaml

  - project_id: project_id_path
  - backup_id: backup_id_path

Response Parameters
-------------------

.. rest_parameters:: parameters.yaml

  - project_id: project_id
  - user_id: user_id
  - backup_id: backup_id
  - username: username
  - backup_metadata: backup_metadata


Response Example
----------------

.. literalinclude:: samples/backup-get-response.json
   :language: javascript


Delete backups(v2)
==================

.. rest_method::  DELETE /v2/{project_id}/actions/{backup_id}

Delete backups in a project.

This operation deletes a certain backup.

Normal response codes: 204

Error response codes:

- Unauthorized (401)
- Forbidden (403)

Query Parameters
-----------------

.. rest_parameters:: parameters.yaml

  - project_id: project_id_path
  - backup_id: backup_id_path

There is no response for this operation.
