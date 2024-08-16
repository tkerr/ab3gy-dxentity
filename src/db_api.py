##############################################################################
# db_api.py
#
# Application Program Interface (API) class for the dxentity database.
##############################################################################

import os
import sqlite3

# Local packages.
import db_schema as schema

##############################################################################
# Globals.
##############################################################################


##############################################################################
# Functions.
##############################################################################


##############################################################################
# API class.
##############################################################################
class db_api(object):
    """
    Application Program Interface (API) class for the dxentity database. 
    """

    # ------------------------------------------------------------------------
    def __init__(self, db=schema.DATABASE_NAME):
        """
        Class constructor.
        Parameters:
            db (str): Full pathname of database. Provides a default if not specified.
        Returns:
            None
        """
        self.connection = sqlite3.connect(db)
        # This will cause results to be returned as row objects with column
        # names included. However, each row must be converted to a dictionary.
        # See _row2dict().
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    # ------------------------------------------------------------------------
    def __del__(self):
        """
        Class destructor.
        """
        self.cursor.close()
        self.connection.close()

    # ------------------------------------------------------------------------
    def _last_rowid(self):
        """
        Return the ID of the last inserted row.
        """
        sql = 'SELECT last_insert_rowid()'
        data = ()
        self.cursor.execute(sql, data)
        result_set = self.cursor.fetchall()
        rowid = self._row2dict(result_set)[0]['last_insert_rowid()']
        return rowid
    
    # ------------------------------------------------------------------------
    def _query_select(self, sql, data):
        """
        Common method to perform a SQL SELECT query.
        Parameters:
            sql (str): The SQL SELECT string to execute.
            data (tuple): A tuple of data values for the select query.
        Returns:
            A list of results, either as dictionaries or tuples.
        """
        result_list = []
        try:
            self.cursor.execute(sql, data)
            result_set = self.cursor.fetchall()
            result_list = self._row2dict(result_set)
        except Exception as e:
            e_name = type(e).__name__
            err_msg = 'SQL SELECT error: {}: {}\n'.format(e_name, str(e))
            err_msg += '  SQL:  "{}"\n'.format(sql)
            err_msg += '  Data: "{}"'.format(data)
            print(err_msg)
        return result_list

    # ------------------------------------------------------------------------
    def _row2dict(self, row_object):
        """
        Convert a row object to a list of dictionaries.
        """
        row_list = []
        for row in row_object:
            row_list.append(dict(row))
        return row_list
    
    
    # ------------------------------------------------------------------------
    def _add_country(self, result_list):
        """
        Add DXCC and country to a result list.
        """
        sql = 'SELECT DXCC,COUNTRY FROM {} WHERE PRIORITY=?'.format(schema.TABLE_COUNTRY)
        for result in result_list:
            data = (result['PRIORITY'],)
            country_list = self._query_select(sql, data)
            if (len(country_list) > 0):
                result['DXCC'] = country_list[0]['DXCC']
                result['COUNTRY'] = country_list[0]['COUNTRY']
        return result_list

    # ------------------------------------------------------------------------
    def callsign_row_insert(self, entry):
        """
        Insert a row into the callsign table.
        Parameters:
            entry (dict): A dictionary of row data defined by blank_entity in parse_cty.py.
        Returns:
            A tuple of (status, rowid)
            status = True if successful, False otherwise.
            rowid = ID of inserted row if successful, -1 otherwise.
        """
        sql = 'INSERT INTO {}('.format(schema.TABLE_CALLSIGN)
        sql += 'CALLSIGN, TYPE, PRIORITY, ENTITY, CQZONE, ITUZONE, CONT, LAT, LON, GMTOFFSET, WAEDC) '
        sql += 'VALUES(?,?,?,?,?,?,?,?,?,?,?)'
        data = (entry['ALIAS'], 'CALLSIGN', entry['ORDER'], entry['ENTITY'], entry['CQ_ZONE'], entry['ITU_ZONE'], \
            entry['CONT'], entry['LAT'], entry['LON'], entry['GMT_OFFSET'], entry['WAEDC'])
        try:
            self.cursor.execute(sql, data)
            self.connection.commit()
            rowid = self._last_rowid()
            return (True, rowid)
        except Exception as e:
            e_name = type(e).__name__
            err_msg = 'Data insert error: {}: {}\n'.format(e_name, str(e))
            err_msg += '  SQL:  "{}"\n'.format(sql)
            err_msg += '  Data: "{}"'.format(data)
            print(err_msg)
            return (False, -1)

    # ------------------------------------------------------------------------
    def country_row_insert(self, entry):
        """
        Insert a row into the country table.
        Parameters:
            entry (dict): A dictionary of row data defined by blank_entity in parse_cty.py.
        Returns:
            A tuple of (status, rowid)
            status = True if successful, False otherwise.
            rowid = ID of inserted row if successful, -1 otherwise.
        """
        sql = 'INSERT INTO {}('.format(schema.TABLE_COUNTRY)
        sql += 'PRIORITY, DXCC, ENTITY, COUNTRY) '
        sql += 'VALUES(?,?,?,?)'
        data = (entry['ORDER'], entry['DXCC'], entry['ENTITY'], entry['COUNTRY'])
        try:
            self.cursor.execute(sql, data)
            self.connection.commit()
            rowid = self._last_rowid()
            return (True, rowid)
        except Exception as e:
            e_name = type(e).__name__
            err_msg = 'Data insert error: {}: {}\n'.format(e_name, str(e))
            err_msg += '  SQL:  "{}"\n'.format(sql)
            err_msg += '  Data: "{}"'.format(data)
            print(err_msg)
            return (False, -1)

    # ------------------------------------------------------------------------
    def entity_row_insert(self, entry):
        """
        Insert a row into the entity table.
        Parameters:
            entry (dict): A dictionary of row data defined by blank_entity in parse_cty.py.
        Returns:
            A tuple of (status, rowid)
            status = True if successful, False otherwise.
            rowid = ID of inserted row if successful, -1 otherwise.
        """
        sql = 'INSERT INTO {}('.format(schema.TABLE_ENTITY)
        sql += 'TYPE, PRIORITY, ENTITY, ALIAS, SUFFIX, CQZONE, ITUZONE, CONT, LAT, LON, GMTOFFSET, WAEDC) '
        sql += 'VALUES(?,?,?,?,?,?,?,?,?,?,?,?)'
        data = (entry['TYPE'], entry['ORDER'], entry['ENTITY'], entry['ALIAS'], entry['SUFFIX'], \
            entry['CQ_ZONE'], entry['ITU_ZONE'], entry['CONT'], entry['LAT'], entry['LON'], \
            entry['GMT_OFFSET'], entry['WAEDC'])
        try:
            self.cursor.execute(sql, data)
            self.connection.commit()
            rowid = self._last_rowid()
            return (True, rowid)
        except Exception as e:
            e_name = type(e).__name__
            err_msg = 'Data insert error: {}: {}\n'.format(e_name, str(e))
            err_msg += '  SQL:  "{}"\n'.format(sql)
            err_msg += '  Data: "{}"'.format(data)
            print(err_msg)
            return (False, -1)
    
    # ------------------------------------------------------------------------
    def import_data(self, cty_list):
        """
        Import data from lists of data records.
        Parameters:
            cty_list (list): List of dictionaries containing cty.dat entity data.
                Dictionary format is defined by blank_entity in parse_cty.py.
        Returns:
            A tuple of (good_count, bad_count)
            good_count (int): Count of successful record inserts
            bad_count (int): Count of failed record inserts
        """
        good_count = 0
        bad_count = 0
        country_list = []
        for entry in cty_list:
            etype = entry['TYPE']           
            if (etype == 'ENTITY'):
                (status, rowid) = self.entity_row_insert(entry)
                if status:
                    good_count += 1
                else:
                    bad_count += 1
                (status, rowid) = self.country_row_insert(entry)
                if status:
                    good_count += 1
                else:
                    bad_count += 1
            elif (etype == 'ALIAS'):
                (status, rowid) = self.entity_row_insert(entry)
                if status:
                    good_count += 1
                else:
                    bad_count += 1
            elif (etype == 'CALLSIGN'):
                (status, rowid) = self.callsign_row_insert(entry)
                if status:
                    good_count += 1
                else:
                    bad_count += 1
        return (good_count, bad_count)

    # ------------------------------------------------------------------------
    def get_version(self):
        """
        Get the cty.dat version.
        Parameters:
            None
        Returns:
            A tuple of (entity, country) corresponding to the VERSION callsign
            in the cty.dat database.
        """
        result_list = self.select_callsign('VERSION', country=True)
        if (len(result_list) > 0):
            version = (result_list[0]['ENTITY'], result_list[0]['COUNTRY'])
        else:
            version = ('','')
        return version
    
    # ------------------------------------------------------------------------
    def select_alias(self, alias, country=True):
        """
        Return the data record corresponding to the specified alias (or entity).
        Must be an exact match in the entity table.
        Parameters:
            alias (str): The alias to select.
            country (bool): If True, then country and DXCC number are included.
        Returns:
            Data record as a list of zero or more matching dictionaries.
        """
        result_list = []
        sql = 'SELECT * FROM {} WHERE ALIAS=? ORDER BY PRIORITY ASC'.format(
            schema.TABLE_ENTITY)
        data = (alias.upper(),)
        result_list = self._query_select(sql, data)
        if country:
            result_list = self._add_country(result_list)
        return result_list

    # ------------------------------------------------------------------------
    def select_callsign(self, callsign, country=True):
        """
        Return the data record corresponding to the specified callsign.
        Must be an exact match in the callsign table.
        Parameters:
            callsign (str): The exact callsign to select.
            country (bool): If True, then country and DXCC number are included.
        Returns:
            Data record as a list of zero or more matching dictionaries.
        """
        result_list = []
        sql = 'SELECT * FROM {} WHERE CALLSIGN=? ORDER BY PRIORITY ASC'.format(
            schema.TABLE_CALLSIGN)
        data = (callsign.upper(),)
        result_list = self._query_select(sql, data)
        if country:
            result_list = self._add_country(result_list)
        return result_list
    
    # ------------------------------------------------------------------------
    def select_country(self, country):
        """
        Return the data record corresponding to the specified country.
        Performs a pattern match containing the specified country string.
        Parameters:
            country (str): The country to select.
        Returns:
            Data record as a list of zero or more matching dictionaries.
        """
        result_list = []
        sql = 'SELECT * FROM {} WHERE COUNTRY LIKE ? ORDER BY PRIORITY ASC'.format(
            schema.TABLE_COUNTRY)
        try:
            data = ('%{}%'.format(country),)
            result_list = self._query_select(sql, data)
        except Exception as err:
            print('Select country error: {}'.format(str(err)))
        return result_list
    
    # ------------------------------------------------------------------------
    def select_dxcc(self, dxcc):
        """
        Return the data record corresponding to the specified DXCC number.
        Parameters:
            dxcc (int/str): The DXCC number to select.
        Returns:
            Data record as a list of zero or more matching dictionaries.
        """
        result_list = []
        sql = 'SELECT * FROM {} WHERE DXCC=? ORDER BY PRIORITY ASC'.format(
            schema.TABLE_COUNTRY)
        try:
            data = (int(dxcc),)
            result_list = self._query_select(sql, data)
        except Exception as err:
            print('Select DXCC error: {}'.format(str(err)))
        return result_list
    
    # ------------------------------------------------------------------------
    def select_entity(self, entity, country=True):
        """
        Return the data record corresponding to the specified entity.
        Must be an exact match in the entity table.
        Parameters:
            entity (str): The entity to select.
            country (bool): If True, then country and DXCC number are included.
        Returns:
            Data record as a list of zero or more matching dictionaries.
            Should return at most one result from a correctly provisioned database.
        """
        result_list = []
        sql = 'SELECT * FROM {} WHERE ENTITY=? AND TYPE=? ORDER BY PRIORITY ASC'.format(
            schema.TABLE_ENTITY)
        data = (entity.upper(),'ENTITY')
        result_list = self._query_select(sql, data)
        if country:
            sql = 'SELECT DXCC,COUNTRY FROM {} WHERE PRIORITY=?'.format(
                schema.TABLE_COUNTRY)
            for result in result_list:
                data = (result['PRIORITY'],)
                country_list = self._query_select(sql, data)
                if (len(country_list) > 0):
                    result['DXCC'] = country_list[0]['DXCC']
                    result['COUNTRY'] = country_list[0]['COUNTRY']
        return result_list
    
    # ------------------------------------------------------------------------
    def dump_database(self):
        """
        Return every entity, alias and callsign in the database.
        Parameters:
            None
        Returns:
            Data records as a list of zero or more dictionaries.
        """
        sql = 'SELECT * FROM {} ORDER BY PRIORITY ASC'.format(schema.TABLE_ENTITY)
        data = ()
        entity_list = self._query_select(sql, data)
        entity_list = self._add_country(entity_list)
        sql = 'SELECT * FROM {} ORDER BY PRIORITY ASC'.format(schema.TABLE_CALLSIGN)
        callsign_list = self._query_select(sql, data)
        callsign_list = self._add_country(callsign_list)
        return entity_list + callsign_list


##############################################################################
# Main program.
############################################################################## 
if __name__ == "__main__":
    import sys
    print('{} main program called'.format(os.path.basename(sys.argv[0])))
    
    