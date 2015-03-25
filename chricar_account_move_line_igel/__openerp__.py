# -*- coding: utf-8 -*-
{ 'sequence': 500,
"name"         : "Account Moves Igel"
, "version"      : "1.0"
, "author"       : "ChriCar Beteiligungs- und Beratungs- GmbH"
, "website"      : "http://www.chricar.at"
, "description"  : """Import table for account move lines of Igel"""
, "category"     : "Client Modules/ChriCar Addons"
, "depends"      : ["account"]
, "init_xml"     : []
, "demo"         : []
, "data"   :
[ "account_move_line_igel_view.xml"
, "wizard/moves_igel_view.xml"
, "security/rule.xml","security/ir.model.access.csv"
]
, "auto_install" : False
, 'installable': False
, 'application'  : False
}
