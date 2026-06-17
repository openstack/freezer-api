=================
Clients (clients)
=================

Clients allow freezer schedulers or users to create a client to be able to
create, update, show or delete job. The client is required to record you
backups on freezer api.


Lists clients(v2)
=================

.. rest_method::  GET /v2/{project_id}/clients

Lists clients.

This operation lists clients.

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
  - offset: marker
  - search: search_option

Response Parameters
-------------------

.. rest_parameters:: parameters.yaml

  - clients: clients


Request Example
---------------

.. literalinclude:: samples/clients-list-request.json
   :language: javascript

Response Example
----------------

.. literalinclude:: samples/clients-list-response.json
   :language: javascript


Creates Client(v2)
==================

.. rest_method:: POST /v2/{project_id}/clients

Creates a client.

This operation creates a new client.

Normal response codes: 201

Error response codes:

- Syntax Error (753)
- BadRequest (400)
- Unauthorized (401)
- ServiceUnavailable (503)


Query Parameters
------------------

.. rest_parameters:: parameters.yaml

  - project_id: project_id_path

Request Parameters
-------------------

.. rest_parameters:: parameters.yaml

  - client: client
  - client.client_id: client.client_id
  - client.hostname: client.hostname
  - client.description: client.description
  - client.uuid: client.uuid
  - client.supported_actions: client.supported_actions
  - client.supported_modes: client.supported_modes
  - client.supported_storages: client.supported_storages
  - client.supported_engines: client.supported_engines
  - client.is_central: client.is_central

Request Example
---------------

.. literalinclude:: samples/clients-create-request.json
   :language: javascript

Response Parameters
-------------------

.. rest_parameters:: parameters.yaml

  - client_id: client_id


Response Example
----------------

.. literalinclude:: samples/clients-create-response.json
   :language: javascript


Show clients(v2)
================

.. rest_method::  GET /v2/{project_id}/clients/{client_id}

Show clients.

This operation shows a certain client . It displays all client details.

Normal response codes: 200

Error response codes:

- Unauthorized (401)
- Forbidden (403)

Query Parameters
-----------------

.. rest_parameters:: parameters.yaml

  - project_id: project_id_path
  - client_id: client_id_path

Response Parameters
-------------------

.. rest_parameters:: parameters.yaml

  - project_id: project_id
  - user_id: user_id
  - client: client
  - client.client_id: client.client_id
  - client.hostname: client.hostname
  - client.description: client.description
  - client.uuid: client.uuid
  - client.supported_actions: client.supported_actions
  - client.supported_modes: client.supported_modes
  - client.supported_storages: client.supported_storages
  - client.supported_engines: client.supported_engines
  - client.is_central: client.is_central


Response Example
----------------

.. literalinclude:: samples/client-get-response.json
   :language: javascript


Delete clients(v2)
==================

.. rest_method::  DELETE /v2/{project_id}/clients/{client_id}

Delete clients.

This operation deletes a certain client.

Normal response codes: 204

Error response codes:

- Unauthorized (401)
- Forbidden (403)

Query Parameters
-----------------

.. rest_parameters:: parameters.yaml

  - project_id: project_id_path
  - client_id: client_id_path

There is no response for this operation.
