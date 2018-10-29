=================
Actions (actions)
=================

Actions allow users to execute backups and restore operations on one node
or more. Actions are stored through the api in the database. It is included
in the job, every job contains set of actions that carry out the backup/restore
job.


Lists Actions(v2)
=================

.. rest_method::  GET /v2/{project_id}/actions

Lists actions.

This operation lists actions in a project.

Normal response codes: 200

Error response codes:

- Unauthorized (401)
- Forbidden (403)

Query Parameters
------------------

.. rest_parameters:: parameters.yaml

  - project_id: project_id_path

Request Parameters
-------------------

.. rest_parameters:: parameters.yaml

  - limit: limit
  - offset: marker

Response Parameters
-------------------

.. rest_parameters:: parameters.yaml

  - actions: actions


Response Example
----------------

.. literalinclude:: samples/actions-list-response.json
   :language: javascript


Creates action(v2)
==================

.. rest_method:: POST /v2/{project_id}/actions

Creates an action.

This operation creates a new action in a project.

The ``body`` attribute specifies contains a set of actions that gets created
 one the job is submitted.

The ``description`` is the name that you give to the job. The name must not
exceed 64 bytes in length.

The ``job_schedule`` is very important to schedule the job or it will run only
once. also you can provide ``event`` which can automatically start/stop the
job.

The ``freezer_action`` holds the actual action parameters. ``freezer_action``
differs from action to another as it depends what this action is doing (backup,
restore, admin, info)

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

  - freezer_action: freezer_action
  - max_retries: max_retries
  - max_retries_interval: max_retries_interval

Request Example
---------------

.. literalinclude:: samples/actions-create-request.json
   :language: javascript

Response Parameters
-------------------

.. rest_parameters:: parameters.yaml

  - action_id: action_id


Response Example
----------------

.. literalinclude:: samples/actions-create-response.json
   :language: javascript


Show actions(v2)
================

.. rest_method::  GET /v2/{project_id}/actions/{action_id}

Shows a action in a project.

This operation shows a certain action. The action details.

Normal response codes: 200

Error response codes:

- Unauthorized (401)
- Forbidden (403)

Query Parameters
-----------------

.. rest_parameters:: parameters.yaml

  - project_id: project_id_path
  - action_id: action_id_path

Response Parameters
-------------------

.. rest_parameters:: parameters.yaml

  - freezer_action: freezer_action
  - max_retries: max_retries
  - max_retries_interval: max_retries_interval
  - user_id: user_id
  - project_id: project_id
  - action_id: action_id

Response Example
----------------

.. literalinclude:: samples/actions-get-response.json
   :language: javascript


Updates actions(v2)
===================

.. rest_method:: POST /v2/{project_id}/actions/{action_id}

Updates an action in a project.

This operation updates or replaces an existing action.

Normal response codes: 201

Error response codes:

- Syntax Error (753)
- BadRequest (400)
- Unauthorized (401)
- ServiceUnavailable (503)


Query Parameters
-----------------

.. rest_parameters:: parameters.yaml

  - project_id: project_id_path
  - action_id: action_id_path

Response Parameters
--------------------

.. rest_parameters:: parameters.yaml

  - freezer_action: freezer_action
  - max_retries: max_retries
  - max_retries_interval: max_retries_interval
  - action_id: action_id


Request Example
---------------

.. literalinclude:: samples/actions-update-request.json
   :language: javascript

Response Example
----------------

.. literalinclude:: samples/actions-update-response.json
   :language: javascript


Delete actions(v2)
==================

.. rest_method::  DELETE /v2/{project_id}/actions/{action_id}

Delete actions in a project.

This operation deletes a certain action.

Normal response codes: 204

Error response codes:

- Unauthorized (401)
- Forbidden (403)

Query Parameters
-----------------

.. rest_parameters:: parameters.yaml

  - project_id: project_id_path
  - action_id: action_id_path

There is no response for this operation.