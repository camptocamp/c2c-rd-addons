{ "name"         : "Product by Stock "
, "version"      : "1.0"
, "author"       : "Camptocamp"
, "website"      : "http://www.camptocamp.com"
, "description"  : """Shows quantity and amount of products per stock location
generated 2009-09-19 23:51:03+02"""
, "category"     : "Warehouse Management"
, "depends"      : 
    [ "c2c_stock_accounting"
    ]
, "init_xml"     : []
, "demo_xml"     : []
, "update_xml"   : 
    [ "stock_product_by_location_view.xml"
    , "security/ir.model.access.csv"
    ]
, "auto_install" : False
, "installable"  : True
}
