# -*- coding: utf-8 -*-
{ 'sequence': 500,
"name"         : "Account Moves Deloitte"
, "version"      : "1.0"
, "author"       : "ChriCar Beteiligungs- und Beratungs- GmbH"
, "website"      : "http://www.chricar.at"
, "description"  : """Import table for account move lines of Deloitte and other accounting systems
generated 2009-10-17 12:10:57+02"""
, "category"     : "Client Modules/ChriCar Addons"
, "depends"      : ["account"]
, "init_xml"     : []
, "demo"         : []
, "data"   :
[ "account_move_line_deloitte_view.xml"
, "wizard/moves_deloitte_view.xml"
, "wizard/move_deloitte_delete.xml"
, "security/rule.xml","security/ir.model.access.csv"
]
, "auto_install" : False
, 'installable': False
, 'application'  : False
}
