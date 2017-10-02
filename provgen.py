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


class TemplatesAPI(object):
    """Object dispatching methods related to templates."""

    def __init__(self, directory):
        """Constructor of the IngestAPI class."""
        self.directory = directory

    def retrieve(self, template):
        """Fill a template with the parameters passed.

        :returns: Complete template in text plain format.
        :rtype: string
        :raises: FileNotFoundError
        """

        with open(self.directory + '/' + template + '.txt') as fin:
            # Keep the specification in a list
            return fin.read()

    def list(self):
        """List available templates in the system.

        :returns: Metadata related to the available templates in JSON format.
        :rtype: string
        :raises: cherrypy.HTTPError
        """
        try:
            templates = []
            # TODO Filter out file names not ending with TXT
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

        # Save the templates specification to be returned
        result = list()
        for template in templates:
            # Open template
            with open(self.directory + '/' + template) as fin:
                # Keep the specification in a list
                docstring = list()
                for line in fin.readlines():
                    if line.startswith('#'):
                        # Add all lines starting with #
                        docstring.append(line[1:])
                    else:
                        # Break as soon as line doesn't start with #
                        break
                result.append({'name': template, 'doc': '\n'.join(docstring)})

        return json.dumps(result)


class Provgen(object):
    """Main class including the dispatcher."""

    def __init__(self):
        """Constructor of the Provgen object."""
        config = configparser.RawConfigParser()
        here = os.path.dirname(__file__)
        config.read(os.path.join(here, 'provgen.cfg'))

        # Read connection parameters
        self.templatesAPI = TemplatesAPI(config.get('Service', 'templatesdir'))

    # def _cp_dispatch(self, vpath):
    #     print(vpath)
    #     if len(vpath):
    #         if vpath[0] in ("templates", "features", "version"):
    #             return self
    #
    #         if vpath[0] == "templates":
    #             # Replace "templates" with the request method (e.g. GET, PUT)
    #             vpath[0] = cherrypy.request.method
    #
    #             # If there are no more terms to process
    #             if len(vpath) < 2:
    #                 return self.templates
    #
    #     return vpath

    @cherrypy.expose
    def index(self):
        cherrypy.response.header_list = [('Content-Type', 'text/plain')]
        return "provgen help should be presented here!"

    @cherrypy.expose
    def templates(self, *args, **kwargs):
        """Read the templates present in the system and return them in JSON format.

        :returns: Templates available in JSON format
        :rtype: string
        """
        if not len(args):
            cherrypy.response.header_list = [('Content-Type', 'application/json')]
            return self.templatesAPI.list()

        cherrypy.response.header_list = [('Content-Type', 'text/plain')]
        try:
            result = self.templatesAPI.retrieve('/'.join(args))
            return result
        except FileNotFoundError:
            # Send Error 404
            messDict = {'code': 0,
                        'message': 'Template %s could not be found.' %
                                   '/'.join(args)}
            message = json.dumps(messDict)
            # cherrypy.log(message)
            cherrypy.response.headers['Content-Type'] = 'application/json'
            raise cherrypy.HTTPError(404, message)

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
        version = '0.1a1'
        cherrypy.response.header_list = [('Content-Type', 'text/plain')]
        return version


if __name__ == "__main__":
    cherrypy.quickstart(Provgen(), '/eudat/provgen')
