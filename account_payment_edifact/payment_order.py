# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    05-AUG-2010 (GK) created
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
from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
import unicode2ascii
import base64
import logging

class P_Bank(object):
    def __init__(self, p_bank, line):
        self.p_bank = p_bank
        self.lines = [line]

    def __repr__(self):
        return "(%s:%s)" % (self.p_bank, self.lines) 
    
    def __contains__(self, line):
        return line in self.lines

    def add(self, line):
        self.lines.append(line)
# end class P_Bank
        

class Date(object):
    def __init__(self, p_bank):
        self.p_banks = [p_bank]

    def __repr__(self):
        return str(self.p_banks)
    
    def __len__(self):
        return len(self.p_banks)
    
    def __contains__(self, p_bank):
        return p_bank in [x.p_bank for x in self.p_banks]

    def add(self, p_bank):
        self.p_banks.append(p_bank)
        
    def append(self, p_bank, line):
        for bank in self.p_banks :
            if bank.p_bank == p_bank :
                bank.add(line)
                
    def iteritems(self):
        return [(x.p_bank, x.lines) for x in self.p_banks]
# end class Date

class payment_order(osv.osv) :
    _inherit = "payment.order"
    _logger = logging.getLogger(__name__)

    def action_open(self, cr, uid, ids, *args):
        result = super(payment_order, self).action_open(cr, uid, ids, args)
        self.generate_edifact(cr, uid, ids, {})
        return result
    # end def action_open
    
#    def set_done(self, cr, uid, ids, *args):
#        result = super(payment_order, self).set_done(cr, uid, ids, args)
#        self.generate_edifact(cr, uid, ids, {})
#        return result
#    # end def action_open

    def get_wizard(self, type):
        return False
    # end def get_wizard

    def _address(self, partner, type_list):
        for type in type_list :
            for addr in partner.address :
                if addr.type == type :
                    return addr
        raise osv.except_osv \
            ( _('Data Error !')
            , _('Partner "%s" has no address defined.')
                % (partner.name)
            )
    # end def _address

    def _u2a(self, text) :
        if not text : return ""
        txt = ""
        for c in text:
            if ord(c) < 128 : txt += c
            elif c in unicode2ascii.EXTRA_LATIN_NAMES : txt += unicode2ascii.EXTRA_LATIN_NAMES[c]
            elif c in unicode2ascii.UNI2ASCII_CONVERSIONS : txt += unicode2ascii.UNI2ASCII_CONVERSIONS[c]
            elif c in unicode2ascii.EXTRA_CHARACTERS : txt += unicode2ascii.EXTRA_CHARACTERS[c]
            elif c in unicode2ascii.FG_HACKS : txt += unicode2ascii.FG_HACKS[c]
            else : txt+= "_"
        return self._edifact_strip(txt)
    # end def _u2a

    def _edifact_strip(self, text) :
        result = text
        txt = "+:'"
        for c in txt:
            result = result.replace(c, "")
        return result
    # end def _edifact_strip

    def _payment_date(self, date) :
        today = time.strftime("%Y%m%d")
        if not date :
            return today
        ldate = time.strftime("%Y%m%d", time.strptime(date, "%Y-%m-%d"))
        if ldate < today :
            return today
        else :
            return ldate
    # end def _payment_date

    def _generate_line(self, l, interntl) :
        s = []
        s.append("SEQ++%(seq)s'" % l)
        s.append("MOA+9:%(amount)s:%(currency)s'" % l)
        if l['move_name'] :
            s.append("RFF+PQ:%(move_name)s'" % l)
        if l['customer_data'] and not interntl :
            s.append("RFF+AEF:%(customer_data)s'" % l)
#        s.append("FII+BF+%(iban)s:%(name)s+%(bic)s:25:5'" % l)
        if interntl :
            s.append("FCA+14'")
            s.append("FII+BF+%(iban)s:%(name)s:25:5'" % l)
        else :
            s.append("FII+BF+%(iban)s:%(name)s'" % l)
        s.append("NAD+BE+++%(name)s+%(street)s+%(city)s+%(zip)s+%(country)s'" % l) # sgr3
        s.append("PRC+11'")
        s.append("FTX+PMD+++%(reference)s'" % l)
        return s
    # end def _generate_line
    
    def _generate_date(self, order, p_banks, i, area_code):
        partner_bank_obj = self.pool.get('res.partner.bank')
        s = []
        for p_bank, lines in p_banks.iteritems() :
            if p_bank.state == "iban"  :
                iban    = p_bank.iban.replace(" ", "").upper()
                account = p_bank.acc_number or iban[9:] ### austria-specific!!!
            else :
                raise osv.except_osv \
                    ( _('Data Error !')
                    , _('Banking account has to be specified as IBAN')
                    )
            bic = ''
            if p_bank.bank.bic:
                bic     = p_bank.bank.bic.replace(" ", "").upper()
            bank_name    = self._u2a(p_bank.bank.name).upper()[0:70]
            bank_country = "" if not p_bank.bank.country else p_bank.bank.country.code
            if [l for l in lines if l.amount <= 0.0] :
                line = lines[0]
                i += 1
                a = sum(l.amount for l in lines)
                own_ref = []
                customer_ref = []
                for l in lines :
                    invoice   = l.move_line_id.invoice
                    if invoice.number :
                        invoice_number = self._u2a(invoice.number.replace(".","").replace("/","")).upper()
                        own_ref.append(invoice_number)
                    if invoice.reference :
                        own_ref.append(self._u2a(invoice.reference).upper())
                    if l.communication != "/" :
                        customer_ref.append(self._u2a(l.communication).upper())
                    else:
                        customer_ref.append(self._u2a(invoice.number).upper())
                    if l.communication2 :
                        customer_ref.append(self._u2a(l.communication2).upper())
                    if not customer_ref :
                        raise osv.except_osv \
                            ( _('Data Error !')
                            , _('A descriptive text for the payment is missing for %s'% (own_ref))
                            )
                    
                p_address = self._address(line.partner_id, ['invoice', 'default', False])
                l = \
                    { 'seq'       : "%s" % i
                    , 'amount'    : "%s" % a
                    , 'bank_name' : bank_name
                    , 'bank_country' : bank_country
                    , 'iban'      : iban
                    , 'account'   : account
                    , 'bic'       : bic
                    , 'currency'  : line.currency.name
                    , 'move_name' : (" ".join(customer_ref))[0:35]
                    , 'customer_data' : None
                    , 'name'      : self._u2a(line.partner_id.name).upper()[0:35]
                    , 'street'    : self._u2a(p_address.street).upper()[0:35]
                    , 'city'      : self._u2a(p_address.city).upper()[0:35]
                    , 'zip'       : self._u2a(p_address.zip).upper()[0:9]
                    , 'country'   : p_address.country_id.code or ""
                    , 'reference' : (" ".join(own_ref))[0:70]
                    }
                s.extend(self._generate_line(l, area_code == 'IN'))
            else :
                for line in lines :
                    i += 1
                    invoice   = line.move_line_id.invoice
                    own_ref = []
                    customer_ref = []
                    customer_data = None
                    if invoice.number :
                        invoice_number = self._u2a(invoice.number.replace(".","").replace("/","")).upper()
                        own_ref.append(invoice_number)
                    if invoice.reference :
                        own_ref.append(self._u2a(invoice.reference).upper())
                    if line.communication != "/" :
                        customer_ref.append(self._u2a(line.communication).upper())
                    else:
                        customer_ref.append(self._u2a(invoice.number).upper())
                    if line.communication2 :
                        customer_ref.append(self._u2a(line.communication2).upper())
                    if invoice.customer_data :
                        customer_data = invoice.customer_data[0:12]
                    if not (customer_ref or customer_data) :
                        raise osv.except_osv \
                            ( _('Data Error !')
                            , _('A descriptive text for the payment is missing for %s'% (own_ref))
                            )

                    p_address = self._address(line.partner_id, ['invoice', 'default', False])
                    l = \
                        { 'seq'       : "%s" % i
                        , 'amount'    : "%s" % line.amount
                        , 'bank_name' : bank_name
                        , 'bank_country' : bank_country
                        , 'iban'      : iban
                        , 'account'   : account
                        , 'bic'       : bic
                        , 'currency'  : line.currency.name
                        , 'move_name' : (" ".join(customer_ref))[0:28] # smaller for AEF
                        , 'customer_data' : customer_data
                        , 'name'      : self._u2a(line.partner_id.name).upper()[0:35]
                        , 'street'    : self._u2a(p_address.street).upper()[0:35]
                        , 'city'      : self._u2a(p_address.city).upper()[0:35]
                        , 'zip'       : self._u2a(p_address.zip).upper()[0:9]
                        , 'country'   : p_address.country_id.code or ""
                        , 'reference' : (" ".join(own_ref))[0:70]
                        }
                    s.extend(self._generate_line(l, area_code == 'IN'))
        return s
    # end def _generate_date

    def _line_count(self, banks):
        i = 0
        for p_bank, lines in banks.iteritems() :
            if [l for l in lines if l.amount <= 0.0] :
                i += 1
            else :
                i += len(lines)
        return i
    # end def _line_count

    def _regions(self, order, company) :
        bank    = order.mode.bank_id
        regions = {}
        for line in order.line_ids :
            date   = self._payment_date(line.date)
            p_bank = line.bank_id
            if not p_bank : 
                raise osv.except_osv \
                    ( _('Data Error !')
                    , _('Payment for (%s) needs banking information') % (line.partner_id.name)
                    )
            if not line.move_line_id : 
                raise osv.except_osv \
                    ( _('Data Error !')
                    , _('Payment for (%s) needs accounting information') % (line.partner_id.name)
                    )
            if line.currency != company.currency_id : 
                raise osv.except_osv \
                    ( _('Data Error !')
                    , _('Payment contains currency (%s) different from company currency (%s).')
                        % (line.currency.name, currency_name)
                    )
            if (    p_bank.bank.country 
                and bank.bank.country
                and (p_bank.bank.country == bank.bank.country)
               ) :
                region = "DO" # domestic
            else :
                region = "IN" # international
            if region not in regions :
                regions[region] = {}
            if date not in regions[region] :
                p_banks = P_Bank(p_bank, line)
                regions[region][date] = Date(p_banks)
            elif p_bank not in regions[region][date] :
                p_banks = P_Bank(p_bank, line)
                regions[region][date].add(p_banks)
            else :
                regions[region][date].append(p_bank, line)
        for area_code, dates in regions.iteritems() :
            for date, p_banks in dates.iteritems() :
                for p_bank, lines in p_banks.iteritems() :
                    amount = sum(l.amount for l in lines)
                    if amount <= 0.0 :
                        raise osv.except_osv \
                            ( _('Data Error !')
                            , _('Payment contains a zero or negative transfer amount (%s) for account "%s" of bank "%s" on this date: %s.\nEventually transfer this amount on another day.')
                                % (amount, p_bank.iban if p_bank.iban else p_bank.acc_number, p_bank.bank.name, date)
                            )
        return regions
    # end def _regions

    def _generate_order(self, cr, uid, ids, order, company, context=None) :
        attachment_obj = self.pool.get('ir.attachment')
        currency_name  = company.currency_id.name
        description    = 'EDIFACT-file'
        att_ids = attachment_obj.search \
            ( cr, uid
            , [ ('res_model',   '=', order._table_name)
              , ('res_id',      '=', order.id)
              , ('description', '=', description)
              ]
            )
        if att_ids :
            attachment_obj.unlink(cr, uid, att_ids, context=context)
        ref     = order.reference.upper().replace(".","").replace("/","")
        refkey  = ref
        refname = time.strftime("%Y%m%d%H%M%S")
        company_name = self._u2a(company.name).upper()[0:35]
        address = self._address(company.partner_id, ['invoice', 'default', False])
        country = address.country_id.code or ""
        bank    = order.mode.bank_id
        if not bank.bank.bic :
            raise osv.except_osv \
                ( _('Data Error !')
                , _('Bank %s has no BIC') % (bank.bank.name)
                )
        if not bank.iban :
            raise osv.except_osv \
                ( _('Data Error !')
                , _('Banking Account for bank %s has no IBAN') % (bank.bank.name)
                )
        iban    = bank.iban.replace(" ", "").upper()
        bic     = bank.bank.bic.replace(" ", "").upper()
        street  = self._u2a(address.street).upper()[0:35]
        city    = self._u2a(address.city).upper()[0:35]
        zip     = self._u2a(address.zip).upper()[0:9]
        for area_code, dates in self._regions(order, company).iteritems() :
            total  = 0.0
            i = 0
            s = []
            s.append("UNA:+.? '")
            s.append("UNB+UNOC:3+%s+%s+%s:%s+%s++PAYMUL'" % (company_name, bic, time.strftime("%y%m%d"), time.strftime("%H%M"),refkey))
            s.append("UNH+%s+PAYMUL:D:96A:UN:FAT01G'" % refname)
            s.append("BGM+452+%s+9'" % ref)
            s.append("DTM+137:%s:203'" % (time.strftime("%Y%m%d%H%M%S")))
            s.append("FII+MR+%s'" % iban) # sgr2 # xxx
            s.append("NAD+MS+++%s+%s+%s++%s+%s'" % (company_name, street, city, zip, country)) # sgr3
            lin = 0
            for date, p_banks in dates.iteritems() :
                lin += 1
                if len(p_banks) == 0 : continue
                amount = 0.0
                for p_bank, lines in p_banks.iteritems() :
                    amount += sum(l.amount for l in lines)
                s.append("LIN+%s'" % lin) # sgr4
                s.append("DTM+203:%s:102'" % (date))
                s.append("RFF+AEK:%s'" % time.strftime("%Y%m%d%H%M%S"))
                s.append("BUS++%s++TRF'" % area_code)
                s.append("MOA+9:%s:%s'" % (amount, currency_name))
                s.append("FII+OR+%s:%s::%s'" % (iban, company_name, currency_name))
                s.append("NAD+OY+++%s+%s+%s+%s+%s'" % (company_name, street, city, zip, country)) # sgr3
                seq = 0
                s.extend(self._generate_date(order, p_banks, seq, area_code))
                i += self._line_count(p_banks)
                total += amount
            s.append("CNT+1:%s'" % total)
            s.append("CNT+2:%s'" % len(dates))
            s.append("CNT+39:%s'" % i)
            t = "".join(s)
            t += ("UNT+%s+%s'" % (len(s)-1, refname))
            t += ("UNZ+1+%s'" % refkey)
            vals = \
                { 'name'        : "%s_%s" % (area_code, ref)
                , 'datas'       : base64.encodestring(t)
                , 'datas_fname' : "%s_%s.txt" % (area_code, ref)
                , 'res_model'   : order._table_name
                , 'res_id'      : order.id
                , 'description' : description
                }
            attachment_obj.create(cr, uid, vals, context=context)
            self._logger.debug('EDIFACT `%s`', t)
    # end def _generate_order

    def generate_edifact(self, cr , uid, ids, context=None):
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        for order in self.browse(cr, uid, ids) :
            if order.state == "cancel" : continue
            self._generate_order(cr, uid, ids, order, company, context)
    # end def generate_edifact

# end class payment_order
payment_order()
