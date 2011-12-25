# -*- coding: utf-8 -*-
{
     "name"         : "Autosearch Check",
     "version"      : "1.0",
     "author"       : "Camptocamp Austria",
     "website"      : "http://www.camptocamp.at",
     "description"  : """ 
     This module checks if number of table resources is large and turns autosearch off
     The default is 80 records (~2 screenfull)
     in most other cases it makes more sense to allow to enter a query before quering the table
     once installed, this check will run periodically and turn off autosearch for ir_act_window where auto_search_check is true
     """,
     "category"     : "Generic Modules/Base",
     "depends"      : ["base"],
     "init_xml"     : [],
     "demo_xml"     : [],
     "update_xml"   : ["autosearch_view.xml"],
     "active"       : False,
     "installable"  : True
}

