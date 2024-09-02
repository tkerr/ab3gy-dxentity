##############################################################################
# db_schema.py
#
# Data objects used to manage the dxentity database schema.
##############################################################################

import os
import sys

##############################################################################
# Globals.
##############################################################################

def get_database_name():
    for path in sys.path:
        db = os.path.join(path, 'dxentity.sqlite3')
        if os.path.isfile(db):
            return db
    return ''

DATABASE_NAME = get_database_name()

# ----------------------------------------------------------------------------
# Entity table.
# Lookup DXCC and country name in the country table using the PRIORITY field.
TABLE_ENTITY = 'tbl_entity'

TABLE_ENTITY_COLUMNS = [
    'ID INTEGER PRIMARY KEY AUTOINCREMENT',
    'TYPE TEXT',                  # "ENTITY" or "ALIAS"
    'PRIORITY INTEGER DEFAULT 0', # The cty.dat priority search order (ORDER is a reserved keyword)
    'ENTITY TEXT',                # The primary entity prefix from cty.dat
    'ALIAS TEXT',                 # The alias entity prefix from cty.dat
    'SUFFIX TEXT',                # The primary entity suffix from cty.dat
    'CQZONE INTEGER DEFAULT 0',
    'ITUZONE INTEGER DEFAULT 0',
    'CONT CHARACTER(2)',
    'LAT REAL DEFAULT 0',
    'LON REAL DEFAULT 0',
    'GMTOFFSET INTEGER DEFAULT 0',
    'WAEDC INTEGER DEFAULT 0',
]

TABLE_ENTITY_UNIQUE = [
]

# ----------------------------------------------------------------------------
# Callsign table for exact callsign matches.
# Lookup DXCC and country name in the country table using the PRIORITY field.
TABLE_CALLSIGN = 'tbl_callsign'

TABLE_CALLSIGN_COLUMNS = [
    'ID INTEGER PRIMARY KEY AUTOINCREMENT',
    'CALLSIGN TEXT',               # Callsign for exact match (may not be unique)
    'TYPE TEXT',                   # Always "CALLSIGN"
    'PRIORITY INTEGER DEFAULT 0',  # The cty.dat priority search order (ORDER is a reserved keyword)
    'ENTITY TEXT',                 # The primary entity prefix from cty.dat
    'SUFFIX TEXT',                 # The primary entity suffix from cty.dat
    'CQZONE INTEGER DEFAULT 0',
    'ITUZONE INTEGER DEFAULT 0',
    'CONT CHARACTER(2)',
    'LAT REAL DEFAULT 0',
    'LON REAL DEFAULT 0',
    'GMTOFFSET INTEGER DEFAULT 0',
    'WAEDC INTEGER DEFAULT 0',
]

TABLE_CALLSIGN_UNIQUE = [
]

# ----------------------------------------------------------------------------
# Country table.
# PRIORITY field is unique and used to match DXCC and country to the callsign.
TABLE_COUNTRY = 'tbl_country'

TABLE_COUNTRY_COLUMNS = [
    'PRIORITY INTEGER PRIMARY KEY', # The unique entity search priority order used as a primary key
    'DXCC INTEGER DEFAULT 0',       # DXCC number for the country (may not be unique)
    'ENTITY TEXT',                  # The primary entity prefix from cty.dat
    'COUNTRY TEXT',                 # The country name from cty.dat
]

TABLE_COUNTRY_UNIQUE = [
]
