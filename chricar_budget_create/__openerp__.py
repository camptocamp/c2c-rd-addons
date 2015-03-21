# -*- coding: utf-8 -*-
{ 'sequence': 500,
"name"         : "Budget Create"
, "version"      : "1.0"
, "author"       : "ChriCar Beteiligungs- und Beratungs- GmbH"
, "website"      : "http://www.chricar.at/ChriCar"
, "description"  : """
Create budget lines derived from account_move_lines of previous periods.
This is helpful for planning fixed costs and often a good starting point 
for variable costs and revenues.
The budget items can, but must not be identical to accounts.
On demand missing budget items are created with the same structure than accounts.
Usually the budget must be created before the year ends. Therefore the source 
periods may overlap (Example use month Oct 2010 to Sept 2011 as basis for 2012)
"""
, "category"     : "Accounting & Finance"
, "depends"      : ["chricar_budget_lines"]
, "init_xml"     : []
, "demo"         : []
, "data"   : ["budget_view.xml","wizard/budget_create_view.xml"]
, "auto_install" : False
, 'installable': False
, 'application'  : False
}
