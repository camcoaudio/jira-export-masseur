from setuptools import setup, find_packages

with open('README.rst') as f:
    README = f.read()

with open('COPYING') as f:
    COPYING = f.read()

setup(
    name='jira_export_masseur',
    description='A little "JIRA Project Configurator" export tranformation library.',
    long_description=README,
    keywords=['JIRA', 'project configurator', 'export', 'transform', 'user', 'name', 'username'],
    author='Sebastian Neuser',
    author_email='sebastian.neuser@camco.de',
    url='https://github.com/camcoaudio/jira_export_masseur',
    license=COPYING,
    version='0.1.0',
    install_requires=['lxml', 'pyyaml'],
    packages=find_packages(exclude=('tests', 'docs')),
    entry_points={
        'console_scripts':[
            'massage-jira-export = jira_export.cli:main',
        ]
    },
)
