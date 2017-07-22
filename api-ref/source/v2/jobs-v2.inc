===========
Jobs (jobs)
===========

Jobs allow users to schedule and execute backup jobs on one node or more. Jobs
are stored through the api in the database. Every job contains set of actions
that carry out the backup job.

List jobs
=========

.. rest_method::  GET /v2/{project_id}/jobs

Lists jobs v2.

This operation lists jobs for the project. The jobs are sorted alphabetically
 by name.

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

  - jobs: jobs


Response Example
----------------

.. literalinclude:: samples/jobs-list-response.json
   :language: javascript


Create job
==========

.. rest_method:: POST /v2/{project_id}/jobs

Creates a job v2.

This operation creates a new job.

The ``body`` attribute specifies contains a set of actions that gets created
 one the job is submitted.

``description`` is the name that you give to the job. The name must not
exceed 64 bytes in length.

The ``job_schedule`` is very important to schedule the job or it will run only
once. also you can provide ``event`` which can automatically start/stop the
job.

The ``job_actions`` the actual backup or restore action to be done.

Normal response codes: 201

Error response codes:

- BadRequest (400)
- Unauthorized (401)
- ServiceUnavailable (503)


Request Parameters
------------------

.. rest_parameters:: parameters.yaml

  - description: job_description_req
  - job_schedule: job_schedule_req
  - job_actions: job_actions_req
  - project_id: project_id_path

Request Example
---------------

.. literalinclude:: samples/job-create-request.json
   :language: javascript


This operation does not return a response body.
