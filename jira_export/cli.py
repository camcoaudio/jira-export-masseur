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
"""JIRA Project Configurator export masseur CLI."""

from argparse import ArgumentParser

from jira_export import Masseur
from yaml import safe_load


def parse_cmdline():
    """Parses command line arguments given to the script.

    Returns:
        the command line arguments parsed by argparse
    """
    parser = ArgumentParser(description=globals()['__doc__'])
    parser.add_argument('-c', '--config', default='prescription.yaml',
                        help='a JIRA project export zip file')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='do not overwrite input files (default: False)')
    parser.add_argument('file', help='a JIRA project export zip file')
    return parser.parse_args()


def main():
    """Program entry point.
    """
    args = parse_cmdline()

    # Load config
    with open(args.config) as conf_file:
        data = conf_file.read()
        config = safe_load(data)

    with Masseur(config['user_name_map'], args.debug) as masseur:
        masseur.massage(args.file)
