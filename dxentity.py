###############################################################################
# dxentity.py - Application to get DX entity information from a callsign
# Author: Tom Kerr AB3GY
# 
# Creates a sqlite database using a cty.dat file and other optional data.
# Searches the database with a supplied callsign to retrieve DX related info
# such as country name, DXCC number, CQ zone, ITU zone, etc.
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


# Environment setup.
import _env_init

# Local packages.
from db_api import db_api


###############################################################################
# Globals.
###############################################################################


###############################################################################
# Functions.
###############################################################################

#------------------------------------------------------------------------------
def check_alias(api, call, alias, waedc):
    """
    Check prefix/suffix to see if it contains a country alias.
    """
    result_list = []
    if (len(alias) > 0):
        # Try the alias as-is.
        result_list = api.select_alias(alias)
        if (len(result_list) == 0):
            # Strip digit from end of alias and try again.
            if (len(alias) > 1) and (alias[-1].isnumeric()):
                result_list = api.select_alias(alias[:-1])
        #print(result_list)
        if (len(result_list) > 0):
            result_list = check_entity_suffix(call, result_list)
            result_list = check_waedc(result_list, waedc)
    return result_list
    
#------------------------------------------------------------------------------
def check_entity_suffix(call, result_list):
    """
    Check the entity suffix when the result list has multiple results.
    Try to select and return only one of the results.
    """
    if (len(result_list) > 1) and (len(call) > 0):
        for result in result_list:
            if 'SUFFIX' in result.keys():
                if (call[-1] == result['SUFFIX']):
                    return [result]
    return result_list

#------------------------------------------------------------------------------
def check_waedc(result_list, waedc):
    """
    Check the DARC WAEDC flag when the result list has multiple results.
    Try to select and return only one of the results.
    """
    if (len(result_list) > 1):
        for result in result_list:
            if 'WAEDC' in result.keys():
                if (result['WAEDC'] == waedc):
                    return [result]
    return result_list
    
#------------------------------------------------------------------------------
def split_callsign(callsign):
    """
    Split the callsign into prefix/call/suffix.
    """
    fields = callsign.split('/')
    max = 0
    call_idx = 0
    pfx  = ''
    call = ''
    sfx  = ''
    # Assume callsign is the longest length field in the list.
    for i in range(len(fields)):
        field = fields[i]
        l = len(field)
        if (l > max):
            max = l
            call_idx = i
    call = fields[call_idx]
    if (call_idx > 0):
        pfx = fields[0]
    if (len(fields) > (call_idx + 1)):
        sfx = fields[call_idx+1]
    
    # Filter some common suffixes that aren't related to DX entities.
    if (sfx == 'QRP'): sfx = ''
    elif (sfx == 'M'): sfx = ''
    elif (sfx == 'P'): sfx = ''
    elif (sfx == 'R'): sfx = ''
    elif sfx.isnumeric(): sfx = ''
    
    # print(pfx, call, sfx)
    return (pfx, call, sfx)

#------------------------------------------------------------------------------
def callsign_lookup(callsign, waedc=-1):
    """
    Parse a callsign and lookup it's DX related info.
    Returns a result list of zero or more database records.
    """
    api = db_api()
    callsign = callsign.strip().upper()
    
    # Check for an exact callsign match.
    result_list = api.select_callsign(callsign)
    if (len(result_list) > 0):
        result_list = check_waedc(result_list, waedc)
        return result_list
    
    # Separate the prefix and suffix.
    (pfx, call, sfx) = split_callsign(callsign)
    
    # Check special suffixes.
    if (sfx == 'AM'):   return []  # Aeronautical mobile
    elif (sfx == 'MM'): return []  # Maritime mobile
    
    # Check the prefix.
    if (len(pfx) > 0):
        result_list = check_alias(api, call, pfx, waedc)
        if (len(result_list) > 0):
            return result_list
            
    # Check the suffix.
    if (len(sfx) > 0):
        result_list = check_alias(api, call, sfx, waedc)
        if (len(result_list) > 0):
            return result_list

    if (len(call) > 0):
        # Check for an exact callsign match without prefix/suffix.
        result_list = api.select_callsign(call)
        if (len(result_list) > 0):
            result_list = check_waedc(result_list, waedc)
            return result_list

        # Whittle down the callsign.
        for i in range(len(call)-1, 0, -1):
            result_list = api.select_alias(call[0:i])
            if (len(result_list) > 0):
                result_list = check_entity_suffix(call, result_list)
                result_list = check_waedc(result_list, waedc)
                return result_list
    return []

#------------------------------------------------------------------------------
def get_country(callsign, waedc=-1):
    """
    Return the country name for a specified callsign.
    """
    result_list = callsign_lookup(callsign)
    if (len(result_list) > 0):
        return result_list[0]['COUNTRY']
    return ''

#------------------------------------------------------------------------------
def get_country_from_dxcc(dxcc):
    """
    Return the country name for a specified DXCC number.
    """
    api = db_api()
    result_list = api.select_dxcc(dxcc)
    if (len(result_list) > 0):
        return result_list[0]['COUNTRY']
    return ''

#------------------------------------------------------------------------------
def get_dx_info(callsign, waedc=-1):
    """
    Return a tuple of DX info for a specified callsign.
    """
    result_list = callsign_lookup(callsign)
    if (len(result_list) > 0):
        result = result_list[0]
        dxinfo = (
            result['ENTITY'],
            result['CONT'],
            result['CQZONE'],
            result['ITUZONE'],
            result['DXCC'],
            result['COUNTRY'],
        )
    else:
        dxinfo = ('', '', 0, 0, 0, '')
    return dxinfo


###############################################################################
# Main program test script.
###############################################################################            
if __name__ == "__main__":
    import os
    import sys
    scriptname = os.path.basename(sys.argv[0])
    if (len(sys.argv) > 1):
        for callsign in sys.argv[1:]:
            dxinfo = get_dx_info(callsign)
            print('{}: {}'.format(callsign.upper(), dxinfo))
    else:
        print('Usage: {} callsign1 [callsign2 [callsign3...]]'.format(scriptname))
        sys.exit(1)
    
# End of file.
