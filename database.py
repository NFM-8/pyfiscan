# -*- coding: utf-8 -*-

"""Provides interface for pyfiscan to YAML-files."""

try:
    import os
    import sys
    import yaml
except ImportError as error:
    print('Import error: %s' % error)
    sys.exit(1)


def gen_yamlfile_locations(yamldir, includes):
    """File handle generator for YAML-files. Only used by database class."""
    if os.path.islink(yamldir):
        sys.exit('Location for YAML-files can not be a symlink: %s' % yamldir)
    if not os.path.isdir(yamldir):
        sys.exit('Location for YAML-files is not a directory: %s' % yamldir)
    for entry in os.scandir(yamldir):
        filename = entry.name
        if filename.startswith('.'):  # skip Vim swap files
            continue
        elif filename.endswith('~'): # skip Emacs temp files
            continue
        elif entry.is_symlink():
            continue
        elif entry.is_dir():
            continue
        elif not entry.is_file():
            continue
        elif not includes and filename.endswith('.yml'):
            yield open(yamldir + filename, 'r')
        elif includes:
            for item in includes:
                if filename == item + '.yml':
                    yield open(yamldir + filename, 'r')


def generate(yamldir, includes):
    """Generates data dictionary of definitions from YAML files. Only used by
    database class.

    """
    data = dict()
    for yamlfile in gen_yamlfile_locations(yamldir, includes):
        try:
            data.update(yaml.safe_load(yamlfile.read())
        except AttributeError:  # empty file
            sys.exit('No data found inside: %s' % yamlfile)
        except yaml.scanner.ScannerError as e:  # syntax error
            sys.exit('Error while loading YAML-file: %s' % e)
        finally:
            yamlfile.close()
    return data


class Database:
    """Reads YAML files and generates a data dictionary of the contents"""
    def __init__(self, yamldir, includes=None):
        self.issues = generate(yamldir, includes)

    def locations(self, application, with_lists=True):
        """Returns list of locations by appname."""
        locations = []
        for issue in self.issues[application].items():
            location = issue[1]['location']
            if with_lists is True:
                locations.append(location)
            else:
                if type(location) == str:
                    locations.append(location)
                elif type(location) == list:
                    locations.extend(location)
        return locations
