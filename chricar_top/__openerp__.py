# -*- coding: utf-8 -*-
{
     "name"         : "Real Estate Top",
     "version"      : "1.0",
     "author"       : "ChriCar Beteiligungs- und Beratungs- GmbH",
     "website"      : "http://www.chricar.at/ChriCar",
     "description"  : """defines the top (inherits location)
generated 2009-07-09 16:17:22+02""",
     "category"     : "Client Modules/Real Estate",
     "depends"      : ["base","product","stock","chricar_partner_parent_companies","crm_helpdesk"],
     "init_xml"     : ["mig_top_init.xml"],
     "demo_xml"     : [],
     "update_xml"   : ["top_view.xml","location_income_tax_view.xml","report_webkit.xml","security/group.xml","security/ir.model.access.csv"],
     "active"       : False,
     "installable"  : True
}

