# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    01-APS-2011 (GK) created
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

class _Record (object) :
    def __init__ (self, **kw):
        self.__dict__["_kw"] = kw.copy()
    # end def __init__
    
    def __repr__(self):
        return str(self.__dict__["_kw"])

    def copy (self, **kw):
        result = self.__class__ (** self._kw)
        result._kw.update (kw)
        return result
    # end def copy
    
    def __getattr__ (self, name):
        try :
            return self._kw [name]
        except KeyError :
            print "WARNING no value found for ", name
            return "MISSING"
# end class _Record

class payment_order(osv.osv) :
    _inherit = "payment.order"

    def action_open(self, cr, uid, ids, *args):
        result = super(payment_order, self).action_open(cr, uid, ids, args)
        self.generate_sepa_credit_transfer(cr, uid, ids, {})
        return result
    # end def action_open
    
#    def set_done(self, cr, uid, ids, *args):
#        result = super(payment_order, self).set_done(cr, uid, ids, args)
#        self.generate_sepa_credit_transfer(cr, uid, ids, {})
#        return result
#    # end def action_open

    def get_wizard(self, type):
        return False
    # end def get_wizard

    def _sepa_strip(self, text) :
        result = text
        txt = "/."
        for c in txt:
            result = result.replace(c, "")
        return result
    # end def _sepa_strip

    def _sepa_payment_date(self, date) :
        today = time.strftime("%Y-%m-%d")
        if not date :
            return today
        elif date < today :
            return today
        else :
            return date
    # end def _sepa_payment_date

    def sepa_payments(self, order, company) :
        dates = {}
        for line in order.line_ids :
            p_bank = line.bank_id
            date   = self._sepa_payment_date(line.date)
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
            if not p_bank : 
                raise osv.except_osv \
                    ( _('Data Error !')
                    , _('Payment for (%s) needs banking information') % (line.partner_id.name)
                    )
            if not p_bank.bank.bic : 
                raise osv.except_osv \
                    ( _('Data Error !')
                    , _('SEPA-Payment requires BIC for bank %s.') % (p_bank.bank.name)
                    )
            if not p_bank.iban : 
                raise osv.except_osv \
                    ( _('Data Error !')
                    , _('SEPA-Payment requires IBAN for bank %s.') % (p_bank.bank.name)
                    )
            if date not in dates :
                dates[date] = Date(P_Bank(p_bank, line))
            elif p_bank not in dates[date] :
                dates[date].add(P_Bank(p_bank, line))
            else :
                dates[date].append(p_bank, line)

        for date, p_banks in dates.iteritems() :
            for p_bank, lines in p_banks.iteritems() :
                amount = sum(l.amount for l in lines)
                if amount <= 0.0 :
                    raise osv.except_osv \
                        ( _('Data Error !')
                        , _('Payment contains a zero or negative transfer amount (%s) for account "%s" of bank "%s" on this date: %s.\nEventually transfer this amount on another day.')
                            % (amount, p_bank.iban, p_bank.bank.name, date)
                        )
        result = {}
        for date, p_banks in dates.iteritems() :
            lls = []
            for p_bank, lines in p_banks.iteritems() :
                if [l for l in lines if l.amount <= 0.0] :
                    tmp_lines = [lines[0]]
                    references = ""
                    for i, line in enumerate(tmp_lines) :
                        invoice = line.move_line_id.invoice
                        rf = []
                        if invoice.number    : rf.append(invoice.number)
                        if invoice.reference : rf.append(invoice.reference)
                        references += " ".join(rf)
                    if not references :
                        raise osv.except_osv \
                            ( _('Data Error !')
                            , _('A descriptive text for the payment is missing')
                            )
                    lls.append \
                        ([_Record
                            ( partner_id    = lines[0].partner_id
                            , p_bank        = p_bank
                            , amount        = sum(l.amount for l in lines)
                            , customer_data = "NOTPROVIDED"
                            , references    = references
                            )
                        ])
                else :
                    tmp_lines = lines
                    for i, line in enumerate(tmp_lines) :
                        invoice = line.move_line_id.invoice
                        rf = []
                        if invoice.number            : rf.append(invoice.number)
                        if line.communication != "/" : rf.append(line.communication)
                        if line.communication2       : rf.append(line.communication2)
                        if invoice.reference         : rf.append(invoice.reference)
                        references = " ".join(rf)
                        if not references :
                            raise osv.except_osv \
                                ( _('Data Error !')
                                , _('A descriptive text for the payment is missing')
                                )
                        if invoice.customer_data :
                            customer_data = invoice.customer_data
                        else :
                            customer_data = "NOTPROVIDED"
                        lls.append \
                            (_Record
                                ( partner_id    = line.partner_id
                                , p_bank        = p_bank
                                , amount        = line.amount
                                , customer_data = customer_data
                                , references    = references
                                )
                            )
            result[date] = lls
        return result
    # end def sepa_payments

    def generate_sepa_credit_transfer(self, cr , uid, ids, context=None):
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        for order in self.browse(cr, uid, ids) :
            if order.state == "cancel" : continue
            bank = order.mode.bank_id
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
            template_ref_obj = self.pool.get("xml.template.ref")
            template_refs = template_ref_obj.browse \
                ( cr, uid
                , template_ref_obj.search
                    (cr, uid, [("name", "=", "%s,%s" % (bank.bank._name, bank.bank.id))])
                )
            if not template_refs :
                raise osv.except_osv \
                    ( _('Data Error !')
                    , _('No SEPA-Template defined for bank %s') % (bank.bank.name)
                    )
            template_ref = template_refs[0]
            protocol = template_ref.xml_template_id.name
            template_obj = self.pool.get("xml.template")
            namespaces = \
                { None  : "APC:STUZZA:payments:ISO:pain:001:001:02:austrian:002"
                , "xsi" : "http://www.w3.org/2001/XMLSchema-instance"
                }
            xml = template_obj.generate_xml \
                (cr, uid
                , template_ref.xml_template_id.id
                , nsmap     = namespaces
                , order     = order
                , company   = company
                , time1     = time.strftime('%Y%m%d%H%M%S')
                , time2     = time.strftime('%Y-%m-%dT%H:%M:%S')
                , sepa_payments = self.sepa_payments
                )
            template_obj.attach_xml \
                ( cr, uid
                , template_ref.xml_template_id.id
                , attach_to   = order
                , xml         = xml
                , name        = "SEPA_" + order.reference
                , fname       = self._sepa_strip(order.reference).upper()
                , description = "SEPA credit transfer " + protocol
                , context     = None
                )
    # end def generate_sepa_credit_transfer
# end class payment_order
payment_order()
