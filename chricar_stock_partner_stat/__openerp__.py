# -*- coding: utf-8 -*-
{ "name"         : "Product Partner Moves"
, "version"      : "1.0"
, "author"       : "Camptocamp"
, "website"      : "http://www.camptocamp.com"
, "description"  : """Shows stock move quantities for each partner and period.
It's not a sale statistic, this has to be done from invoices.
Adds partner, transaction type and period to stock move.
"""
, "category"     : "Warehouse Management"
, "depends"      : ["stock", "sale", "purchase", "chricar_view_id", "c2c_stock_accounting"]
, "init_xml"     : []
, "demo_xml"     : []
, "update_xml"   : ["partner_product_view.xml"]
, "auto_install" : False
, "installable"  : True
}
