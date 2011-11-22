# -*- coding: utf-8 -*-
{
     "name"         : "Account Moves Deloitte",
     "version"      : "1.0",
     "author"       : "ChriCar Beteiligungs- und Beratungs GmbH",
     "website"      : "http://www.chricar.at",
     "description"  : """Import table for account move lines of Deloitte
generated 2009-10-17 12:10:57+02""",
     "category"     : "Client Modules/ChriCar Addons",
     "depends"      : ["base","account"],
     "init_xml"     : [],
     "demo_xml"     : [],
     "update_xml"   : ["account_move_line_deloitte_view.xml","security/rule.xml","security/ir.model.access.csv"],
     "active"       : False,
     "installable"  : True
}

