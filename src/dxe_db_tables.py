##############################################################################
# dxe_db_tables.py
#
# Create and manage tables for the dxentity database.
##############################################################################

# System level packages.
import os
from pathlib import Path
import sqlite3

# Local packages.
import dxe_db_schema as schema
from dxe_db_api import dxe_db_api


##############################################################################
# Globals.
############################################################################## 


##############################################################################
# Functions.
############################################################################## 

#-----------------------------------------------------------------------------
def delete_database():
    """
    Delete an existing dxentity database.
    Operation cannot be undone.
    Parameters:
        None
    Returns:
        True if successful, False otherwise
    """
    ok = False
    db_file = Path(schema.DATABASE_NAME)
    if db_file.exists():
        try:
            os.remove(schema.DATABASE_NAME)
            ok = True
        except Exception as err:
            print('Error deleting {}: {}'.format(schema.DATABASE_NAME, str(err)))
    else:
        ok = True
    return ok
    
#-----------------------------------------------------------------------------
def create_table(cursor, table, columns, unique=[]):
    """
    Create a database table and report errors.
    Parameters:
        cursor (sqlite3.Cursor): Cursor object used to execute SQL statements.
        table (str): The table name to create.
        columns (list): A list of column specifications for the table.  At least
            one column must be specified.
        unique (list): An optional list of unique columns.
    Returns:
        True if successful, False otherwise
    """
    column_spec = columns[0]
    for c in columns[1:]:
        column_spec += ', {}'.format(c)
    unique_spec = ''
    if (len(unique) > 0):
        unique_spec = ', UNIQUE({}'.format(unique[0])
        for u in unique[1:]:
            unique_spec += ',{}'.format(u)
        unique_spec += ')'
    sql = 'CREATE TABLE {}({}{})'.format(table, column_spec, unique_spec)
    try:
        cursor.execute(sql)
    except Exception as e:
        print('Create table "{}" error: {}'.format(table, str(e)))
        return False
    return True

#-----------------------------------------------------------------------------
def delete_table(cursor, table):
    """
    Delete a database table and report errors.
    Parameters:
        cursor (sqlite3.Cursor): Cursor object used to execute SQL statements.
        table (str): The table name to create.
    Returns:
        True if successful, False otherwise
    """
    sql = 'DROP TABLE IF EXISTS {}'.format(table)
    try:
        cursor.execute(sql)
    except Exception as e:
        print('Delete table "{}" error: {}'.format(table, str(e)))
        return False
    return True

#-----------------------------------------------------------------------------
def create_column(cursor, table, column_spec):
    """
    Create a table column and report errors.
    Parameters:
        cursor (sqlite3.Cursor): Cursor object used to execute SQL statements.
        table (str): The table to contain the column.
        column_spec (str): The column specification.
    Returns:
        True if successful, False otherwise
    """
    sql = 'ALTER TABLE {} ADD COLUMN {}'.format(table, column_spec)
    try:
        cursor.execute(sql)
    except Exception as e:
        print('Table "{}" add column error: {}'.format(table, str(e)))
        print('Column spec: "{}"'.format(column_spec))
        return False
    return True

#-----------------------------------------------------------------------------
def has_table(cursor, table):
    """
    Check if the specified table exists in the database.
    Parameters:
        cursor (sqlite3.Cursor): Cursor object used to execute SQL statements.
        table (str): The table name.
    Returns:
        True if table exists, False otherwise
    """
    found = False
    result_set = cursor.execute('PRAGMA table_list')
    for result in result_set:
        if (result[1] == table) and (result[2] == 'table'):
            found = True
            break
    return found

#-----------------------------------------------------------------------------
def create_entity_table():
    """
    Create the DXCC entity table.
    Parameters:
        None
    Returns:
        True if successful, False otherwise
    """
    ok = False
    api = dxe_db_api()
    table = schema.TABLE_ENTITY
    if (not has_table(api.cursor, table)):
        ok = create_table(
            api.cursor, 
            table, 
            schema.TABLE_ENTITY_COLUMNS,
            schema.TABLE_ENTITY_UNIQUE)
    else:
        print('Entity table exists, not created.')
    return ok

#-----------------------------------------------------------------------------
def create_callsign_table():
    """
    Create the callsign table for exact matches.
    Parameters:
        None
    Returns:
        True if successful, False otherwise
    """
    ok = False
    api = dxe_db_api()
    table = schema.TABLE_CALLSIGN
    if (not has_table(api.cursor, table)):
        ok = create_table(
            api.cursor, 
            table, 
            schema.TABLE_CALLSIGN_COLUMNS,
            schema.TABLE_CALLSIGN_UNIQUE)
    else:
        print('Callsign table exists, not created.')
    return ok

#-----------------------------------------------------------------------------
def create_country_table():
    """
    Create the country name table.
    Parameters:
        None
    Returns:
        True if successful, False otherwise
    """
    ok = False
    api = dxe_db_api()
    table = schema.TABLE_COUNTRY
    if (not has_table(api.cursor, table)):
        ok = create_table(
            api.cursor, 
            table, 
            schema.TABLE_COUNTRY_COLUMNS,
            schema.TABLE_COUNTRY_UNIQUE)
    else:
        print('Country table exists, not created.')
    return ok


##############################################################################
# Main program.
############################################################################## 
if __name__ == "__main__":
    import os
    import sys
    print('{} main program called'.format(os.path.basename(sys.argv[0])))
    
    