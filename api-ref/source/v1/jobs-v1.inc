=================
Jobs (jobs)
=================

Jobs allow users to schedule and execute backup jobs on one node or more. Jobs
 are stored through the api in the database. Every job contains set of actions
  that carry out the backup job.

Lists jobs
==========

.. rest_method::  GET /v1/jobs

Lists jobs.

This operation lists jobs for the project.

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

  - jobs: jobs


Response Example
----------------

.. literalinclude:: samples/jobs-list-response.json
   :language: javascript


Creates job
===========

.. rest_method:: POST /v1/jobs

Creates a job.

This operation creates a new job.

The ``body`` attribute specifies contains a set of actions that gets created
 one the job is submitted.

The ``description`` is the name that you give to the job. The name must not
exceed 64 bytes in length.

The ``job_schedule`` is very important to schedule the job or it will run only
once. also you can provide ``event`` which can automatically start/stop the
job.

The ``job_actions`` the actual backup or restore action to be done.

Normal response codes: 201

Error response codes:

- Syntax Error (753)
- BadRequest (400)
- Unauthorized (401)
- ServiceUnavailable (503)


Request Parameters
------------------

.. rest_parameters:: parameters.yaml

  - description: job_description_req
  - job_schedule: job_schedule_req
  - job_actions: job_actions_req

Request Example
---------------

.. literalinclude:: samples/job-create-request.json
   :language: javascript


This operation does not return a response body.


Show jobs
=========

.. rest_method::  GET /v1/jobs/{job_id}

Shows jobs.

This operation shows a certain job. It displays all job details with actions
inside the job.



Normal response codes: 200

Error response codes:

- Unauthorized (401)
- Forbidden (403)

Query Parameters
-----------------

.. rest_parameters:: parameters.yaml

  - job_id: job_id_path

Response Parameters
-------------------

.. rest_parameters:: parameters.yaml

  - user_id: user_id
  - description: job_description_req
  - job_schedule: job_schedule_req
  - client_id: client_id
  - job_actions: job_actions_req
  - job_id: job_id

Response Example
----------------

.. literalinclude:: samples/job-get-response.json
   :language: javascript


Updates jobs
============

.. rest_method:: PATCH /v1/jobs/{job_id}

Updates a job.

This operation creates a new job.

The ``body`` attribute specifies contains a set of actions that gets updated
 once the job is submitted.

The ``description`` is the name that you give to the job. The name should not
exceed 64 bytes in length.

The ``job_schedule`` is very important to schedule the job or it will run only
once. also you can provide ``event`` which can automatically start/stop the
job.

The ``job_actions`` the actual backup or restore action to be done.

Normal response codes: 201

Error response codes:

- Syntax Error (753)
- BadRequest (400)
- Unauthorized (401)
- ServiceUnavailable (503)


Query Parameters
-----------------

.. rest_parameters:: parameters.yaml

  - job_id: job_id_path

Request Parameters
------------------

.. rest_parameters:: parameters.yaml

  - description: job_description_req
  - job_schedule: job_schedule_req
  - job_actions: job_actions_req

Request Example
---------------

.. literalinclude:: samples/job-update-request.json
   :language: javascript

Response Example
----------------

.. literalinclude:: samples/job-update-response.json
   :language: javascript


Delete jobs
===========

.. rest_method::  DELETE /v1/jobs/{job_id}

Delete jobs.

This operation deletes a certain job .

Normal response codes: 204

Error response codes:

- Unauthorized (401)
- Forbidden (403)

Query Parameters
-----------------

.. rest_parameters:: parameters.yaml

  - job_id: job_id_path

There is no response for this operation.