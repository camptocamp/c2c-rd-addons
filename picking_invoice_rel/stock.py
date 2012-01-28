# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011 Camptocamp Austria (<http://www.camptocamp.com>).
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
from osv import fields, osv
import netsvc

class stock_picking(osv.osv):
    _inherit = "stock.picking"

    _columns = {
        'invoice_ids': fields.many2many('account.invoice', 'picking_invoice_rel', 'picking_id', 'invoice_id', 'Invoices'),
    }


    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        res = super(stock_picking,self).action_invoice_create(cr, uid, ids, journal_id,
            group, type, context)
        logger = netsvc.Logger()
        logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, 'action_invoice_create: %s' % res)
        picking_id = res.keys()[0]
        invoice_ids = res.values()[0]
        logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, 'action_invoice_create: %s %s' % (picking_id,invoice_ids))
    
        self.write(cr, uid, picking_id, {'invoice_ids' : [(6,0, [invoice_ids] )]}, context=context) 
        return res

stock_picking()

