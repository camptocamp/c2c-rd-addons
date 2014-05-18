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

from openerp.osv import osv, fields
#import openerp.addons.decimal_precision as dp

import re
from openerp.tools.translate import _



#----------------------------------------------------------
#  Product
#----------------------------------------------------------

class product_product(osv.osv):
    _inherit = 'product.product'
    _columns = {
      'track_internal' : fields.boolean('Track Internal Lots', help="Force to use a Production Lot during internal moves"),
    }

product_product()

class stock_move(osv.osv):
    _inherit = 'stock.move'

    def _check_tracking(self, cr, uid, ids, context=None):
        """ Checks if production lot is assigned to stock move or not.
        @return: True or False
        """
# WARNING
# the check must be state independent - IMHO does not make sense to allow "wrong" data entry and fail only in state done
# this would prohibit generation of pickings form SO/PO
# added track_internal - OpenERP must be able to provied a complete tracking
        for move in self.browse(cr, uid, ids, context=context):
            if move_state == 'done' and not move.prodlot_id and \
            ( \
            (move.product_id.track_production and move.location_id.usage == 'production') or \
            (move.product_id.track_production and move.location_dest_id.usage == 'production') or \
            (move.product_id.track_incoming and move.location_id.usage == 'supplier') or \
            (move.product_id.track_outgoing and move.location_dest_id.usage == 'customer') or \
            (move.product_id.track_internal and ( move.location_id.usage=='internal' or move.location_dest_id.usage=='internal')) \
            ):
                raise osv.except_osv(_('Error !'), _('Missing lot for product %s') % move.product_id.name)
                return False
        return True


stock_move()
