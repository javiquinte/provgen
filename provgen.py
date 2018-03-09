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
import datetime
import prov.model as prov
from provstore.api import Api
from provstore.api import NotFoundException
import configparser


def customescape(input):
    input = input.replace('/', '\/')
    input = input.replace('+', '\+')
    input = input.replace('=', '\=')
    return input.replace('@', '\@')


@cherrypy.popargs('id')
class RecordsAPI(object):
    def __init__(self, user=None, apikey=None):
        """Constructor of the RecordsAPI class."""
        self.user = user
        self.apikey = apikey

    @cherrypy.expose
    def index(self, id):
        # Read record with provstore.api and send it back to user in N3 format
        api = Api(username=self.user, api_key=self.apikey)
        result = ""
        try:
            id = int(id)
            if cherrypy.request.method == 'GET':
                record = api.document.get(id)
                result = record.prov.serialize(format='rdf', rdf_format='n3')
                cherrypy.response.headers['Content-Type'] = 'text/n3'

            if cherrypy.request.method == 'DELETE':
                api.delete_document(id)
                cherrypy.response.headers['Content-Type'] = 'text/plain'

        except NotFoundException:
            # Send Error 404
            messDict = {'code': 0,
                        'message': 'Record not found: %i' % id}
            message = json.dumps(messDict)
            cherrypy.log(message)
            cherrypy.response.headers['Content-Type'] = 'application/json'
            raise cherrypy.HTTPError(404, message)

        return result


class TemplatesAPI(object):
    """Object dispatching methods related to templates."""

    def __init__(self, directory, user=None, apikey=None):
        """Constructor of the TemplatesAPI class."""
        self.directory = directory
        self.extension = 'n3'
        self.user = user
        self.apikey = apikey

    def retrieve(self, template, params):
        """Fill a template with the parameters passed.

        :returns: Details about the record created in JSON format.
        :rtype: string
        :raises: FileNotFoundError, BadRequest
        """

        prefixLit = 'EUDAT_LITERAL'
        prefixEsc = 'EUDAT_ESCAPE'

        with open(self.directory + '/' + template + '.' + self.extension) as fin:
            # Keep the specification in a list
            wholetemp = fin.read()
            for key, value in params.items():
                wholetemp = wholetemp.replace('{%s:%s}' % (prefixEsc, key), customescape(value))
                wholetemp = wholetemp.replace('{%s:%s}' % (prefixLit, key), value)

            # Check that all variables have been replaced

            # Look for opening markup of variable
            startvar = wholetemp.find('{%s:' % prefixLit)
            if startvar >= 0:
                # Look for closing markup of variable
                endvar = wholetemp.find('}', startvar)
                if endvar >= startvar:
                    raise Exception('Missing variable: %s' % wholetemp[startvar+len(prefixLit)+2:endvar])

            startvar = wholetemp.find('{%s:' % prefixEsc)
            if startvar >= 0:
                # Look for closing markup of variable
                endvar = wholetemp.find('}', startvar)
                if endvar >= startvar:
                    raise Exception('Missing variable: %s' % wholetemp[startvar+len(prefixEsc)+2:endvar])

            # Read record with pyprov and send it in Prov-JSON to ProvStore
            api = Api(username=self.user, api_key=self.apikey)

            doc1 = prov.ProvDocument()
            doc2 = doc1.deserialize(content=wholetemp, format='rdf', rdf_format='n3')
            record = api.document.create(doc2, name="example.n3")
            return json.dumps({'id': record.id,
                               'created_at': record.created_at,
                               'url': record.url}, default=datetime.datetime.isoformat)

    def list(self):
        """List available templates in the system.

        :returns: Metadata related to the available templates in JSON format.
        :rtype: string
        :raises: cherrypy.HTTPError
        """
        try:
            templates = []
            for (dirpath, dirnames, filenames) in os.walk(self.directory):
                # Filter out files not ending with self.extension
                filenames = [fi[:-len(self.extension)-1] for fi in filenames if fi.endswith('.' + self.extension)]
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
            with open(self.directory + '/' + template + '.' + self.extension) as fin:
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
        self.config = configparser.RawConfigParser()
        here = os.path.dirname(__file__)
        self.config.read(os.path.join(here, 'provgen.cfg'))

        # Read connection parameters
        user = self.config.get('ProvStore', 'user')
        apikey = self.config.get('ProvStore', 'apikey')
        self.templatesAPI = TemplatesAPI(self.config.get('Service', 'templatesdir'),
                                         user=user, apikey=apikey)
        self.records = RecordsAPI(user=user, apikey=apikey)

    @cherrypy.expose
    def index(self):
        cherrypy.response.headers['Content-Type'] = 'text/html'

        # TODO Create an HTML page with a minimum documentation for a user
        try:
            with open('help.html') as fin:
                texthelp = fin.read()
        except:
            texthelp = """<html>
                            <head>Provgen - EUDAT</head>
                            <body>
                              Default help for the Provgen service (EUDAT).
                            </body>
                          </html>"""

        return texthelp

    @cherrypy.expose
    def templates(self, *args, **kwargs):
        """Get a template in Notation3 format or a list of templates (JSON).

        :returns: Templates available in JSON format or a template with all variables replaced.
        :rtype: string
        """
        if not len(args):
            cherrypy.response.headers['Content-Type'] = 'application/json'
            return self.templatesAPI.list().encode('utf-8')

        try:
            cherrypy.response.headers['Content-Type'] = 'application/json'
            result = self.templatesAPI.retrieve('/'.join(args), kwargs)
            return result.encode('utf-8')
        except FileNotFoundError:
            # Send Error 404
            messDict = {'code': 0,
                        'message': 'Template %s could not be found.' %
                                   '/'.join(args)}
            message = json.dumps(messDict)
            # cherrypy.log(message)
            cherrypy.response.headers['Content-Type'] = 'application/json'
            raise cherrypy.HTTPError(404, message)
        except Exception as e:
            # Send Error 400
            messDict = {'code': 0,
                        'message': str(e)}
            message = json.dumps(messDict)
            # cherrypy.log(message)
            cherrypy.response.headers['Content-Type'] = 'application/json'
            raise cherrypy.HTTPError(400, message)

    @cherrypy.expose
    def features(self):
        """Read the features of the system and return them in JSON format.

        :returns: System capabilities in JSON format
        :rtype: string
        """
        syscapab = {
                     "ProvStore": self.config.has_section('ProvStore'),
                   }
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps(syscapab).encode('utf-8')

    @cherrypy.expose
    def version(self):
        """Return the version of this implementation.

        :returns: System capabilities in JSON format
        :rtype: string
        """
        version = '0.1a1'
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        return version.encode('utf-8')


server_config = {
    'global': {
        'tools.proxy.on': True,
    	'server.socket_host': '127.0.0.1',
    	'server.socket_port': 8080,
    	'engine.autoreload_on': False
    }
}
cherrypy.tree.mount(Provgen(), '/eudat/provgen', server_config)

if __name__ == "__main__":
    cherrypy.engine.signals.subscribe()
    cherrypy.engine.start()
    cherrypy.engine.block()
