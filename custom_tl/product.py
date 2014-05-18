#  -*- coding: utf-8 -*-
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

from openerp.osv import osv, fields
from openerp.tools.translate import _
        

#----------------------------------------------------------
# Product INHERIT
#----------------------------------------------------------
class product_template(osv.osv):
    _inherit = "product.template"

    _columns = {
         'weight_drip_off': fields.float('Dripp Off Weight'),
         'product_line': fields.selection([('fix','Fix'),('seasonal','Seasonal')],'Product Line'),
         'name_engl': fields.char('Name engl',size=32),
         'minimum_durability': fields.integer('Minimum Durability in Month'),
         'supplier': fields.char('Supplier',size=64),
         'purchase_unit': fields.char('Purchase Unit',size=64),
         'purchase_container': fields.char('Purchase Container',size=64),
         'purchase_container_net_weight': fields.float('Purchase Container Net Weight'),
         'purchase_container_tara_weight': fields.float('Purchase Container Tara Weight'),
         'purchase_container_gross_weight': fields.float('Purchase Container Gross Weight'),
         'purchase_container_dimension': fields.char('Purchase Container Dimension',size=64),
         'portions_per_container': fields.char('Portions per Container',size=64),
    }

product_template()
