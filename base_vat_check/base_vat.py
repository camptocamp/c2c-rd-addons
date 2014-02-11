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
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from urllib import getproxies

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _sel = [('vies','VIES'),('simple','Simple'),('none','Not Checked')]
    _columns = \
        { 'vat_subjected'     : fields.boolean('VAT Legal Statement', help="Check this box if the partner is subjected to the VAT. It will be used for the VAT legal statement.")
        , 'vat_method'        : fields.selection(_sel, 'VAT Method', readonly=True, help="""'VIES' checks using http://ec.europa.eu/taxation_customs/vies, 'Simple' calculates checksum for specific countries""")
        , 'vat_check_date'    : fields.datetime('VAT Check Date', readonly=True)
        , 'vat_check_name'    : fields.char('VAT Check Name', size=256, readonly=True)
        , 'vat_check_address' : fields.text('VAT Check Address', readonly=True)
        }

    def check_vat(self, cr, uid, ids, context=None):
        #res = super(res_partner, self).check_vat(cr, uid, ids, context=None)
        res = True
        self.check_vat_ext(cr, uid, ids, context=None)
        return res

    def check_vat_ext(self, cr, uid, ids, context):
        if not context:
            context = {}
        vat = ''
        if context.get('vat'):
            if context['vat'] != 'none':
                vat = context['vat'].replace(" ","")
        else:
            for partner in self.browse(cr, uid, ids, context):
                if partner.vat:
                    vat = partner.vat.replace(" ","")
        method = 'none'
        date_now = time.strftime('%Y-%m-%d %H:%M:%S')
        name = ""
        address = ""
        if vat:
            vat = vat.replace(' ','')
            vat_mod = False
            user_company = self.pool.get('res.users').browse(cr, uid, uid).company_id
            if user_company.vat_check_vies:
                try:
                    from suds.client import Client
                    vat_mod = True
                except:
                    raise osv.except_osv(_('Error'), _('import module "suds" failed - check VIES needs this module'))

            check = False
            if vat_mod:
                try:
                    client = Client("http://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl", proxy=getproxies())
                    res = client.service.checkVat(countryCode=vat[:2], vatNumber=vat[2:])

                    check = bool(res["valid"])
                    if check :
                        #date_now = res["requestDate"]
                        name = res["name"]
                        address = res["address"]
                        method = 'vies'
                    else:
                        raise osv.except_osv(_('VIES Error'), _('VIES check failed "%s"') % vat)
                except:
                    raise osv.except_osv(_('VIES Error'), _('General Error: connection timeout for "%s"') % vat)

            else:
                vat_country, vat_number = self._split_vat(vat)
                if self.simple_vat_check(cr, uid, vat_country, vat_number, context=context):
                    method = 'simple'
                else:
                    raise osv.except_osv(_('Error'), _('simple VAT check digit failed'))
        vals = {'vat_method': method, 'vat_check_date': date_now, 'vat_check_name' : name, 'vat_check_address' : address, 'vat' : vat}
        self.write(cr, uid, ids, vals)
        return vals

    def vat_change(self, cr, uid, ids, value, context=None):
        res = super(res_partner, self).vat_change(cr, uid, ids, value, context=None)   

        if not context:
            context = {}
        context['vat'] = value or 'none'
        vals = self.check_vat_ext(cr, uid, ids, context)  
        res['value'].update(vals)
        return res

res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

