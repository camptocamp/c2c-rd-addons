# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    23-Jan-2013 (GK) created
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/> or
# write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################
from osv import fields, osv
import time
from tools.translate import _
import decimal_precision as dp
from tools.sql import drop_view_if_exists

class account_period(osv.osv) :
    _inherit = "account.period"


    def kz_check(self, code, check_pos,check_neg):
        import logging
        _logger = logging.getLogger(__name__)
        codes = []
        if code == '067':
           codes = check_pos
        if code == '090':
           codes = check_neg
        amount = 0
        for c in codes:
           amt = self.kz(c, False)
           if amt < 0 and c in check_pos :
               amount -= amt
           if amt > 0 and c in check_neg :
               amount += amt
           
           _logger.info('FGF kz_negativ %s %s %s ' % (c,codes,amount))
           
        return amount   

    def kz(self, code, check_negativ=True ) :
        import logging
        _logger = logging.getLogger(__name__)
        _logger.info('FGF kz %s %s ' % (code,check_negativ))
        check_pos = [ '022','029' ]
        check_neg = [ '060', ]
        cr      = self.cr
        uid     = self.uid
        period  = self.period
        aml_obj = self.pool.get("account.move.line")
        atc_obj = self.pool.get("account.tax.code")
        #atc_ids = atc_obj.search(cr, uid, [("code", "=", code.replace("KZ", "").replace('-',''))])
        code3 = code.replace("KZ", "").replace('-','')        
        if code3 in ['067', '090']:
            amount =  self.kz_check(code3, check_pos, check_neg)
            if amount == 0:
               amount = "0.00"
            else :
               amount = "%0.2f" % amount
            _logger.info('FGF check %s %s' % (code3,amount))
            return amount
        else: 
            atc_ids = atc_obj.search(cr, uid, [("code", "like", code3)])
            _logger.info('FGF atc_ids %s ' % (atc_ids))
            atc_ids2 = atc_obj.search(cr, uid, [('parent_id', 'child_of', atc_ids)])
            _logger.info('FGF atc_ids2 %s ' % (atc_ids2))
            #aml_ids = aml_obj.search(cr, uid, [("period_id", "=", period.id), ("tax_code_id", "in", tuple(atc_ids))])  # vereinbarte entgelte, hängt von Firmenart ab, currency_id
            aml_ids = aml_obj.search(cr, uid, [("period_id", "=", period.id), ("tax_code_id", "in", atc_ids2)])  # vereinbarte entgelte, hängt von Firmenart ab, currency_id
            if not aml_ids :
                return "0.00"
            else :
                amount = sum(l.tax_amount for l in aml_obj.browse(cr, uid, aml_ids))
                _logger.info('FGF all tax %s %s %s' % (code3,amount,check_negativ))
                if check_negativ and amount < 0:
                    if code3 in check_pos :
                        return "0.00"
                    else:
                        return "%0.2f" % abs(amount)
                else: 
                    return amount
            #return             sum(l.tax_amount for l in aml_obj.browse(cr, uid, aml_ids))
        _logger.info('FGF all tax no return %s', code ) 
    # end def kz

    def generate_u30(self, cr , uid, ids, context=None):
        self.cr  = cr
        self.uid = uid
        for period in self.browse(cr, uid, ids) :
            self.period = period
            tax_number = period.company_id.tax_office_number
            template_obj  = self.pool.get("xml.template")
            template_ids  = template_obj.search(cr, uid, [("name", "=", "U30 VAT declaration")])
            if not template_ids :
                raise osv.except_osv \
                    ( _("Customization Error !")
                    , _("No Template '%s' defined") % template_name
                    )
            template_id = template_ids[0]
            xml = template_obj.generate_xml \
                (cr, uid
                , template_id
                , period   = period
                , paket_nr = time.strftime("%y%m%d%H")
                , datum    = time.strftime("%Y-%m-%d")
                , uhrzeit  = time.strftime("%H:%M:%S")
                , beginn   = period.date_start[0:7]
                , ende     = period.date_stop[0:7]
                , vst      = "000"
                , are      = "J"
                , repo     = "J"
                , kz       = self.kz
                , tax_nr   = tax_number
                )
            template_obj.attach_xml \
                ( cr, uid
                , template_id
                , attach_to   = period
                , xml         = xml
                , name        = period.code + "_U30"
                , fname       = period.code + "_U30"
                , description = "U30 VAT declaration for period"
                , context     = None
                )
    # end def generate_u30

    def button_generate_u30(self, cr, uid, ids, context=None):
        self.generate_u30(cr, uid, ids, context=context)
        return True 

# end class account_period
account_period()


class account_period_tax(osv.osv):
    _name        = "account.period.tax"
    _description = "Account Period Tax"
    _auto        = False

    def _get_percent(self, cr, uid, ids, field_name, arg, context=None):
         result = {}
         tax_obj = self.pool.get('account.tax') 
         tax_code_obj = self.pool.get('account.tax.code') 
         for code in self.browse(cr, uid, ids, context):
             result[code.id] = 0.00
             for tc in tax_code_obj.browse(cr, uid, [code.tax_code_id.id], context):
                 tax_ids = tax_obj.search(cr, uid, ['|',('base_code_id','=',tc.id), ('tax_code_id','=',tc.id )]) 
                 for percent in tax_obj.browse(cr, uid, tax_ids, context):
                     result[code.id] = percent.amount
         return result

    def _get_base(self, cr, uid, ids, field_name, arg, context=None):
         result = {}
         tax_obj = self.pool.get('account.tax') 
         tax_code_obj = self.pool.get('account.tax.code') 
         for code in self.browse(cr, uid, ids, context):
             result[code.id] = False
             for tc in tax_code_obj.browse(cr, uid, [code.tax_code_id.id], context):
                 tax_ids = tax_obj.search(cr, uid, [('base_code_id','=',tc.id)]) 
                 if tax_ids:
                     result[code.id] = True
         import logging
         _logger = logging.getLogger(__name__)
         _logger.info('FGF get_base %s ' % (result))
         return result

    def _get_percent_amount(self, cr, uid, ids, field_name, arg, context=None):
         result = {}
         for code in self.browse(cr, uid, ids, context):
             if code.tax_base:
                 result[code.id] = code.tax_amount * code.tax_percent 
             else:
                 result[code.id] = code.tax_amount  
         return result


    def _get_percent_amount_check(self, cr, uid, ids, field_name, arg, context=None):
         result = {}
         for code in self.browse(cr, uid, ids, context):
             if code.tax_base:
                 result[code.id] = -code.tax_amount * code.tax_percent 
             else:
                 result[code.id] = code.tax_amount  
         return result
 
    _columns  = {
          'name'               : fields.char    ('Tax Code Name',size=32) 
        , 'company_id'         : fields.many2one('res.company', 'Company', required=True)
        , 'period_id'          : fields.many2one('account.period' , 'Period' ,readonly=True)
        , 'tax_code_id'        : fields.many2one('account.tax.code', 'Tax Code', help="The tax basis of the tax declaration.")
        , 'debit'              : fields.float   ('Debit', digits_compute=dp.get_precision('Account') ,readonly=True)
        , 'credit'             : fields.float   ('Credit', digits_compute=dp.get_precision('Account'),readonly=True)
        , 'balance'            : fields.float   ('Balance Period', digits_compute=dp.get_precision('Account')    ,readonly=True)
        , 'tax_amount'         : fields.float   ('Tax Amount', digits_compute=dp.get_precision('Account'),readonly=True)
        , 'tax_base'           : fields.function(_get_base, method=True, type='boolean', string='Tax Base') 
        , 'tax_percent'        : fields.function(_get_percent, digits_compute=dp.get_precision('Account'), method=True, type='float', string='Tax %')
        , 'tax_percent_amount' : fields.function(_get_percent_amount, digits_compute=dp.get_precision('Account'), method=True, type='float', string='Tax % Amount')
        , 'tax_percent_amount_check' : fields.function(_get_percent_amount_check, digits_compute=dp.get_precision('Account'), method=True, type='float', string='Tax Check')
        }

    def init(self, cr):
        drop_view_if_exists(cr, "account_period_tax")
        cr.execute("""
           create or replace view account_period_tax as
         select max(l.id) as id,
               c.name as name,l.company_id as company_id, l.period_id as period_id, l.tax_code_id as tax_code_id, 
               sum(l.debit) as debit, sum(l.credit) as credit, sum(l.debit-l.credit) as balance, sum(l.tax_amount) as tax_amount
           from account_move_line l,
                account_tax_code c
          where c.id = l.tax_code_id
           group by c.name,l.company_id, l.period_id, l.tax_code_id
           """)
         
account_period_tax()
