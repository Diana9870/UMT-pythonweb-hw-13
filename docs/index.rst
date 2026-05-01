Contacts API Documentation
=========================

Welcome to the **Contacts API** documentation.

This project is a FastAPI-based application that provides:

- JWT Authentication
- Contacts management (CRUD)
- Redis caching
- Role-based access control
- Docker support
- Pytest testing

--------------------------------------------------

Quick Start
-----------

Run the project using Docker:

.. code-block:: bash

   docker-compose up --build

Open API docs:

- http://localhost:8000/docs

--------------------------------------------------

Project Structure
-----------------

.. code-block:: text

   app/
     ├── routes/
     ├── services/
     ├── repository/
     ├── models.py
     ├── schemas.py
     ├── main.py

--------------------------------------------------

API Modules
-----------

Auth
~~~~

.. automodule:: app.routes.auth
   :members:
   :undoc-members:
   :show-inheritance:

Users
~~~~~

.. automodule:: app.routes.users
   :members:
   :undoc-members:
   :show-inheritance:

Contacts
~~~~~~~~

.. automodule:: app.routes.contacts
   :members:
   :undoc-members:
   :show-inheritance:

--------------------------------------------------

Services
--------

Auth Service
~~~~~~~~~~~~

.. automodule:: app.services.auth
   :members:
   :undoc-members:
   :show-inheritance:

Redis Cache
~~~~~~~~~~~

.. automodule:: app.services.redis_cache
   :members:
   :undoc-members:
   :show-inheritance:

--------------------------------------------------

Repository Layer
----------------

Users Repository
~~~~~~~~~~~~~~~~

.. automodule:: app.repository.users
   :members:
   :undoc-members:
   :show-inheritance:

Contacts Repository
~~~~~~~~~~~~~~~~~~~

.. automodule:: app.repository.contacts
   :members:
   :undoc-members:
   :show-inheritance:

--------------------------------------------------

Models
------

.. automodule:: app.models
   :members:
   :undoc-members:
   :show-inheritance:

--------------------------------------------------

Schemas
-------

.. automodule:: app.schemas
   :members:
   :undoc-members:
   :show-inheritance:

--------------------------------------------------

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`