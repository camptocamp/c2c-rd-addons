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
from openerp.tools.translate import _
import logging
import openerp.addons.decimal_precision as dp


class product_template(osv.osv):
    _inherit = "product.template"    

    _columns = {
        'uos_coeff': fields.float('UOM -> UOS Coeff', 
            help='Coefficient to convert UOM to UOS\n'
            ' uos = uom * coeff'),

        'uos_coeff_inv': fields.float('UoM per UoS ' , digits_compute= dp.get_precision('Product UoS'), 
             help='Inverted Coefficient to convert UOM to UOS\n'
            ' uos = uom / coeff '),
    }

product_template()

class product_product(osv.osv):
    _inherit = "product.product"    

    def uos_coeff_inv_change(self, cr, uid, ids, uos_coeff_inv=None, context=None):
        _logger = logging.getLogger(__name__)
        _logger.debug('FGF sale uos_coeff_inv %s'  % uos_coeff_inv )
        res = {}
        res['value'] = {}
        if uos_coeff_inv:
              res['value']['uos_coeff'] = 1.0/uos_coeff_inv
        _logger.debug('FGF sale uos res %s' % (res) )
        return res    
    
    def _product_pack_available(self, cr, uid, ids, name, args, context=None):
        res = {}
        for prod in self.browse(cr, uid, ids, context=context):
                pack_qty = ''
                if prod.packaging and prod.packaging[0].qty and prod.packaging[0].qty != 0:
                    pack_qty = prod.qty_available / prod.packaging[0].qty
                res[prod.id] = pack_qty
        return res

    def _product_pack_name(self, cr, uid, ids, name, args, context=None):
        res = {}
        for prod in self.browse(cr, uid, ids, context=context):
                pack_name = ''
                if prod.packaging and prod.packaging[0].ul :
                    pack_name = prod.packaging[0].ul.name + ' '+_(u'á')+' '+ str(prod.packaging[0].qty)
                res[prod.id] = pack_name
        return res


    _columns = {
        'pack_name' : fields.function(_product_pack_name, type='char', string='Pack Name'),
        'pack_qty_available': fields.function(_product_pack_available, 
                                        type='float',  digits_compute=dp.get_precision('Product UoM'),
                                                    string='Pack Quantity On Hand',)
        }
                    
product_product()

