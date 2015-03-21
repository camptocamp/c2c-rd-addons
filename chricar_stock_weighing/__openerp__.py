# -*- coding: utf-8 -*-
{ 'sequence': 500,
"name"         : "Stock Weighing"
, "version"      : "1.0"
, "author"       : "ChriCar Beteiligungs- und Beratungs- GmbH"
, "website"      : "http://www.chricar.at"
, "description"  : """Stock Weighing

Extension to carrier

    * allows to records weights of the vehicle, etc.

Extension to Production

    * allows simplified data entry for harvest
    * quality attributes for stock_moves
"""
, "category"     : "Client Modules/Farm"
, "depends"      : ["stock", "mrp", "delivery", "mrp_reopen","chricar_stock_care"]
, "init_xml"     : []
, "demo"         : []
, "data"   :
[ "stock_weighing_view.xml"
, "mrp_view.xml"
, "mrp_workflow.xml"
, "stock_report.xml"
]
, "auto_install" : False
, 'installable': False
, 'application'  : False
}
