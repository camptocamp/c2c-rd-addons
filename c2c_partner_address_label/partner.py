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

from openerp.osv import fields,osv
import openerp.tools
from openerp.tools.translate import _
import logging


# new in 6.1 label_format
#----------------------------------------------------------
#  Country
#----------------------------------------------------------

#class Country(osv.osv):
#    _inherit = 'res.country'
#    _columns = {
#        'zip_position' : fields.selection([('before','Before'),('after','After'),('below','Below')], string="Zip Position", help="Zip position relative to city name"),
#    }
#
#    _defaults = {
#        'zip_position': lambda *a: 'before',
#    }
#
#    def init(self, cr):
#        # set reasonable values
#        cr.execute("""update res_country
#                         set zip_position = 'after'
#                       where code in ('US')
#                         and zip_position is null""")
#        cr.execute("""update res_country
#                         set zip_position = 'below'
#                       where code in ('GB')
#                         and zip_position is null""")
#Country()

#----------------------------------------------------------
#  Company
#----------------------------------------------------------

class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'company_address_id':fields.many2one('res.partner', 'Address for Report Header'),
        'address_label_position' : fields.selection([('left','Left'),('right','Right')], string="Address Window Position", help="Position of address window on standard company enevlops. Many reports do not use this yet"),
        'print_code': fields.boolean('Print Product Code',help="Print product code on invoice, picking, sale order"),
        'print_address_info': fields.boolean('Print Address Info',help="Print additional address information next ot address field"),
        'print_cell_borders': fields.boolean('Print Cell Borders',help="Print fine cell borders"),
        'document_label_position': fields.selection([('left','Left'),('right','Right')], string="Document Label Position", help="Position of address number and date left or right"),
    }
    _defaults = {
        'address_label_position': lambda *a: 'right',
        'document_label_position': lambda *a: 'right',
        'print_code': lambda *a: True,
        'print_address_info': lambda *a: True,
        'print_cell_borders': lambda *a: True,
        
    }

res_company()

#----------------------------------------------------------
#  Address
#----------------------------------------------------------
class res_partner(osv.osv):
    _inherit = 'res.partner'

    def _address_label(self, cr, uid, ids, name, arg, context=None):
        _logger = logging.getLogger(__name__)
        res = {}
        _logger.debug('FGF address_label ids %s ' % (ids))
        for a in self.browse(cr,uid,ids,context):
            _logger.debug('FGF address_label street %s' % (a.street))
            lf ='\n'

#            bc = self.pool.get('ir.module.module').search(cr, uid,  [('name', '=', 'base_partner_contact'),('state', '=', 'installed')], context=context)
#            if bc:
#                l = a.full_name
#            else:
#                l = a.name or ''
#                if a.title:
#                    l = l + ' ' + a.title.name
#
#            bc = self.pool.get('ir.module.module').search(cr, uid,  [('name', '=', 'base_contact'),('state', '=', 'installed')], context=context)
#
#            if not bc:
#                t = ''
#                if a.title:
#                    t = a.title.name + ' ' or ''
#                if a.name:
#                    t = t + a.name
#                if t:
#                    l = l + lf + t



            if a.parent_id:
                l = a.parent_id.name + lf + a.name
            else:
                l = a.name
            address = self._display_address(cr,uid,a,without_company=True)
            address_compact =''
            for line in address.split('\n'):
                if line.strip():
                    address_compact += line + '\n'
            res[a.id] = l + lf + address_compact
            _logger.debug('FGF address_label %s' % (res[a.id]))
        return res

    _columns = {
        'address_label': fields.function(_address_label, type='text', method = True, string="Address Label"),
    }

res_partner()
