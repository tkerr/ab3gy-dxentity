###############################################################################
# parse_cty.py - Parse the cty.dat amateur radio DXCC entity file
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

import codecs
import copy
import locale
import re


###############################################################################
# Globals.
###############################################################################

cty_list = []
dxcc_list = []

blank_entity = {
    'TYPE'       : '?',
    'ORDER'      : 0,
    'ENTITY'     : '',
    'ALIAS'      : '',
    'SUFFIX'     : '',
    'CQ_ZONE'    : 0,
    'ITU_ZONE'   : 0,
    'CONT'       : '',
    'LAT'        : 0.0,
    'LON'        : 0.0,
    'GMT_OFFSET' : 0.0,
    'WAEDC'      : False,
    'COUNTRY'    : '',
    'DXCC'       : 0,
}

blank_dxcc = {
    'DXCC'     : 0,
    'ENTITY'   : '',
    'COUNTRY'  : '',
}

current_entity = blank_entity
entity_order = 0
line_count = 0
error_count = 0

alias_re = re.compile('(\w+)')
call_re = re.compile('([\w\/]+)')
cq_override_re  = re.compile('(.+)\((\d+)\)')          # CQ zone override in parentheses (value in match group 2)
itu_override_re = re.compile('(.+)\[(\d+)\]')          # ITU zone override in square brackets (value in match group 2)
lat_lon_override_re = re.compile('(.+)\<([\+\-\.\/\d]+)\>')  # Lat/Lon override in angle brackets (value in match group 2)
cont_override_re = re.compile('(.+)\{(\w+)\}')         # Continent override in braces
gmt_override_re = re.compile('(.+)\~([\-\+\.\d]+)\~')  # GMT offset override in parentheses
    

###############################################################################
# Functions.
###############################################################################

# ----------------------------------------------------------------------------
def make_utf8(string_in):
    """
    Ensure a string is encoded as UTF-8.

    Special characters that can't be converted to UTF-8 are ignored and dropped
    from the string.
    """
    enc_in = locale.getpreferredencoding()
    return string_in.encode(enc_in, 'ignore').decode('utf-8', 'ignore')

# ----------------------------------------------------------------------------
def new_entity(type='?', order=0, entity='', alias='', suffix='', cq_zone=0, 
    itu_zone=0, cont='', lat=0.0, lon=0.0, gmt_offset=0.0, waedc=False, 
    country='', dxcc=0):
    """
    Create and return a new, initialized entity info dictionary.
    """
    global blank_entity
    new_entity = copy.deepcopy(blank_entity)
    new_entity['TYPE']       = type.upper()
    new_entity['ORDER']      = int(order)
    new_entity['ENTITY']     = entity.upper()
    new_entity['ALIAS']      = alias.upper()
    new_entity['SUFFIX']     = suffix.upper()
    new_entity['CQ_ZONE']    = int(cq_zone)
    new_entity['ITU_ZONE']   = int(itu_zone)
    new_entity['CONT']       = cont.upper()
    new_entity['LAT']        = float(lat)
    new_entity['LON']        = float(lon)
    new_entity['GMT_OFFSET'] = float(gmt_offset)
    new_entity['WAEDC']      = waedc
    new_entity['COUNTRY']    = country
    new_entity['DXCC']       = int(dxcc)
    return new_entity

# ----------------------------------------------------------------------------
def _parse_entity(line_in):
    """
    Internal function to parse the first line of a DXCC entity in a cty.dat file.
    Appends to the global cty_list.
    """
    global cty_list
    global current_entity
    global entity_order
    entity_order += 1
    entity = new_entity(type='ENTITY', order=entity_order)
    fields = line_in.strip().split(':')
    if (len(fields) > 0): entity['COUNTRY'] = fields[0].strip()
    if (len(fields) > 1): entity['CQ_ZONE'] = int(fields[1].strip())
    if (len(fields) > 2): entity['ITU_ZONE'] = int(fields[2].strip())
    if (len(fields) > 3): entity['CONT'] = fields[3].strip().upper()
    if (len(fields) > 4): entity['LAT'] = float(fields[4].strip())
    if (len(fields) > 5): entity['LON'] = float(fields[5].strip())
    if (len(fields) > 6): entity['GMT_OFFSET'] = float(fields[6].strip())
    if (len(fields) > 7): 
        pfx = fields[7].strip()
        if pfx.startswith('*'):
            entity['WAEDC'] = True
            pfx = pfx[1:]
        idx = pfx.find('/')
        if (idx > 0):
            entity['SUFFIX'] = pfx[idx+1:].upper()
            pfx = pfx[:idx]
        entity['ENTITY'] = pfx
        entity['ALIAS'] = pfx
        current_entity = entity
        cty_list.append(entity)

# ----------------------------------------------------------------------------
def _parse_alias_line(line_in):
    """
    Internal function to parse an entity alias line in a cty.dat file.
    """
    fields = line_in.strip().strip(';').split(',')
    for f in fields:
        f = f.strip()
        if (len(f) > 0):
            if f.startswith('='):
                _parse_callsign(f)
            else:
                _parse_alias(f)

# ----------------------------------------------------------------------------
def _parse_alias(field):
    """
    Internal function to process entity aliases.
    Appends to the global cty_list.
    """
    global cty_list
    global current_entity
    global error_count
    global alias_re
    global cq_override_re
    global itu_override_re
    global lat_lon_override_re
    global cont_override_re
    global gmt_override_re
    m = alias_re.match(field)
    if m:
        alias = m.group(1).upper()
        if (alias != current_entity['ENTITY']):
            entity = new_entity(
                type='ALIAS',
                order=current_entity['ORDER'],
                entity=current_entity['ENTITY'],
                alias=alias,
                suffix=current_entity['SUFFIX'],
                cq_zone=current_entity['CQ_ZONE'],
                itu_zone=current_entity['ITU_ZONE'],
                cont=current_entity['CONT'],
                lat=current_entity['LAT'],
                lon=current_entity['LON'],
                gmt_offset=current_entity['GMT_OFFSET'],
                waedc=current_entity['WAEDC'],
                country=current_entity['COUNTRY'],
            )
            entity = _parse_overrides(field, entity)
            cty_list.append(entity)
    else:
        error_count += 1
        print('Alias match error: {}'.format(field))

# ----------------------------------------------------------------------------
def _parse_callsign(field):
    """
    Internal function to parse callsigns.
    Appends to the global cty_list.
    """
    global cty_list
    global current_entity
    global error_count
    field = field[1:]
    m = call_re.match(field)
    if m:
        callsign = m.group(1).upper()
        entity = new_entity(
            type='CALLSIGN',
            order=current_entity['ORDER'],
            entity=current_entity['ENTITY'],
            alias=callsign,
            suffix=current_entity['SUFFIX'],
            cq_zone=current_entity['CQ_ZONE'],
            itu_zone=current_entity['ITU_ZONE'],
            cont=current_entity['CONT'],
            lat=current_entity['LAT'],
            lon=current_entity['LON'],
            gmt_offset=current_entity['GMT_OFFSET'],
            waedc=current_entity['WAEDC'],
            country=current_entity['COUNTRY'],
        )
        entity = _parse_overrides(field, entity)
        cty_list.append(entity)
    else:
        error_count += 1
        print('Callsign match error: {}'.format(field))

# ----------------------------------------------------------------------------
def _parse_overrides(field, entity):
    """
    Internal function to process alias and callsign overrides.
    """
    m = cq_override_re.match(field)
    if m:
        entity['CQ_ZONE'] = int(m.group(2))
        #print('{} {}'.format(field, entity['CQ_ZONE']))
    m = itu_override_re.match(field)
    if m:
        entity['ITU_ZONE'] = int(m.group(2))
        #print('{} {}'.format(field, entity['ITU_ZONE']))
    m = lat_lon_override_re.match(field)
    if m:
        v = m.group(2)
        idx = v.find('/')
        if (idx > 0):
            entity['LAT'] = float(v[0:idx])
            entity['LON'] = float(v[idx+1:])
        else:
            entity['LAT'] = float(v)
        #print('{} {} {} {}'.format(field, v, entity['LAT'], entity['LON']))
    m = cont_override_re.match(field)
    if m:
        entity['CONT'] = m.group(2).upper()
        #print('{} {}'.format(field, entity['CONT']))
    m = gmt_override_re.match(field)
    if m:
        entity['GMT_OFFSET'] = float(m.group(2))
        #print('{} {}'.format(field, entity['GMT_OFFSET']))
    return entity

# ----------------------------------------------------------------------------
def parse_cty(filename):
    """
    Public function to parse a file in cty.dat format.
    Returns a list of entities formatted as dictionaries.
    """
    global error_count
    global line_count
    global cty_list
    cty_list = []
    try:
        cty_in = codecs.open(filename, mode='r', encoding='utf-8', errors='ignore')
    except Exception as err:
        print('Error opening {}: {}'.format(filename, str(err)))
        error_count += 1
        return cty_list
    try:
        for line in cty_in:
            line_count += 1
            line = make_utf8(line)
            if line.startswith(' '):
                _parse_alias_line(line)
            else:
                _parse_entity(line)
        cty_in.close()
    except Exception as err:
        print('Error parsing dat file: {}: {}'.format(filename, str(err)))
        error_count += 1
        return cty_list
    return cty_list

# ----------------------------------------------------------------------------
def parse_dxcc_csv(filename):
    """
    Public function to parse a DXCC entity CSV file.
    Format is <dxcc-number>,<entity-prefix>,<country-name>
    Returns a list of dxcc entities formatted as dictionaries.
    The order of entries in the CSV file is the assumed priority of search.
    Also adds the DXCC code to the global cty_list if parse_cty() has been run.
    """
    global cty_list
    global dxcc_list
    dxcc_list = []
    try:
        dxcc_in = codecs.open(filename, mode='r', encoding='utf-8', errors='ignore')
    except Exception as err:
        print('Error opening {}: {}'.format(filename, str(err)))
        return dxcc_list
    try:
        for line in dxcc_in:
            line = make_utf8(line)
            fields = line.strip().split(',')
            if (len(fields) > 2):
                if (len(fields) > 3):
                    # Country name has commas in it - join it back together
                    country = ','.join(fields[2:])
                else:
                    country = fields[2]
                country = country.strip('"')
                new_dxcc = copy.deepcopy(blank_dxcc)
                new_dxcc['DXCC'] = int(fields[0])
                new_dxcc['ENTITY'] = fields[1].upper()
                new_dxcc['COUNTRY'] = country
                dxcc_list.append(new_dxcc)
                
                # Add DXCC code to the ctl_list entry if it is blank.
                # This assumes that the entity order in cty.dat and the CSV file match.
                for entry in cty_list:
                    if (entry['ENTITY'] == new_dxcc['ENTITY']):
                        if (entry['DXCC'] == 0):
                            entry['DXCC'] = new_dxcc['DXCC']
                            break;
    except Exception as err:
        print('Error parsing CSV file: {}: {}'.format(filename, str(err)))
        return dxcc_list
    return dxcc_list

# ----------------------------------------------------------------------------
def parse_custom_aliases(entity, alias_line):
    """
    Public function to parse a list of custom aliases for a specified entity.
    Parameters:
        entity (dict): Entity dictionary as defined by blank_entity.
        alias_line (str): Comma-separated alias list in cty.dat format.
            Overrides are allowed.
    Returns:
        List of aliases formatted as dictionaries.
    """
    global cty_list
    global current_entity
    cty_list = []
    current_entity = entity
    _parse_alias_line(alias_line)
    return cty_list


# ----------------------------------------------------------------------------
def get_version():
    """
    Return the cty.dat version by looking up the VERSION alias.
    """
    global cty_list
    version = ''
    for entry in cty_list:
        if (entry['ALIAS'] == 'VERSION'):
            version = '{},{}'.format(entry['ENTITY'], entry['COUNTRY'])
            break
    return version
    

###############################################################################
# Main program test script.
###############################################################################            
if __name__ == "__main__":

    import os
    import sys
    import pprint
    
    my_country_list = []
    
    scriptname = os.path.basename(sys.argv[0])
    if (len(sys.argv) > 1):
        cty_filename = sys.argv[1]
    else:
        print('Usage: {} <cty.dat file> [dxcc_list.csv]'.format(scriptname))
        sys.exit(1)

    my_cty_list = parse_cty(cty_filename)
    if (len(sys.argv) > 2):
        parse_dxcc_csv(sys.argv[2])
        
    pprint.pp(my_cty_list, indent=2, width=120)
    print('{} line count: {}  Error count: {}'.format(cty_filename, line_count, error_count))
    print('List size: {}'.format(len(cty_list)))
    print('Version: {}'.format(get_version()))
    sys.exit(0)
    
# End of file.
