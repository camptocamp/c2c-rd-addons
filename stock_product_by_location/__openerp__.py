{ 'sequence': 500,
"name"         : "Product by Stock Location"
, "version"      : "1.0"
, "author"       : "ChriCar Beteiligungs- und Beratungs- GmbH"
, "website"      : "http://www.camptocamp.com"
, "description"  : """Shows quantity and amount of products per stock location"""
, "category"     : "Warehouse Management"
, "depends"      : ["stock"]
, "init_xml"     : []
, "demo"         : []
, "data"   : 
[ "stock_product_by_location_view.xml"
, "security/ir.model.access.csv"
]
, "auto_install" : False
, 'installable': False
, 'application'  : False
}
