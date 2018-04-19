.. provgen documentation master file, created by
   sphinx-quickstart on Mon Jul  3 10:39:39 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to provgen's documentation!
===================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Installation
============

The code is hosted in the following repository: https://github.com/javiquinte/provgen.git

To get the code and deploy it you can execute the following commands: ::

  git clone https://github.com/javiquinte/provgen.git
  cd provgen
  cp provgen.cfg.sample provgen.cfg

In order to run `Provgen` you will need a recent version of python3 and the cherrypy package.
The latter can be easily installed with pip. ::

  pip3 cherrypy

Using Apache to proxy the requests
==================================

blah, blah...

Starting the service
====================

Once the application has been deployed it can be started by means of the following command: ::

  cherryd -d -i provgen


B2SAFE functions
================

The following B2SAFE functions could be modified to collect and store Provenance information.

EUDATiCHECKSUMretrieve
--------------------------

EUDATiCHECKSUMretrieve(path, checksum, modtime): 
Set the checksum if needed and update the timestamp of the modification also. Three things are available: the full path of the file, the final checksum and the modification time of the checksum. We also know if the checksum has been updated or just read. The latter should not produce any provenance information.

EUDATReplication
----------------
EUDATReplication(source, destination, registered, recursive, response): 
Replicate the source to the destination. The parameter registered determines whether the file has a PID which needs to be updated or not. Variable response contains a string with the result of the operation.

EUDATPIDRegistration
--------------------
EUDATPIDRegistration(source, destination, notification, registration_response): 
Verify that a PID exist for a given path and optionally create it if not found.

EUDATCreatePID
--------------
EUDATCreatePID(parent_pid, path, ror, fio, fixed, newPID): 
parent_pid is the PID of the digital object that was replicated to us (not necessarily the ROR); path is the path of the object to store with the PID record; ror is the ROR PID of the digital object that we want to store; fio is the FIO PID of the digital object that we want to store; fixed is a boolean flag to define that the object related to this PID cannot change; and newPID is the pid generated for this object.

1. Do we also want to catch the errors in data transfer and checksum calculation?

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
