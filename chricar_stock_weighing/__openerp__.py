# -*- coding: utf-8 -*-
{ "name"         : "Stock Weighing"
, "version"      : "1.0"
, "author"       : "Camptocamp"
, "website"      : "http://www.camptocamp.com"
, "description"  : """Stock Weighing

Extension to carrier

 * allows to records weights of the vehicle, etc.

Extension to Production

 * allows simplified data entry for harvest
 * quality attributes for stock_moves
 """
, "category"     : "Client Modules/Farm"
, "depends"      : ["stock", "mrp", "delivery", "c2c_sale_multi_partner","mrp_reopen"]
, "init_xml"     : []
, "demo_xml"     : []
, "update_xml"   : 
    [ "stock_weighing_view.xml"
    , "mrp_view.xml"
    , "mrp_workflow.xml"
    , "stock_report.xml"
    ]
, "auto_install" : False
, "installable"  : True
}
