# -*- coding: utf-8 -*-
{ "name"         : "Product by Stock "
, "version"      : "1.0"
, "author"       : "Camptocamp Austria"
, "website"      : "http://www.camptocamp.com"
, "description"  : """Shows quantity and amount of products per production location"""
, "category"     : "Warehouse Management"
, "depends"      : 
    [ "account"
    , "product"
    , "stock"
    , "chricar_view_id"
    , "c2c_stock_extension"
    , "c2c_stock_accounting"
    , "chricar_stock_dispo_production_V1"
    ]
, "init_xml"     : []
, "demo"         : []
, "update_xml"   : ["stock_product_production_view.xml"]
, "auto_install" : False
, "installable"  : True
}
