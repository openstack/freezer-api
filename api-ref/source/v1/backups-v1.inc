=================
Backups (backups)
=================

Backups allow users to record their backups and metadata information about
those backups and when backups were taken. It holds the backup information.

Lists backups
=============

.. rest_method::  GET /v1/backups

Lists backups.

This operation lists backups for the project.

Normal response codes: 200

Error response codes:

- Unauthorized (401)
- Forbidden (403)

Query Parameters
-----------------

.. rest_parameters:: parameters.yaml

  - limit: limit
  - offset: marker

Response Parameters
-------------------

.. rest_parameters:: parameters.yaml

  - backups: backups


Response Example
----------------

.. literalinclude:: samples/backup-list-response.json
   :language: javascript


Show backups
============

.. rest_method::  GET /v1/backups/{backup_id}

Show backups.

This operation shows a certain backup . It displays all backup details.

Normal response codes: 200

Error response codes:

- Unauthorized (401)
- Forbidden (403)

Query Parameters
-----------------

.. rest_parameters:: parameters.yaml

  - backup_id: backup_id_path

Response Parameters
-------------------

.. rest_parameters:: parameters.yaml

  - user_id: user_id
  - backup_id: backup_id
  - user_name: username
  - backup_metadata: backup_metadata


Response Example
----------------

.. literalinclude:: samples/backup-get-response.json
   :language: javascript


Delete backups
==============

.. rest_method::  DELETE /v1/backups/{backup_id}

Delete backups.

This operation deletes a certain backup .

Normal response codes: 204

Error response codes:

- Unauthorized (401)
- Forbidden (403)

Query Parameters
-----------------

.. rest_parameters:: parameters.yaml

  - backup_id: backup_id_path

There is no response for this operation.
