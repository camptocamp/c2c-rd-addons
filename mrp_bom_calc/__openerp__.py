# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com) All Rights Reserved.
# sinoj@zbeanztech.com
# Copyright (c) 2009 ChriCar Bet. u Ber. GmbH
# Copyright (c) 2012 ChriCar Beteiligungs- und Beratungs- GmbH (http://www.camptocamp.at)
# Author : Ferdinand Gassauer (Camptocamp)
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
#
##############################################################################

{ 'sequence': 500,

'name': 'MRP bom calculation',
'version': '.02',
'description': """
This programm adds 
 *  version management and 
 *  calculation of costs to bill of material
""",
'author': 'zBeanz',
'website': 'http://www.zbeanztech.com',
'depends': ['c2c_product_price_unit','mrp','mrp_subproduct'],
'init_xml': [],
'data': [
       'mrp_view.xml',
       'mrp_bom_workflow.xml',
],
'demo_xml': [],
'installable': False,
'active': False,
'certificate': '',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
