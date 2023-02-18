###############################################################################
# dxentity.py - Amateur radio DXCC entity processing module.
# Author: Tom Kerr AB3GY
#
# Provides methods for associating callsigns with DXCC entity countries.
# 
# Typical usage is to import a cty.dat file using import_cty_dat(), then use 
# calls to get_country() to return a country name string for callsigns of 
# interest.
# 
# dump_callsigns() and dump_prefixes() will print the unique callsigns and
# callsign prefixes obtained from a source cty.dat to stdout or a file.  Data
# is in CSV format.
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
# Copyright (c) 2020 Tom Kerr AB3GY (ab3gy@arrl.net).
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

from bisect import bisect_left
import codecs
import collections
import locale
import re
import sys
import traceback

class dxentity (object):

    #--------------------------------------------------------------------------
    def __init__(self, verbose=False):
        """
        Class constructor.
        """ 
        self.__version__ = str("0.1")  # Version per PEP 396
        
        # Class members intended to be "public"
        self.Verbose = verbose
        
        # Dictionary of data values based on country.
        self._data = {}
        self._CQ   = 0     # CQ Zone index
        self._ITU  = 1     # ITU Zone index
        self._CONT = 2     # Continent index
        
        # Dictionary of ADIF-specified DXCC entities based on the DXCC entity.
        self._dxcc_entity = {}
        self._CODE = 0         # DXCC entity code index
        self._DELETED = 1      # DXCC deleted flag index
        self._ALT = 2          # DXCC alternate country name (from cty.dat file)
        
        # List of unique callsigns and their associated countries.
        self._call_callsign = []
        self._call_country = []
        
        # List of callsign prefixes based on first character of prefix.
        # Each list is sorted by prefix length from largest to smallest, then alphabetical order
        # within each same-length subgroup.
        self._pfx_0, self._pfx_1, self._pfx_2, self._pfx_3, self._pfx_4 = [], [], [], [], []
        self._pfx_5, self._pfx_6, self._pfx_7, self._pfx_8, self._pfx_9 = [], [], [], [], []
        self._pfx_A, self._pfx_B, self._pfx_C, self._pfx_D, self._pfx_E = [], [], [], [], []
        self._pfx_F, self._pfx_G, self._pfx_H, self._pfx_I, self._pfx_J = [], [], [], [], []
        self._pfx_K, self._pfx_L, self._pfx_M, self._pfx_N, self._pfx_O = [], [], [], [], []
        self._pfx_P, self._pfx_Q, self._pfx_R, self._pfx_S, self._pfx_T = [], [], [], [], []
        self._pfx_U, self._pfx_V, self._pfx_W, self._pfx_X, self._pfx_Y = [], [], [], [], []
        self._pfx_Z = []
        
        # Dictionary of the above lists.
        self._PFX_PFX = 0
        self._PFX_COUNTRY = 1
        self._pfx_list = {
            "0" : self._pfx_0, "1" : self._pfx_1, "2" : self._pfx_2, "3" : self._pfx_3, "4" : self._pfx_4,
            "5" : self._pfx_5, "6" : self._pfx_6, "7" : self._pfx_7, "8" : self._pfx_8, "9" : self._pfx_9,
            "A" : self._pfx_A, "B" : self._pfx_B, "C" : self._pfx_C, "D" : self._pfx_D, "E" : self._pfx_E,
            "F" : self._pfx_F, "G" : self._pfx_G, "H" : self._pfx_H, "I" : self._pfx_I, "J" : self._pfx_J,
            "K" : self._pfx_K, "L" : self._pfx_L, "M" : self._pfx_M, "N" : self._pfx_N, "O" : self._pfx_O,
            "P" : self._pfx_P, "Q" : self._pfx_Q, "R" : self._pfx_R, "S" : self._pfx_S, "T" : self._pfx_T,
            "U" : self._pfx_U, "V" : self._pfx_V, "W" : self._pfx_W, "X" : self._pfx_X, "Y" : self._pfx_Y,
            "Z" : self._pfx_Z }
            
        # List of callsign prefix meta data based on first character of prefix.
        # Used for alphabetical sort of list for each subgroup based on prefix length.
        # Fields are as follows:
        # [prefix list length, max length, min length,  
        #  index of max length, index of next smallest length, ... , index of min length, 
        #  prefix list length (again)]
        self._META_LEN = 0
        self._META_MAX = 1
        self._META_MIN = 2
        self._meta_0, self._meta_1, self._meta_2, self._meta_3, self._meta_4 = [0,0,100], [0,0,100], [0,0,100], [0,0,100], [0,0,100]
        self._meta_5, self._meta_6, self._meta_7, self._meta_8, self._meta_9 = [0,0,100], [0,0,100], [0,0,100], [0,0,100], [0,0,100]
        self._meta_A, self._meta_B, self._meta_C, self._meta_D, self._meta_E = [0,0,100], [0,0,100], [0,0,100], [0,0,100], [0,0,100]
        self._meta_F, self._meta_G, self._meta_H, self._meta_I, self._meta_J = [0,0,100], [0,0,100], [0,0,100], [0,0,100], [0,0,100]
        self._meta_K, self._meta_L, self._meta_M, self._meta_N, self._meta_O = [0,0,100], [0,0,100], [0,0,100], [0,0,100], [0,0,100]
        self._meta_P, self._meta_Q, self._meta_R, self._meta_S, self._meta_T = [0,0,100], [0,0,100], [0,0,100], [0,0,100], [0,0,100]
        self._meta_U, self._meta_V, self._meta_W, self._meta_X, self._meta_Y = [0,0,100], [0,0,100], [0,0,100], [0,0,100], [0,0,100]
        self._meta_Z = [0,0,100]
        
    # Dictionary of the above lists.
        self._meta_list = {
            "0" : self._meta_0, "1" : self._meta_1, "2" : self._meta_2, "3" : self._meta_3, "4" : self._meta_4,
            "5" : self._meta_5, "6" : self._meta_6, "7" : self._meta_7, "8" : self._meta_8, "9" : self._meta_9,
            "A" : self._meta_A, "B" : self._meta_B, "C" : self._meta_C, "D" : self._meta_D, "E" : self._meta_E,
            "F" : self._meta_F, "G" : self._meta_G, "H" : self._meta_H, "I" : self._meta_I, "J" : self._meta_J,
            "K" : self._meta_K, "L" : self._meta_L, "M" : self._meta_M, "N" : self._meta_N, "O" : self._meta_O,
            "P" : self._meta_P, "Q" : self._meta_Q, "R" : self._meta_R, "S" : self._meta_S, "T" : self._meta_T,
            "U" : self._meta_U, "V" : self._meta_V, "W" : self._meta_W, "X" : self._meta_X, "Y" : self._meta_Y,
            "Z" : self._meta_Z }
            
            
    ###########################################################################
    # Class methods intended to be private.
    ###########################################################################            
    
    # ------------------------------------------------------------------------    
    def _print_msg(self, msg):
        """
        Print a formatted message.  Used internally for verbose printing.

        Parameters
        ----------
        msg : str
            The message text to print.
        
        Returns
        -------
        None
        """
        cl = type(self).__name__                         # This class name
        fn = str(traceback.extract_stack(None, 2)[0][2]) # Calling function name
        print(cl + '.' + fn + ': ' + msg)

    #--------------------------------------------------------------------------   
    def _add_callsign(self, callsign, country):
        """
        Add the unique callsign and country into the database in sorted order.
        """
        index = bisect_left(self._call_callsign, callsign)
        self._call_callsign.insert(index, callsign)
        self._call_country.insert(index, country)

    #--------------------------------------------------------------------------    
    def _add_pfx(self, pfx, country):
        """
        Add the prefix and country into the database sorted by length from 
        longest to shortest.
        """
        c = pfx[0]
        lp = len(pfx)
        ll = len(self._pfx_list[c])
        if ll == 0:
            # Initialize the prefix list for this prefix.
            self._pfx_list[c].insert(0, [pfx, country])
        else:
            added = False
            for index in range(ll):
                # Insert prefix into database in order from longest to shortest.
                if lp > len(self._pfx_list[c][index][self._PFX_PFX]):
                    self._pfx_list[c].insert(index, [pfx, country])
                    added = True
                    break;
            if not added:
                # Shortest prefix so far. Append it to the end.
                self._pfx_list[c].append([pfx, country])
                
        # Update the metadata for this list.
        if lp > self._meta_list[c][self._META_MAX]:
            self._meta_list[c][self._META_MAX] = lp
        if lp < self._meta_list[c][self._META_MIN]:
            self._meta_list[c][self._META_MIN] = lp

    #--------------------------------------------------------------------------
    def _callsign_index(self, call):
        """
        Binary search the list of unique callsigns.
        Return the index of the callsign if found, or -1 if not found.
        """
        min = 0
        max = len(self._call_callsign) - 1
        while True:
            if max < min:
                return -1
            mid = (min + max) // 2
            if self._call_callsign[mid] < call:
                min = mid + 1
            elif self._call_callsign[mid] > call:
                max = mid - 1
            else:
                return mid

    #--------------------------------------------------------------------------    
    def _do_pfx_sort(self, pfx_list, min, max):
        """
        Brute force bubble sort.
        """
        swapped = True
        while swapped:
            swapped = False
            for i in range(min, max):
                if pfx_list[i][self._PFX_PFX] > pfx_list[i+1][self._PFX_PFX]:
                    pfx_list[i], pfx_list[i+1] = pfx_list[i+1], pfx_list[i]
                    swapped = True

    #--------------------------------------------------------------------------                
    def _make_pfx_meta(self):
        """
        Build the prefix metadata lists.
        """
        for key in self._meta_list.keys():
            # Add the list length.
            ll = len(self._pfx_list[key])
            self._meta_list[key][self._META_LEN] = ll
            if ll > 0: 
                lp1 = len(self._pfx_list[key][0][self._PFX_PFX])  # Length of max length prefix
                self._meta_list[key].append(0)                    # Index of max length prefix is always zero
                
                # Add the index of the start of each smaller prefix length.
                for i in range(ll):
                    lp2 = len(self._pfx_list[key][i][self._PFX_PFX])
                    if lp2 < lp1:
                        self._meta_list[key].append(i)
                        lp1 = lp2
                        
                # Add length of prefix in list as a convenience item for sorting.
                self._meta_list[key].append(ll)

    #--------------------------------------------------------------------------            
    def _prefix_index(self, call):
        """
        Return the index of the call's prefix in the corresponding prefix list.
        Returns -1 if not found.
        """
        index = -1
        c = call[0]
        pfx_list = []
        meta_list = []
        try:
            pfx_list = self._pfx_list[c]
            meta_list = self._meta_list[c]
        except KeyError:
            return -1
        for i in range(3, len(meta_list) - 1):
            min = meta_list[i]
            max = meta_list[i+1] - 1
            lp = len(pfx_list[min][self._PFX_PFX])
            if len(call) >= lp:
                pfx = call[0:lp]
                index = self._prefix_search(pfx_list, pfx, min, max)
                if index >= 0: break
        return index

    #--------------------------------------------------------------------------    
    def _prefix_search(self, pfx_list, pfx, min, max):
        """
        Perform a binary search on the specified prefix list for the prefix.
        The search is performed between the min and max index values provided.
        Returns the index of the prefix in the list if found, or -1 if not found.
        """
        while True:
            if max < min:
                return -1
            mid = (min + max) // 2
            if pfx_list[mid][self._PFX_PFX] < pfx:
                min = mid + 1
            elif pfx_list[mid][self._PFX_PFX] > pfx:
                max = mid - 1
            else:
                return mid

    #--------------------------------------------------------------------------    
    def _sort_pfx_byalpha(self):
        """
        Sort the prefixes in each length subgroup in alphabetical order.
        """
        for key in self._pfx_list.keys():
            if self._meta_list[key][self._META_LEN] > 0:
                for i in range(3, len(self._meta_list[key])-1):
                    min = self._meta_list[key][i]
                    max = self._meta_list[key][i+1] - 1
                    self._do_pfx_sort(self._pfx_list[key], min, max)
       

    ###########################################################################
    # Class methods intended to be public.
    ###########################################################################
    
    def dump_callsigns(self, filename=""):
        """
        Dump the callsign database as a comma-separated list of callsign,country.
        Write to a file if a filename is given, otherwise print to stdout.  
        """
        f_out = None
        status = 0
        
        # Open output file if file name is provided.
        if len(filename) > 0:
            try:
                f_out = open(filename, 'w')
            except Exception as e:
                if self.Verbose:
                    self._print_msg(str(e))
                return -1
                
        # Dump the callsigns.
        for index in range(len(self._call_callsign)):
            record = str(self._call_callsign[index] + "," + self._call_country[index])
            if f_out:
                try:
                    f_out.write(record + "\n")
                except Exception as e:
                    if self.Verbose:
                        self._print_msg(str(e))
                    status = -1
                    break
            else:
                print(record)
        
        if f_out:
            f_out.close()
            
        return status

    #--------------------------------------------------------------------------    
    def dump_prefixes(self, filename=""):
        """
        Dump the prefix database as a comma-separated list of prefix,country.
        Write to a file if a filename is given, otherwise print to stdout.
        """
        f_out = None
        status = 0
        
        # Open output file if file name is provided.
        if len(filename) > 0:
            try:
                f_out = open(filename, 'w')
            except Exception as e:
                if self.Verbose:
                    self._print_msg(str(e))
                return -1
        
        # Dump the prefixes.        
        for key in sorted(self._pfx_list.keys()):
            ll = len(self._pfx_list[key])
            if ll > 0:
                for index in range(ll):
                    record = self._pfx_list[key][index][self._PFX_PFX] + "," + self._pfx_list[key][index][self._PFX_COUNTRY]
                    if f_out:
                        try:
                            f_out.write(record + "\n")
                        except Exception as e:
                            if self.Verbose:
                                self._print_msg(str(e))
                            status = -1
                            break
                    else:
                         print(record)
        if f_out:
            f_out.close()
            
        return status

    #--------------------------------------------------------------------------    
    def get_continent(self, country):
        """
        Lookup the country name in the database and return its associated continent.
        Returns the continent enumeration string if found, or an empty string if not found.
        """
        cont = ""
        if len(country) > 0:
            country = country.upper()
            if country in self._data.keys():
                cont = self._data[country][self._CONT]
        return cont

    #--------------------------------------------------------------------------    
    def get_country(self, call):
        """
        Lookup the callsign in the database and return its associated country.
        Returns the country name string if found, or an empty string if not found.
        """
        if len(call) > 0:
            callsign = call.upper()
            c = callsign[0]
        
            # Check unique callsigns first.
            index = self._callsign_index(callsign)
            if index >= 0:
                return self._call_country[index]
            
            # Check prefixes next.
            index = self._prefix_index(callsign)
            if index >= 0:
                return self._pfx_list[c][index][self._PFX_COUNTRY]
            
        return str("")

    #--------------------------------------------------------------------------    
    def get_country_from_dxcc(self, dxcc):
        """
        Return the country name for a DXCC entity number.
        Returns the country name string if found, or an empty string if not found.
        """
        country = str("")
        
        # Make sure DXCC is a non-negative integer.
        dxcc_in = 0
        try:
            dxcc_in = int(dxcc)
            if (dxcc_in < 0): return country
        except (TypeError, ValueError):
            return country
            
        for (k, v) in self._dxcc_entity.items():
            dxcc_val = int(v[self._CODE])
            if (dxcc_val == dxcc_in):
                country = str(k)
                break
        return country

    #--------------------------------------------------------------------------    
    def get_cq(self, country):
        """
        Lookup the country name in the database and return its associated CQ zone.
        Returns the CQ zone as a string if found, or an empty string if not found.
        """
        cq = ""
        if len(country) > 0:
            country = country.upper()
            if country in self._data.keys():
                cq = self._data[country][self._CQ]
        return cq

    #--------------------------------------------------------------------------    
    def get_dxcc(self, country):
        """
        Lookup the country name in the database and return its associated DXCC code.
        Returns the DXCC code as a string if found.  Returns '0' if DXCC not found.
        """
        dxcc_code = '0'
        entity = self.get_entity(country)
        
        try:
            dxcc_code = self._dxcc_entity[entity][self._CODE]
        except KeyError as e:
            dxcc_code = '0'
            
        return dxcc_code

    #--------------------------------------------------------------------------   
    def get_entity(self, country_in):
        """
        Attempt to find the ADIF specified entity name for the given input country.
        The CTY.DAT file formats country names to 26 characters or less.  This 
        method attempts to match the country name to the ADIF-specified entity name.
        
        NOTE: A better way to do this would be with fuzzy matching, but the Python 
        fuzzywuzzy package has many dependencies under Windows (including Visual Studio)
        and makes this package less portable.
        """
        country_in = country_in.strip().upper()
        entity_out = country_in
        entity_found = False
        
        try:
            alt = self._dxcc_entity[country_in][self._ALT]
            # If we made it this far, then country_in is a vaid entity.
            entity_found = True
        except KeyError as e:
            entity_found = False
            
        if not entity_found:
            entity_list = self._dxcc_entity.keys()
            for entity in entity_list:
                alt = self._dxcc_entity[entity][self._ALT]
                if len(alt) > 0:
                    if country_in == alt:
                        # Found an alternative name from cty.dat.
                        entity_out = entity
                        # if self.Verbose: print(country_in + ' converted to ' + entity_out)
                        break
        return entity_out

   #--------------------------------------------------------------------------    
    def get_itu(self, country):
        """
        Lookup the country name in the database and return its associated ITU zone.
        Returns the ITU zone as a string if found, or an empty string if not found.
        """
        itu = ""
        if len(country) > 0:
            country = country.upper()
            if country in self._data.keys():
                itu = self._data[country][self._ITU]
        return itu

    #--------------------------------------------------------------------------
    def import_cty_dat(self, cty_dat_file):
        """
        Import a cty.dat file and use it for DXCC entity processing.
        cty.dat is a standard DXCC entity database file that is used by many amateur 
        radio programs for associating a callsign with a DXCC entity.
        A good reference can be found here: http://www.country-files.com
        A format reference can be found here:  http://www.country-files.com/cty-dat-format
        """
        if self.Verbose:
            self._print_msg('Importing ' + cty_dat_file)
        try:
            cty_in = codecs.open(cty_dat_file, mode='r', encoding='utf-8', errors='ignore')
        except Exception as e:
            if self.Verbose:
                self._print_msg(str(e))
            return -1

        itu_override_re = re.compile("(.+)(\[\d+\])")    # callsign prefix with ITU zone override in brackets
        cq_override_re  = re.compile("(.+)(\(\d+\))")    # callsign prefix with CQ zone override in parentheses
        continent_override_re = re.compile("(.+)(\{\w\w\})")  # callsign prefix with continent override in braces
        tz_override_re = re.compile("(.+)(\~\-?\d+\~)")  # callsign prefix with GMT offset override in parentheses
        
        country = str("")
        
        for line in cty_in:
        # If line starts with a space, then it is a continuation with a list
        # of prefixes and/or callsigns.
            line = self.make_utf8(line)
            if line.startswith(" "):
                pfx_list = line.strip().strip(";").split(",")
                for pfx in pfx_list:
            
                    # Strip ITU zone overrides.
                    m = itu_override_re.search(pfx)
                    if m:
                        pfx = m.group(1)
                
                    # Strip CQ zone overrides.
                    m = cq_override_re.search(pfx)
                    if m:
                        pfx = m.group(1)
                    
                    # Strip continent overrides.
                    m = continent_override_re.search(pfx)
                    if m:
                        pfx = m.group(1)
                    
                    # Strip GMT offset overrides.
                    m = tz_override_re.search(pfx)
                    if m:
                        pfx = m.group(1)
                    
                    # Specific callsigns start with an equals sign (=).
                    if (pfx.startswith("=")):
                        self._add_callsign(pfx.strip("=").upper(), country)
                    else:
                        # Add the prefix.
                        if len(pfx) > 0:
                            self._add_pfx(pfx.upper(), country)
                
            # If line does not start with a space, then it contains DXCC country data.
            else:
                dxcc_data = line.strip().split(":")
                country = self.get_entity(str(dxcc_data[0]))
                self._data[country] = [str(dxcc_data[1]).strip(), str(dxcc_data[2]).strip(), str(dxcc_data[3]).strip().upper()]
            
        cty_in.close()
        
        # Build the prefix metadata lists.
        self._make_pfx_meta()
        
        # Perform a secondary alphanumeric sort of the prefix data.
        self._sort_pfx_byalpha()

    #--------------------------------------------------------------------------
    def import_dxcc_csv(self, dxcc_csv_file):
        """
        Import a DXCC CSV file and use it for DXCC entity processing.
        The DXCC CSV file fields are as follows:
        Entity Code, Entity Name, Deleted (Y/N), Alternate Name
        
        Call this function BEFORE calling import_cty_dat().
        """
        if self.Verbose:
            self._print_msg('Importing ' + dxcc_csv_file)
        try:
            csv_in = codecs.open(dxcc_csv_file, mode='r', encoding='utf-8', errors='ignore')
        except Exception as e:
            if self.Verbose:
                self._print_msg(str(e))
            return -1
            
        for line in csv_in:
            data = self.make_utf8(line).strip().split(',')
            entity = str(data[1])
            if len(entity):
                self._dxcc_entity[entity] = [str(data[0]), str(data[2]), str(data[3]).strip().upper()]
        
        csv_in.close()

    #--------------------------------------------------------------------------
    def make_utf8(self, string_in):
        """
        Ensure a string is encoded as UTF-8.

        Special characters that can't be converted to UTF-8 are ignored and dropped
        from the string.
        """
        enc_in = locale.getpreferredencoding()
        return string_in.encode(enc_in, 'ignore').decode('utf-8', 'ignore')   


###############################################################################
# End of dxentity class.
###############################################################################
        
###############################################################################
# Main program test script.
###############################################################################            
if __name__ == "__main__":
    
    myDXentity = dxentity(True)
    myDXentity.import_dxcc_csv("dxcc_entity.csv")  # Always import this first
    myDXentity.import_cty_dat("cty.dat")
    myDXentity.dump_callsigns("callsigns.txt")
    myDXentity.dump_prefixes("prefixes.txt")
    
    f_in  = open("dxentity_test_callsigns.txt", 'r')
    f_out = open("dxentity_test_results.txt", 'w')
    for line in f_in:
        if line.startswith("#"): continue
        callsign = line.strip()
        if len(callsign) > 0:
            country = myDXentity.get_country(callsign)
            if len(country) > 0:
                f_out.write(callsign + "," + country + "\n")
            else:
                msg = "*** No country for " + callsign + " ***"
                f_out.write(msg + "\n")
                print(msg)
        
    f_in.close()
    f_out.close()
    sys.exit(0)
    
# End of file.
