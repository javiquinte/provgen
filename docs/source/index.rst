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
Set the checksum if needed and update the timestamp also.

* EUDATrp_transferInitiated( *source )
Set the initiation of transfer.

* EUDATrp_transferFinished( *source )
Set the finalization of a transfer.

* EUDATrp_ingestObject
From the higher view perspective the EUDATrp_ingestObject function is driving
the archival process of data. ::

    # Manage the ingestion in B2SAFE
    # Check the checksum
    # Create PID
    #
    # Parameters:
    # *source [IN] target object to assign a PID
    #
    # Author: Stephane Coutin (CINES)
    # updated : Stéphane Coutin (CINES)
    # 23/10/14 (use EUDATiCHECKSUMget to avoid duplicate checksum calculation)
    #-----------------------------------------------------------------------------
    EUDATrp_ingestObject( *source )
    {
        rp_getRpIngestParameters(*protectArchive, *archiveOwner);
        logInfo("ingestObject-> Check for (*source)");
        EUDATiCHECKSUMget(*source, *checksum, *modtime);
        EUDATCreateAVU("INFO_Checksum", *checksum, *source);
    # Modified begin
        EUDATgetLastAVU(*source, "OTHER_original_checksum", *orig_checksum);
    # Modified end
        if ( *checksum == *orig_checksum )
        {
            logInfo("ingestObject-> Checksum is same as original = *checksum");
            EUDATCreateAVU("ADMIN_Status", "Checksum_ok", *source);
    	EUDATgetLastAVU( *source, "EUDAT/ROR" , *RorValue );
            EUDATCreatePID("None", *source, *RorValue, "None", "false", *PID);
            # test PID creation
            if((*PID == "empty") || (*PID == "None") || (*PID == "error")) {
                logInfo("ingestObject-> ERROR while creating the PID for *source PID = *PID");
                EUDATCreateAVU("ADMIN_Status", "ErrorPID", *source);
            }
            else {
                logInfo("ingestObject-> PID created for *source PID = [*PID] ROR = [*RorValue]");
                EUDATCreateAVU("ADMIN_Status", "Archive_ok", *source);
                if (*protectArchive) {
                    logInfo("ingestObject-> changing *source owner to = *archiveOwner with read access to$userNameClient");
                    msiSetACL("default","read",$userNameClient,*source);
                    msiSetACL("default","own",*archiveOwner,*source);
                }
            }
        }
        else
        {
            logInfo("ingestObject-> Checksum (*checksum) is different than original (*orig_checksum)");
            EUDATCreateAVU("ADMIN_Status", "ErrorChecksum", *source);
        }
    }

* Do we also want to catch the errors in data transfer and checksum calculation?

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
