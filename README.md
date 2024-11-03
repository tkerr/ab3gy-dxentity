# AB3GY dxentity database
Python amateur radio DXCC entity processing module.  
Provides functions for associating callsigns with DXCC entity countries.  

Uses a sqlite database created from a cty.dat file and other optional data.  
Searches the database with a supplied callsign to retrieve DX related info 
such as country name, DXCC number, CQ zone, ITU zone, etc.

cty.dat is maintained by Jim Reisert A1DC and can be found here: http://www.country-files.com  
A format reference can be found here:  http://www.country-files.com/cty-dat-format  

Developed for personal use by the author, but available to anyone under the license terms below.  

The current sqlite database was created from **CTY-3436 (San Felix & San Ambrosio, CE0X)**  

## Example Use

```
import dxentity

# Get the country only
country = dxentity.get_country('AB3GY')
print(country)

# Output:  
United States  
```

```
# Get a DX info tuple
(entity, cont, cqzone, ituzone, dxcc, country) = dxentity.get_dx_info('AB3GY')
print(entity, cont, cqzone, ituzone, dxcc, country)

# Output:  
K NA 5 8 291 United States   
```

```
# Operating in a different country
(entity, cont, cqzone, ituzone, dxcc, country) = dxentity.get_dx_info('HB0/AB3GY')
print(entity, cont, cqzone, ituzone, dxcc, country)

Output:  
HB0 EU 14 28 251 Liechtenstein  
```

```
# Get the current database version
(entity, cont, cqzone, ituzone, dxcc, country) = dxentity.get_dx_info('VERSION')
print(entity, cont, cqzone, ituzone, dxcc, country)

# Output:   
CN AF 33 37 446 Morocco  
```

### Database Setup
Use the `db_utils.py` application to import a new cty.dat file and create a sqlite database:
```
python db_utils.py 4 ./cty/cty.dat ./cty/dxcc_list.csv  
```
Custom aliases and callsigns can be added from a CSV file:
```
python db_utils.py 5 ./cty/custom_alias.csv  
```

Use the `cty_utils.py` application to check a new cty.dat file:
```
python cty_utils.py 7 ./cty/cty.dat ./cty/dxcc_list.csv  
```

Run each script with no parameters to see help text.  

 
## Author
Tom Kerr AB3GY
ab3gy@arrl.net

## License
The files maintained in the repository are released under the 3-clause BSD license.
See license.txt for details.  
cty.dat copyright can be found here: https://www.country-files.com/copyright  
