# -*- coding: utf-8 -*-
{ 'sequence': 500,
"name"         : "Budget Products"
, "version"      : "1.0"
, "author"       : "ChriCar Beteiligungs- und Beratungs- GmbH"
, "website"      : "http://www.chricar.at/ChriCar"
, "description"  : """Allows to compare current and previous budgets with current and previous real

ToDo

    * make multicompany ready - budget items and/or budget lines need company_id
"""
, "category"     : "Client Modules/ChriCar Addons"
, "depends"      : ["product","chricar_view_id","c2c_budget_chricar"]
, "init_xml"     : []
, "demo"         : []
, "data"   : ["budget_update.xml","security/ir.model.access.csv"]
, "auto_install" : False
, 'installable': False
, 'application'  : False
}
