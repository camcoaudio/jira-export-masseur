JIRA export masseur
===================

A little library / command-line script that transforms JIRA Project Configurator exports.

At the moment, it is only able to rename users but it should be no big deal to expand its
functionalities if you need more than that. Pull requests are welcome!


Installation
------------

You can use ``setuptools`` to install the library and command-line script::

    $ python setup.py install


Usage
-----

Command-line interface
^^^^^^^^^^^^^^^^^^^^^^

In its easiest form you can call the script like this::

    $ massage-jira-export project-dump.zip

The script is configured with a YAML file. You can find an example configuration at
`docs/prescription.example.yaml <docs/prescription.example.yaml>`_.
