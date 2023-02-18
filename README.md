# AB3GY dxentity database
Amateur radio DXCC entity processing module.

Provides methods for associating callsigns with DXCC entity countries.
 
Typical usage is to import a cty.dat file using i`mport_cty_dat()`, then use calls to `get_country()` to return a country name string for callsigns of interest. 

`dump_callsigns()` and `dump_prefixes()` will print the unique callsigns and callsign prefixes obtained from a source cty.dat to stdout or a file.  Data is in CSV format.

`cty.dat` is a standard DXCC entity database file that is used by many amateur radio programs for associating a callsign with a DXCC entity.

A good reference can be found here: http://www.country-files.com

A format reference can be found here:  http://www.country-files.com/cty-dat-format

Developed for personal use by the author, but available to anyone under the license terms below.

### **_This is very much still a work in process._** ###

## Dependencies
Written for Python 3.x.

This package has been tested on Windows 10 PCs. Other operating systems have not been tested.
 
## Author
Tom Kerr AB3GY
ab3gy@arrl.net

## License
Released under the 3-clause BSD license.
See license.txt for details.
