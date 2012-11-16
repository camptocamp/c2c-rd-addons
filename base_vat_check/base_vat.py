# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2012 OpenERP SA (<http://openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
import time

class res_partner(osv.osv):
    _inherit = 'res.partner'

    def check_vat(self, cr, uid, ids, context=None):
         """ugly hack to check a second time as check_funct does not return which method succeded
         """
         res = super(res_partner, self).check_vat(cr, uid, ids, context=None)
                 
         for partner in self.browse(cr, uid, ids, context):
             #if res and partner.vat:
             if partner.vat:
                method = ''
                date_now = time.strftime('%Y-%m-%d %H:%M:%S')
                try:
                    import vatnumber
                    vat = vatnumber.check_vies(partner.vat.replace(' ',''))
                    if vat:
                        method = 'vies'
                except:
                    method = 'simple'
             else:
                method = False
                date_now = False
             self.write(cr, uid, ids, {'vat_method': method, 'vat_check_date': date_now})
         return res
          
    _columns = {
        'vat_subjected': fields.boolean('VAT Legal Statement', help="Check this box if the partner is subjected to the VAT. It will be used for the VAT legal statement."),
        'vat_method':  fields.selection([('vies','VIES'),('simple','Simple')], 'VAT Method', readonly=True, help="""'VIES' checks using http://ec.europa.eu/taxation_customs/vies, 'Simple' calculates checksum for specific countries"""),
        'vat_check_date': fields.datetime('VAT Check Date', readonly=True),
    }

    
res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: