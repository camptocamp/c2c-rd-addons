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
from openerp.osv import fields, osv
import openerp.netsvc
import logging



class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def button_validate(self, cr , uid, ids, context=None):
        """FIXME
        workaround because of limited multi company support
        """
        _logger = logging.getLogger(__name__)
        if not context:
            context = {}
        for invoice in self.browse(cr, uid, ids, context):
            _logger.debug('FGF validate partner %s ' %(invoice.partner_id.id)   )
            if invoice.partner_id.company_id and invoice.partner_id.company_id.id != invoice.company_id.id:
               _logger.debug('FGF update partner %s ' %(invoice.partner_id.id)   )
               self.pool.get('res.partner').write(cr, 1, [invoice.partner_id.id], {'company_id':''})

        res= self.button_validate(cr , uid, ids, context)
        return res

account_invoice()
