# -*- coding: utf-8 -*-
{ "name"         : "Timesheet encode tasks"
, "version"      : "1.0"
, "author"       : "Camptocamp Austria"
, "website"      : "http://www.camptocamp.at"
, "description"  : """
 Allows to enter work by task on daily basis timesheets
 Analysis of work of today, yesterday, this month, last month, 
 also grouped by projects
 """
 , "category"     : "Generic Modules/Human Resources"
 , "depends"      : ["base","project","project_timesheet"]
 , "init_xml"     : []
 , "demo"         : []
 , "update_xml"   : ["timesheet_task_view.xml"]
 , "auto_install" : False
 , "installable"  : True
, 'application'  : False
}

