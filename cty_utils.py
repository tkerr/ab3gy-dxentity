###############################################################################
# cty_utils.py - Utilities for managing cty.dat and related amateur radio DXCC 
# entity files
# Author: Tom Kerr AB3GY
# 
# cty.dat is a standard DXCC entity database file that is used by many amateur 
# radio programs for associating a callsign with a DXCC entity.
# A good reference can be found here: http://www.country-files.com
# A format reference can be found here:  http://www.country-files.com/cty-dat-format
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
import pprint

# Environment setup.
import _env_init

# Local packages.
from parse_cty import parse_cty, parse_dxcc_csv, get_version

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
    print('Usage: {} <cmd-num> <cty.dat file> [dxcc_list.csv]'.format(scriptname))
    print('Run maintenance utilities on cty.dat and dxcc data')
    print('Commands:')
    print('  1: Print cty.dat version')
    print('  2: Print entities from cty.dat file')
    print('  3: Print the entire cty.dat database')
    print('  4: Sanity check the cty.dat data')
    print('  5: Check for zero DXCC values in cty.dat data')
    print('  6: Cross-check cty.dat and dxcc_list.csv')
    print('  7: Run commands 4, 5, 6')
    sys.exit(1)

#------------------------------------------------------------------------------
def check_data():
    """
    Sanity check the data imported from cty.dat.
    """
    global cty_list
    any_error = False
    print('Sanity check the data imported from cty.dat')
    for entry in cty_list:
        error = False
        if (entry['ORDER'] == 0):
            error = True
            any_error = True
            print('Zero ORDER field:')
        if (len(entry['ENTITY']) == 0):
            error = True
            any_error = True
            print('Empty ENTITY field:')
        if (len(entry['ALIAS']) == 0):
            error = True
            any_error = True
            print('Empty ALIAS field:')
        if (len(entry['COUNTRY']) == 0):
            error = True
            any_error = True
            print('Empty COUNTRY field:')
        if (entry['CQ_ZONE'] == 0):
            error = True
            any_error = True
            print('Zero CQ_ZONE field:')
        if (entry['ITU_ZONE'] == 0):
            error = True
            any_error = True
            print('Zero ITU_ZONE field:')
        if error:
            print(entry)
    if not any_error:
        print('No errors found.')

#------------------------------------------------------------------------------
def check_dxcc():
    """
    Check for zero DXCC values in cty.dat data.
    """
    global cty_list
    global dxcc_list
    any_error = False
    if (len(dxcc_list) == 0):
        print('Empty DXCC list, check not performed.')
        return
    print('Check for zero DXCC values in cty.dat data')
    for entry in cty_list:
        if (entry['DXCC'] <= 0):
            any_error = True
            print('Invalid DXCC:')
            print(entry)
    if not any_error:
        print('No errors found.')

#------------------------------------------------------------------------------
def cross_check():
    """
    Cross-check cty.dat and dxcc_list.csv.
    """
    global cty_list
    global dxcc_list
    cty_entity_list = []
    cty_country_list = []
    dxcc_entity_list = []
    dxcc_country_list = []
    any_error = False
    if (len(dxcc_list) == 0):
        print('Empty DXCC list, cross-check not performed.')
        return
    print('Cross-check cty.dat and dxcc_list.csv')
    
    # Build the cross-check lists.
    for entry in cty_list:
        v = entry['ENTITY']
        if v not in cty_entity_list:
            cty_entity_list.append(v)
        v = entry['COUNTRY']
        if v not in cty_country_list:
            cty_country_list.append(v)
    for entry in dxcc_list:
        v = entry['ENTITY']
        if v not in dxcc_entity_list:
            dxcc_entity_list.append(v)
        v = entry['COUNTRY']
        if v not in dxcc_country_list:
            dxcc_country_list.append(v)
    
    # Check cty list against dxcc list.
    for v in cty_entity_list:
        if v not in dxcc_entity_list:
            any_error = True
            print('"{}" not found in dxcc list'.format(v))
    for v in cty_country_list:
        if v not in dxcc_country_list:
            any_error = True
            print('"{}" not found in dxcc list'.format(v))
    
    # Check dxcc list against cty list.
    for v in dxcc_entity_list:
        if (v != '00'):
            if v not in cty_entity_list:
                any_error = True
                print('"{}" not found in cty list'.format(v))
    for v in dxcc_country_list:
        if (v != 'None'):
            if v not in cty_country_list:
                any_error = True
                print('"{}" not found in cty list'.format(v))
    
    if not any_error:
        print('No errors found.')

#------------------------------------------------------------------------------
def print_database():
    """
    Print the entire cty.dat database.
    """
    global cty_list
    pprint.pp(cty_list, indent=2, width=120)

#------------------------------------------------------------------------------
def print_entities():
    """
    Print entities from cty_list sorted by entity value.
    """
    global cty_list
    dxcc_list = []
    for entry in cty_list:
        if (entry['TYPE'] == 'ENTITY'):
            dxcc_list.append({'ENTITY':entry['ENTITY'], 'COUNTRY':entry['COUNTRY']})
    dxcc_list.sort(key=lambda d: d['ENTITY'])
    for entry in dxcc_list:
        print('{},{}'.format(entry['ENTITY'], entry['COUNTRY']))


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

    if (len(sys.argv) > 2):
        cty_list = parse_cty(sys.argv[2])
    else:
        print('No cty.dat file specified.')
        print_usage()
    if (len(sys.argv) > 3):
        dxcc_list = parse_dxcc_csv(sys.argv[3])

    if (cmd == 1):
        print('cty.dat version: {}'.format(get_version()))
    elif (cmd == 2):
        print_entities()
    elif (cmd == 3):
        print_database()
    elif (cmd == 4):
        check_data()
    elif (cmd == 5):
        check_dxcc()
    elif (cmd == 6):
        cross_check()
    elif (cmd == 7):
        check_data()
        check_dxcc()
        cross_check()
    else:
        print('Unknown command: {}'.format(cmd))
        print_usage()

    sys.exit(0)
    
# End of file.
