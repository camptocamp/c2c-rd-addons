# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{ 'sequence': 500,
'name'        : 'VAT check enhanced'
, 'version'     : '1.0'
, 'category'    : 'Base'
, 'description' : """
This module enhances the VAT check to comply to accounting standards

    * save date and the method (vies/checksum) used for checking
    * automatically save the company name associated with the VAT-ID
        * at least some German VAT numbers return '---' as company name !!!

"""
, 'author'      : 'ChriCar Beteiligungs- und Beratungs- GmbH'
, 'depends'     : [ 'base_vat' ]
, 'data'  : ['base_vat_view.xml', 'installer_view.xml']
, 'demo_xml'    : []
, 'installable': False
, 'active'      : False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
