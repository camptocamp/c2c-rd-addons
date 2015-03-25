# -*- coding: utf-8 -*-
{ 'sequence': 500,
"name"         : "Timesheet encode tasks"
, "version"      : "1.0"
, "author"       : "ChriCar Beteiligungs- und Beratungs- GmbH"
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
, "data"   : ["timesheet_task_view.xml"]
, "auto_install" : False
, 'installable': True
, 'application'  : False
}

