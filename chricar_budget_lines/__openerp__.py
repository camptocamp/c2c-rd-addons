# -*- coding: utf-8 -*-
{ 'sequence': 500,
"name"         : "Budget Products Lines"
, "version"      : "1.0"
, "author"       : "ChriCar Beteiligungs- und Beratungs- GmbH"
, "website"      : "http://www.chricar.at"
, "description"  : """Allows to plan details for product budgets
generated 2009-08-21 15:12:07+02"""
, "category"     : "Client Modules/ChriCar Addons"
, "depends"      : 
[ "chricar_budget"
, "mrp"
, "stock"
, "account"
, "chricar_view_id"
, "chricar_partner_parent_companies"
, "c2c_product_price_unit"
]
, "init_xml"     : []
, "demo"         : []
, "data"   : ["budget_lines_view.xml"]
, "auto_install" : False
, 'installable': False
, 'application'  : False
}
