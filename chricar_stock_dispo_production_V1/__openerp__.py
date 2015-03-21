{ 'sequence': 500,
"name"         : "Dispo Production"
, "version"      : "1.0"
, "author"       : "ChriCar Beteiligungs- und Beratungs- GmbH"
, "website"      : "http://www.chricar.at"
, "description"  : """Dispo Production
generated 2010-04-02 15:01:02+02"""
, "category"     : "Client Modules/Farm"
, "depends"      : ["sale","stock", "one2many_sorted","c2c_stock_accounting", "c2c_product_price_unit"]
, "init_xml"     : ["mig_stock_dispo_production_init.xml"]
, "demo"         : []
, "data"   :
[ "stock_dispo_production_view.xml"
, "stock_prod_lot_update.xml"
]
, "auto_install" : False
, 'installable': False
, 'application'  : False
}
