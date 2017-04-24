=================
Backups (backups)
=================

Backups allow users to record their backups and metadata information about
those backups and when backups were taken. It holds the backup information.

List backups
============

.. rest_method::  GET /v2/{project_id}/backups

Lists backups.

This operation lists backups for the project. The backups are sorted
alphabetically by name.

Normal response codes: 200

Error response codes:

- Unauthorized (401)
- Forbidden (403)

Request Parameters
------------------

.. rest_parameters:: parameters.yaml

  - project_id: project_id_path

Query Parameters
-----------------

.. rest_parameters:: parameters.yaml

  - limit: limit
  - marker: marker

Response Parameters
-------------------

.. rest_parameters:: parameters.yaml

  - backups: backups


Response Example
----------------

.. literalinclude:: samples/backup-list-response.json
   :language: javascript

