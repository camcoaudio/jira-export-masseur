# Copyright 2017 Sebastian Neuser
#
# This file is part of jira_export_masseur.
#
# jira_export_masseur is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jira_export_masseur is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with jira_export_masseur. If not, see <http://www.gnu.org/licenses/>.
"""JIRA Project Configurator export masseur main logic."""

from io import BytesIO
from os import unlink
from re import sub
from shutil import make_archive, rmtree
from tempfile import mkdtemp
from zipfile import ZipFile

from lxml.etree import XMLParser, parse, tostring


class Masseur(object):
    """Instances of this class can be used to transform exported JIRA projects.

    Attributes:
        user_name_map:  a `dict` of strings that describes user name transitions {old: new}
        debug:          if `True`, processed files are placed next to originals and the zip file is
                        not packed to ease diffing of results
    """

    # Define default XML parser options
    _PARSER = XMLParser(strip_cdata=False, resolve_entities=False)

    def __init__(self, user_name_map, debug=False):
        self.debug = debug
        self.user_name_map = user_name_map

        # Prepare workspace and paths
        self._workspace = mkdtemp()
        self._config_xml_path = self.workspace_path('config.xml')
        self._data_zip_path = self.data_path('/data.zip')
        self._objects_xml_path = self.data_path('/activeobjects.xml')
        self._entities_xml_path = self.data_path('/entities.xml')

    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        if self.debug:
            return
        rmtree(self.workspace_path())


    def _prepare_output_path(self, path):
        """Prepares the output path for an XML file.

        Args:
            path:   the input path
            debug:  if set to `True` the input path is modified to allow diffing the files
        """
        if not self.debug:
            return path
        return sub(r'\.xml', r'.proc.xml', path)


    def data_path(self, path=None):
        """Returns the absolute path to the data directory in the workspace.

        Args:
            path:   if provided, this path is appended to the data path
        """
        if path is None:
            return self.workspace_path('data')
        return self.workspace_path('data/' + path)


    def massage(self, export_zip_path):
        """Takes a complete export zip file and makes transformations.

        Args:
            export_zip_path:    path to the exported zip
        """
        self.unpack(export_zip_path)
        self.update_config(self._config_xml_path, self._prepare_output_path(self._config_xml_path))
        self.update_entities(self._entities_xml_path,
                             self._prepare_output_path(self._entities_xml_path))

        # Pack new zip file
        if not self.debug:
            self.pack(export_zip_path)


    def pack(self, export_zip_path):
        """Re-packs processed JIRA export files to a zip.
        """
        entities_xml_out_path = self._prepare_output_path(self._entities_xml_path)
        with ZipFile(self._data_zip_path, 'w') as data_zip:
            data_zip.write(self._objects_xml_path, 'activeobjects.xml')
            data_zip.write(entities_xml_out_path, 'entities.xml')
        unlink(self._objects_xml_path)
        unlink(entities_xml_out_path)
        outfile = sub(r'\.zip', r'.fixed_users', export_zip_path)
        make_archive(outfile, 'zip', self.workspace_path())


    def unpack(self, export_zip_path):
        """Unpacks a JIRA project export zip.

        Args:
            export_zip_path:    path to the exported zip
        """
        # Unpack project export
        with ZipFile(export_zip_path) as project_export_zip:
            project_export_zip.extractall(path=self.workspace_path())
        with ZipFile(self._data_zip_path) as data_zip:
            data_zip.extractall(path=self.data_path())


    def update_config(self, in_path, out_path):
        """Updates user names in config.xml.

        Args:
            in_path:    path to the XML file to read from
            out_path:   path to the XML file to write to
        """
        def _update_children(root, name):
            for elem in root.findall('.//' + name):
                if elem.text not in self.user_name_map.keys():
                    continue
                elem.text = self.user_name_map[elem.text]

        config = parse(in_path, parser=self._PARSER)

        for elem in ['administratorUser', 'author', 'lead', 'memberUser', 'owner', 'username']:
            _update_children(config, elem)

        with open(out_path, 'w') as config_xml:
            config_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            config_xml.write(tostring(config, encoding='unicode'))


    def update_entities(self, in_path, out_path):
        """Updates user names in entities.xml

        Args:
            in_path:    path to the XML file to read from
            out_path:   path to the XML file to write to
        """
        def _update_attributes(root, name):
            for elem in root.findall('.//*[@{}]'.format(name)):
                for username in self.user_name_map:
                    if elem.attrib[name] == username:
                        elem.attrib[name] = self.user_name_map[username]
                    else:
                        elem.attrib[name] = sub(' {} '.format(username),
                                                ' {} '.format(self.user_name_map[username]),
                                                elem.attrib[name])

        with open(in_path, newline='\n') as entities_xml:
            content = entities_xml.read()
        content = sub('\x0c', '\u2622', content)
        content = sub('\x0d', '\u2623', content)
        content = bytes(content, 'utf-8')
        entities = parse(BytesIO(content), parser=self._PARSER)

        for attr in ['author',
                     'authorKey',
                     'caller',
                     'creator',
                     'deltaFrom',
                     'deltaTo',
                     'entityId',
                     'lead',
                     'lowerChildName',
                     'lowerUserName',
                     'newvalue',
                     'objectName',
                     'oldvalue',
                     'owner',
                     'roletypeparameter',
                     'sourceName',
                     'updateauthor',
                     'user',
                     'username']:
            _update_attributes(entities, attr)
        for attr in ['author',
                     'body',
                     'data',
                     'deltaTo',
                     'description',
                     'infoMessage',
                     'name',
                     'newstring',
                     'oldstring',
                     'searchField',
                     'summary',
                     'title']:
            for elem in entities.findall('.//*[@{}]'.format(attr)):
                elem.set(attr, sub("'", '\u2624', elem.get(attr)))

        content = tostring(entities, encoding=str)
        content = sub('\u2622', '\x0c', content)
        content = sub('\u2623', '\x0d', content)
        content = sub('\u2624', '&apos;', content)
        content = sub('--><', '-->\n<', content)

        with open(out_path, 'w') as entities_xml:
            entities_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            entities_xml.write(content)


    def workspace_path(self, path=None):
        """Returns the absolute path to the workspace.

        Args:
            path:   if provided, this path is appended to the workspace path
        """
        if path is None:
            return self._workspace
        return self._workspace + '/' + path
