{ 'sequence': 500,
"name"         : "Tenant"
, "version"      : "1.0"
, "author"       : "ChriCar Beteiligungs- und Beratungs- GmbH"
, "website"      : "http://www.chricar.at/ChriCar"
, "description"  : """defines the tenant
generated 2009-07-09 18:08:09+02"""
, "category"     : "Client Modules/Real Estate"
, "depends"      : ["chricar_top"]
, "init_xml"     : ["mig_tenant_init.xml", "security/ir.model.access.csv"]
, "demo"         : []
, "data"   : ["tenant_view.xml"]
, "auto_install" : False
, 'installable': False
, 'application'  : False
}
