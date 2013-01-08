# -*- coding: utf-8 -*-
{ "name"         : "Real Estate Top"
, "version"      : "1.0"
, "author"       : "Camptocamp"
, "website"      : "http://www.camptocamp.com"
, "description"  : """defines the top (inherits location)
generated 2009-07-09 16:17:22+02"""
, "category"     : "Client Modules/Real Estate"
, "depends"      : 
    [ "product"
    , "stock"
    , "chricar_partner_parent_companies"
    , "crm_helpdesk"
    ]
, "init_xml"     : ["mig_top_init.xml"]
, "demo_xml"     : []
, "update_xml"   : ["security/group.xml","top_view.xml","location_income_tax_view.xml","report_webkit.xml","security/ir.model.access.csv"]
, "auto_install" : False
, "installable"  : True
}
