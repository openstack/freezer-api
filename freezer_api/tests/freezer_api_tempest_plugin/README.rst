==================================
Tempest Integration of Freezer API
==================================

This directory contains Tempest tests to cover the freezer-api project.

Instructions for Running/Developing Tempest Tests with Freezer API Project

#. Make sure there is Devstack or other environment for running Keystone and Elasticsearch.

#. Clone the Tempest Repo::

    run 'git clone https://github.com/openstack/tempest.git'

#. Create a virtual environment for Tempest. In these instructions, the Tempest virtual environment is ``~/virtualenvs/tempest-freezer-api``.

#. Activate the Tempest virtual environment::

    run 'source ~/virtualenvs/tempest-freezer-api/bin/activate'

#. Make sure you have the latest pip installed in the virtual environment::

    run 'pip install --upgrade pip'

#. Install Tempest requirements.txt and test-requirements.txt in the Tempest virtual environment::

    run 'pip install -r requirements.txt -r test-requirements.txt'

#. Install Tempest project into the virtual environment in develop mode::

    run ‘python setup.py develop’

#. Create logging.conf in Tempest Repo home dir/etc

    Make a copy of logging.conf.sample as logging.conf

    In logging configuration

    You will see this error on Mac OS X

    socket.error: [Errno 2] No such file or directory

    To fix this, edit logging.conf

    Change ‘/dev/log/ to '/var/run/syslog’ in logging.conf

    see: https://github.com/baremetal/python-backoff/issues/1 for details

#. Create tempest.conf in Tempest Repo home dir/etc::

    run 'oslo-config-generator --config-file etc/config-generator.tempest.conf --output-file etc/tempest.conf'

    Add the following sections to tempest.conf and modify uri and uri_v3 to point to the host where Keystone is running::

    [identity]

    username = freezer
    password = secretservice
    tenant_name = service
    domain_name = default
    admin_username = admin
    admin_password = secretadmin
    admin_domain_name = default
    admin_tenant_name = admin
    alt_username = admin
    alt_password = secretadmin
    alt_tenant_name = admin
    use_ssl = False
    auth_version = v3
    uri = http://10.10.10.6:5000/v2.0/
    uri_v3 = http://10.10.10.6:35357/v3/

    [auth]

    allow_tenant_isolation = true
    tempest_roles = admin


#. Clone freezer-api Repo::

    run 'git clone https://github.com/openstack/freezer-api.git'

#. Set the virtual environment for the freezer-api to the Tempest virtual environment::

    run 'source ~/virtualenvs/tempest-freezer-api/bin/activate'

#. pip install freezer-api requirements.txt and test-requirements.txt in the Tempest virtual environment::

    run 'pip install -r requirements.txt -r test-requirements.txt'

#. Install nose in the Tempest virtual environment::

    run 'pip install nose'

#. Install the freezer-api project into the Tempest virtual environment in develop mode::

    run ‘python setup.py develop’

#. Setup the freezer-api.conf and freezer-paste.ini files according to the main freezer-api README.rst

#. Set the freezer-api project interpreter (pycharm) to the Tempest virtual environment.

#. Create a test config (pycharm) using the Tempest virtual environment as python interpreter.

#. Run the tests in the api directory in the freezer_api_tempest_plugin directory.
