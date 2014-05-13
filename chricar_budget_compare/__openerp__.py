# -*- coding: utf-8 -*-
{ "name"         : "Budget Products"
, "version"      : "1.0"
, "author"       : "Camptocamp"
, "website"      : "http://www.camptocamp.com"
, "description"  : """Allows to compare current and previous budgets with current and previous real

ToDo
 
 * make multicompany ready - budget items and/or budget lines need company_id
 """
 , "category"     : "Client Modules/ChriCar Addons"
 , "depends"      : ["product","chricar_view_id","c2c_budget"]
 , "init_xml"     : []
 , "demo_xml"     : []
 , "update_xml"   : ["budget_update.xml","security/ir.model.access.csv"]
 , "auto_install" : False
 , "installable"  : True
}
