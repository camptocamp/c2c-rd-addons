{ "name"         : "Dispo Production"
, "version"      : "1.0"
, "author"       : "ChriCar Beteiligungs- und Beratungs- GmbH"
, "website"      : "http://www.chricar.at"
, "description"  : """Dispo Production
generated 2010-04-02 15:01:02+02"""
, "category"     : "Client Modules/Farm"
, "depends"      : ["sale","stock"]
, "init_xml"     : ["mig_stock_dispo_production_init.xml"]
, "demo_xml"     : []
, "update_xml"   : 
    [ "stock_dispo_production_view.xml"
    , "stock_prod_lot_update.xml"
    ]
, "auto_install" : False
, "installable"  : True
}
