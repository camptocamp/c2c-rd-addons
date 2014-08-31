# -*- coding: utf-8 -*-
{ "name"         : "Account Moves ISM"
, "version"      : "1.0"
, "author"       : "ChriCar Beteiligungs- und Beratungs GmbH"
, "website"      : "http://www.chricar.at"
, "description"  : """Import table for account move lines of Deloitte"""
, "category"     : "Client Modules/ChriCar Addons"
, "depends"      : ["account","one2many_sorted"]
, "init_xml"     : []
, "demo_xml"     : []
, "update_xml"   : 
    [ "account_move_line_ism_view.xml"
    , "security/rule.xml","security/ir.model.access.csv"
    ]
, "auto_install" : False
, "installable"  : True
}

