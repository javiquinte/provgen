.. provgen documentation master file, created by
   sphinx-quickstart on Mon Jul  3 10:39:39 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to provgen's documentation!
===================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

B2SAFE functions
================

* EUDATiCHECKSUMretrieve(*path, *checksum, *modtime)
Set the checksum if needed and update the timestamp of the modification also. Three things are available: the full path of the file, the final checksum and the modification time of the checksum. We also know if the checksum has been updated or just read. The latter should not produce any provenance information.

* EUDATReplication(*source, *destination, *registered, *recursive, *response)
Replicate the source to the destination. The parameter registered determines whether the file has a PID which needs to be updated or not. Variable response contains a string with the result of the operation.

* EUDATPIDRegistration(*source, *destination, *notification, *registration_response)
Verify that a PID exist for a given path and optionally create it if not found.

* EUDATCreatePID(*parent_pid, *path, *ror, *fio, *fixed, *newPID)
parent_pid is the PID of the digital object that was replicated to us (not necessarily the ROR); path is the path of the object to store with the PID record; ror is the ROR PID of the digital object that we want to store; fio is the FIO PID of the digital object that we want to store; fixed is a boolean flag to define that the object related to this PID cannot change; and newPID is the pid generated for this object.

* Do we also want to catch the errors in data transfer and checksum calculation?

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
