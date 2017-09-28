#!/usr/bin/env python3
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

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

version = '0.1a1'

class TemplatesAPI(object):
    """Object dispatching methods related to templates."""

    def __init__(self, directory):
        """Constructor of the IngestAPI class."""
        self.directory = directory

    @cherrypy.expose
    def GET(self):
        """List available templates in the system.

        :returns: Metadata related to the available templates in JSON format.
        :rtype: string
        :raises: cherrypy.HTTPError
        """
        try:
            templates = []
            for (dirpath, dirnames, filenames) in os.walk(self.directory):
                templates.extend(filenames)
                break
        except:
            # Send Error 404
            messDict = {'code': 0,
                        'message': 'Could not read the list of available templates'}
            message = json.dumps(messDict)
            cherrypy.log(message, traceback=True)
            cherrypy.response.headers['Content-Type'] = 'application/json'
            raise cherrypy.HTTPError(404, message)

        cherrypy.response.status = '200 OK'
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps(templates)


class Provgen(object):
    """Main class including the dispatcher."""

    def __init__(self):
        """Constructor of the Provgen object."""
        config = configparser.RawConfigParser()
        here = os.path.dirname(__file__)
        config.read(os.path.join(here, 'provgen.cfg'))

        # Read connection parameters
        self.templates = TemplatesAPI(config.get('Service', 'templatedir'))

    def _cp_dispatch(self, vpath):
        if len(vpath):
            if vpath[0] in ("features", "version"):
                return self

            if vpath[0] == "templates":
                # Replace "templates" with the request method (e.g. GET, PUT)
                vpath[0] = cherrypy.request.method

                # If there are no more terms to process
                if len(vpath) < 2:
                    return self.templates

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
    cherrypy.quickstart(Provgen(), '/eudat/provgen')
