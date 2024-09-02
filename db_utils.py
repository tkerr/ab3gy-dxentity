###############################################################################
# db_utils.py - Database management utility functions for the dxentity 
# application.
# Author: Tom Kerr AB3GY
#
# Designed for personal use by the author, but available to anyone under the
# license terms below.
###############################################################################

###############################################################################
# License
# Copyright (c) 2024 Tom Kerr AB3GY (ab3gy@arrl.net).
#
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,   
# this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,  
# this list of conditions and the following disclaimer in the documentation 
# and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without 
# specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.
###############################################################################

# System level packages.
import os
import sys
import json

# Environment setup.
import _env_init

# Local packages.
from db_api import db_api
import parse_cty
import db_tables as tables


###############################################################################
# Globals.
###############################################################################
cty_list = []
dxcc_list = []

###############################################################################
# Functions.
###############################################################################

#------------------------------------------------------------------------------
def print_usage():
    """
    Print a usage statement and exit.
    """
    scriptname = os.path.basename(sys.argv[0])
    print('Usage: {} <cmd> [cty.dat] [dxcc_list.csv]'.format(scriptname))
    print('Run maintenance utilities on the dxentity database.')
    print('Commands:')
    print('  1: Delete the existing database (cannot be undone)')
    print('  2: Initialize a new database')
    print('  3 <cty.dat> [dxcc_list.csv]: Import data from cty.dat and dxcc_list.csv')
    print('  4 <cty.dat> [dxcc_list.csv]: Run commands 1, 2 and 3')
    print('  5 <custom_alias.csv>: Add custom aliases to existing database from csv file')
    print('  6: Print the database version')
    print('  7: Dump the database')
    sys.exit(1)

#------------------------------------------------------------------------------
def db_init():
    """
    Initialize the dxentity database.
    """
    print('Initializing database')
    print('Creating entity table')
    ok1 = tables.create_entity_table()
    print('Creating callsign table')
    ok2 = tables.create_callsign_table()
    print('Creating country table')
    ok3 = tables.create_country_table()
    return (ok1 and ok2 and ok3)

#------------------------------------------------------------------------------
def db_remove():
    """
    Delete an existing dxentity database.
    Operation cannot be undone.
    """
    print('Deleting database')
    ok = tables.delete_database()
    return ok

#------------------------------------------------------------------------------
def db_import():
    """
    Import data from cty.dat (and optionally dxcc_list.csv).
    """
    global cty_list
    print('Importing data into database')
    if (len(cty_list) == 0):
        print('Database import error: cty.dat data not found.')
        return
    api = db_api()
    (good_count, bad_count) = api.import_data(cty_list)
    print('Successful inserts: {}'.format(good_count))
    print('Failed inserts:     {}'.format(bad_count))
    return (good_count, bad_count)

#------------------------------------------------------------------------------
def db_add_custom(filename):
    """
    Add aliases from a custom CSV file.
    Each line of the CSV file must be formatted is as follows:
        <entity>,<alias/=callsign>[,alias/=callsign...]
        Overrides are permitted
    """
    good_count = 0
    bad_count = 0
    try:
        with open(filename, 'r') as fd:
            parse_cty.cty_list = []
            for line in fd:
                (good,bad) = db_add_alias_line(line)
                good_count += good
                bad_count += bad
    except Exception as err:
        print('Error adding custom aliases: {}'.format(str(err)))
    print('Successful inserts: {}'.format(good_count))
    print('Failed inserts:     {}'.format(bad_count))
    return (good_count, bad_count)

#------------------------------------------------------------------------------
def db_add_alias_line(line):
    """
    Add custom aliases from a line in a custom alias CSV file.
    """
    good_count = 0
    bad_count = 0
    api = db_api()
    line = line.strip()
    num_seps = line.count(',')
    if (num_seps > 0):
        idx = line.index(',')
        entity = line[0:idx]
        entity_list = api.select_entity(entity)
        for entry in entity_list:
            current_entity = parse_cty.new_entity(
                type='ENTITY',
                order=entry['PRIORITY'],
                entity=entity,
                alias=entity,
                suffix=entry['SUFFIX'],
                cq_zone=entry['CQZONE'],
                itu_zone=entry['ITUZONE'],
                cont=entry['CONT'],
                lat=entry['LAT'],
                lon=entry['LON'],
                gmt_offset=entry['GMTOFFSET'],
                waedc=entry['WAEDC'],
                country=entry['COUNTRY'],
                dxcc=entry['DXCC'],
            )
            alias_list = parse_cty.parse_custom_aliases(current_entity, line[idx+1:])
            for alias in alias_list:
                status = False
                if (alias['TYPE'] == 'ALIAS'):
                    (status,rowid) = api.entity_row_insert(alias)
                elif (alias['TYPE'] == 'CALLSIGN'):
                    (status,rowid) = api.callsign_row_insert(alias)
                if status:
                    good_count += 1
                else:
                    bad_count += 1
    return (good_count, bad_count)

#------------------------------------------------------------------------------
def db_dump():
    """
    Dump the entire database and pretty print it in JSON format.
    """
    api = db_api()
    result_list = api.dump_database()
    print(json.dumps(result_list, sort_keys=True, indent=2))
    print('Record count: {}'.format(len(result_list)))

#------------------------------------------------------------------------------
def db_get_version():
    """
    Print the database version.
    """
    api = db_api()
    (entity, suffix, country) = api.get_version()
    if (len(suffix) > 0):
        entity += '/{}'.format(suffix.lower())
    print('{}, {}'.format(entity, country))


###############################################################################
# Main program test script.
###############################################################################            
if __name__ == "__main__":

    # Get the command.
    if (len(sys.argv) < 2):
        print('No command specified.')
        print_usage()
    try:
        cmd = int(sys.argv[1])
    except Exception as err:
        print(str(err))
        print_usage()
   
    if (cmd == 3) or (cmd == 4):
        if (len(sys.argv) > 2):
            cty_list = parse_cty.parse_cty(sys.argv[2])
        else:
            print('No cty.dat file specified.')
            print_usage()
        if (len(sys.argv) > 3):
            dxcc_list = parse_cty.parse_dxcc_csv(sys.argv[3])

    if (cmd == 1):
        db_remove()
    elif (cmd == 2):
        db_init()
    elif (cmd == 3):
        db_import()
    elif (cmd == 4):
        ok = db_remove()
        if ok:
            ok = db_init()
            if ok:
                db_import()
    elif (cmd == 5):
        if (len(sys.argv) > 2):
            db_add_custom(sys.argv[2])
        else:
            print('No custom_alias.csv file specified.')
            print_usage()
    elif (cmd == 6):
        db_get_version()
    elif (cmd == 7):
        db_dump()
    else:
        print('Unknown command: {}'.format(cmd))
        print_usage()

    sys.exit(0)
    
# End of file.
