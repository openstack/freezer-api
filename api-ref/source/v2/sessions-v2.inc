===================
Sessions (sessions)
===================

A session is a group of jobs which share the same scheduling time. A session
is identified by its ``session_id`` and has a numeric tag (session_tag) which
is incremented each time that a new session is started. The purpose of the
``session_tag`` is that of identifying a group of jobs which have been
executed together and which therefore represent a snapshot of a distributed
system.

When a ``job`` is added to a session, the scheduling time of the session is
copied into the job data structure, so that any job belonging to the same
session will start at the same time.

Lists Sessions(v2)
==================

.. rest_method::  GET /v2/{project_id}/sessions

Lists sessions.

This operation lists sessions in a project.

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

Response Parameters
-------------------

.. rest_parameters:: parameters.yaml

  - sessions: sessions


Response Example
----------------

.. literalinclude:: samples/sessions-list-response.json
   :language: javascript


Creates session(v2)
===================

.. rest_method:: POST /v2/{project_id}/sessions

Creates a session.

This operation creates a new session in a project.

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

Request Parameters
------------------

.. rest_parameters:: parameters.yaml

  - description: session_description
  - hold_off: session_hold_off
  - session_tag: session_tag
  - schedule: session_schedule
  - schedule_internval: session_schedule_internval
  - event: session_event

Request Example
---------------

.. literalinclude:: samples/sessions-create-request.json
   :language: javascript

Response Parameters
-------------------

.. rest_parameters:: parameters.yaml

  - session_id: session_id

Response Example
----------------

.. literalinclude:: samples/sessions-create-response.json
   :language: javascript


Show sessions(v2)
=================

.. rest_method::  GET /v2/{project_id}/sessions/{session_id}

Shows sessions.

This operation shows a certain session in a project. It displays 
all session details with jobs included in this session.

Normal response codes: 200

Error response codes:

- Unauthorized (401)
- Forbidden (403)

Query Parameters
-----------------

.. rest_parameters:: parameters.yaml

  - project_id: project_id_path
  - session_id: session_id_path

Response Parameters
-------------------

.. rest_parameters:: parameters.yaml

  - user_id: user_id
  - description: session_description
  - schedule: session_schedule
  - session_tag: session_tag
  - session_id: session_id
  - hold_off: session_hold_off

Response Example
----------------

.. literalinclude:: samples/sessions-get-response.json
   :language: javascript

.. literalinclude:: samples/sessions-get-with-job-response.json
   :language: javascript



Updates a session(v2)
=====================

.. rest_method:: PATCH /v2/{project_id}/sessions

Updates a session.

This operation updates a new session in a project.

Normal response codes: 200

Error response codes:

- Syntax Error (753)
- BadRequest (400)
- Unauthorized (401)
- ServiceUnavailable (503)

Query Parameters
-----------------

.. rest_parameters:: parameters.yaml

  - project_id: project_id_path

Request Parameters
------------------

.. rest_parameters:: parameters.yaml

  - description: session_description
  - hold_off: session_hold_off
  - session_tag: session_tag
  - schedule: session_schedule
  - schedule_internval: session_schedule_internval
  - event: session_event
  - session_id: session_id_path

Request Example
---------------

.. literalinclude:: samples/sessions-update-request.json
   :language: javascript

Response Parameters
-------------------

.. rest_parameters:: parameters.yaml

  - session_id: session_id
  - version: version_doc

Response Example
----------------

.. literalinclude:: samples/sessions-update-response.json
   :language: javascript


Add jobs(v2)
============

.. rest_method::  PUT /v2/{project_id}/sessions/{session_id}/jobs/{job_id}

attaches job to a session.

This operation adds a certain job to a session. The api will load the job
and the session and add the job to session document.

Normal response codes: 204

Error response codes:

- Unauthorized (401)
- Forbidden (403)

Query Parameters
-----------------

.. rest_parameters:: parameters.yaml

  - project_id: project_id_path
  - session_id: session_id_path
  - job_id: job_id_path

No response will be returned for this job.


Remove jobs(v2)
===============

.. rest_method::  DELETE /v2/{project_id}/sessions/{session_id}/jobs/{job_id}

Removes a job from a session.

This operation will remove a certain job to a session in a project.

Normal response codes: 204

Error response codes:

- Unauthorized (401)
- Forbidden (403)

Query Parameters
-----------------

.. rest_parameters:: parameters.yaml

  - project_id: project_id_path
  - session_id: session_id_path
  - job_id: job_id_path

No response will be returned for this job.


Start sessions(v2)
==================

.. rest_method::  POST /v2/{project_id}/sessions/{session_id}/actions

Removes a job from a session.

This operation will remove a certain job to a session in a project.

Normal response codes: 202

Error response codes:

- Unauthorized (401)
- Forbidden (403)

Query Parameters
-----------------

.. rest_parameters:: parameters.yaml

  - project_id: project_id_path
  - session_id: session_id_path

Response Parameters
-------------------

.. rest_parameters:: parameters.yaml

  - result: result
  - session_tag: session_tag

Response Example
----------------

.. literalinclude:: samples/session-start-response.json
   :language: javascript


Remove  sessions(v2)
====================

.. rest_method::  DELETE /v2/{project_id}/sessions/{session_id}

Removes a session.

This operation will remove a certain a session in a project.

Normal response codes: 204

Error response codes:

- Unauthorized (401)
- Forbidden (403)

Query Parameters
-----------------

.. rest_parameters:: parameters.yaml

  - project_id: project_id_path
  - session_id: session_id_path

No response will be returned for this job.
