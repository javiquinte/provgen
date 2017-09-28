#!/usr/bin/env python
#
# Provgen WS - prototype
#
# (c) 2017 Javier Quinteros, GEOFON team
# <javier@gfz-potsdam.de>
#
# ----------------------------------------------------------------------

"""Provgen WS - prototype

   :Platform:
       Linux
   :Copyright:
       GEOFON, GFZ Potsdam <geofon@gfz-potsdam.de>
   :License:
       GNU General Public License v3

.. moduleauthor:: Javier Quinteros <javier@gfz-potsdam.de>, GEOFON, GFZ Potsdam
"""

##################################################################
#
# First all the imports
#
##################################################################


import cherrypy
import os
import json
# from dcmysql import Collection

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

version = '0.1a1'

class IngestAPI(object):
    """Object dispatching methods related to a data file ingestion."""

    def __init__(self):
        """Constructor of the IngestAPI class."""
        pass

    @cherrypy.expose
    def POST(self):
        """Add a new data file.

        :returns: Metadata related to the new file in JSON format.
        :rtype: string
        :raises: cherrypy.HTTPError
        """
        jsonMemb = json.loads(cherrypy.request.body.fp.read())

        # Read only the fields that we support
        fullpath = jsonMemb.get('fullpath', None)
        checksum = jsonMemb.get('checksum', None)

        try:
            irodsfile = IrodsFile(fullpath)
        except:
            # Send Error 404
            messDict = {'code': 0,
                        'message': 'Could not create the file %s !' % fullpath}
            message = json.dumps(messDict)
            cherrypy.log(message, traceback=True)
            cherrypy.response.headers['Content-Type'] = 'application/json'
            raise cherrypy.HTTPError(404, message)

        cherrypy.response.status = '201 File ingested (%s)' % fullpath
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return irodsfile.toJSON()


class DataColl(object):
    """Main class including the dispatcher."""

    def __init__(self):
        """Constructor of the Provgen object."""
        config = configparser.RawConfigParser()
        here = os.path.dirname(__file__)
        config.read(os.path.join(here, 'provgen.cfg'))

        # Read connection parameters
        self.templates = config.get('Service', 'templatedir')

        self.ingest = IngestAPI()

    def _cp_dispatch(self, vpath):
        if len(vpath):
            if vpath[0] in ("features", "version"):
                return self

            if vpath[0] == "collections":
                # Replace "collections" with the request method (e.g. GET, PUT)
                vpath[0] = cherrypy.request.method

                # If there are no more terms to process
                if len(vpath) < 2:
                    return self.colls

                # Remove the collection ID
                cherrypy.request.params['collID'] = vpath.pop(1)
                if len(vpath) > 1:
                    # Remove a word and check that is "members"
                    if vpath[1] not in ("members", "capabilities", "download"):
                        raise cherrypy.HTTPError(400, 'Bad Request')

                    if vpath[1] == "capabilities":
                        vpath.pop(0)
                        return self.coll

                    if vpath[1] == "members":
                        # Remove "members"
                        vpath.pop(1)

                        # Check if there are more parameters
                        if len(vpath) > 1:
                            cherrypy.request.params['memberID'] = vpath.pop(1)
                            if (len(vpath) > 1) and (vpath[1] == "download"):
                                vpath.pop(0)
                            return self.member

                        return self.members

                    if vpath[1] == "download":
                        vpath.pop(0)
                        return self.coll

                return self.coll

        return vpath

    @cherrypy.expose
    def features(self):
        """Read the features of the system and return them in JSON format.

        :returns: System capabilities in JSON format
        :rtype: string
        """
        syscapab = {
                     "whatever": False,
                   }
        cherrypy.response.header_list = [('Content-Type', 'application/json')]
        return json.dumps(syscapab)

    @cherrypy.expose
    def version(self):
        """Return the version of this implementation.

        :returns: System capabilities in JSON format
        :rtype: string
        """
        cherrypy.response.header_list = [('Content-Type', 'text/plain')]
        return version


if __name__ == "__main__":
    cherrypy.quickstart(DataColl(), '/eudat/provgen')
