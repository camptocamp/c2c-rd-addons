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
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
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
from tools.translate import _
from lxml import etree
import time
import base64

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
        for p_bank in self.p_banks :
            if p_bank.p_bank == p_bank :
                p_bank.add(line)
                
    def iteritems(self):
        return [(x.p_bank, x.lines) for x in self.p_banks]
# end class Date

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

    def _invoice_customer_data(self) :
        invoice_obj = self.pool.get('account.invoice')
        return invoice_obj._columns.has_key("customer_data")
    # end def _invoice_customer_data

    def _dates(self, order, company) :
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
                dates[date].append(p_banks, line)
        for date, p_banks in dates.iteritems() :
            for p_bank, lines in p_banks.iteritems() :
                amount = sum(l.amount for l in lines)
                if amount <= 0.0 :
                    raise osv.except_osv \
                        ( _('Data Error !')
                        , _('Payment contains a zero or negative transfer amount (%s) for account "%s" of bank "%s" on this date: %s.\nEventually transfer this amount on another day.')
                            % (amount, p_bank.iban, p_bank.bank.name, date)
                        )
        return dates
    # end def _dates

    def _remove_attachments(self, cr, uid, order, description, context=None):
        attachment_obj = self.pool.get('ir.attachment')
        ref   = self._sepa_strip(order.reference).upper()
        att_ids = attachment_obj.search \
            ( cr, uid
            , [ ('res_model', '=', order._table_name)
              , ('res_id', '=', order.id)
              , ('description', '=', description)
              , ('datas_fname', '=', "%s.xml" % ref)
              ]
            )
        if att_ids :
            attachment_obj.unlink(cr, uid, att_ids, context=context)
    # end def _remove_attachments

    def _manage_attachments(self, cr, uid, order, text, description, context=None):
        attachment_obj = self.pool.get('ir.attachment')
        self._remove_attachments(cr, uid, order, description, context=context)
        ref   = self._sepa_strip(order.reference).upper()
        title = description.lower().replace(" ", "_")
        vals  = \
            { 'name'         : title
            , 'datas'        : text
            , 'datas_fname'  : "%s.xml" % ref
            , 'res_model'    : order._table_name
            , 'res_id'       : order.id
            , 'description'  : description
            }
        attachment_obj.create(cr, uid, vals, context=context)
    # end def _manage_attachments

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
            func = order.mode.bank_id.bank.sepa_credit_transfer_protocol
            self.f = getattr(order, "_pain_001_001_" + func)
            self.f(order, company, context)
    # end def generate_sepa_credit_transfer
    
    def _pain_001_001_02_austrian_002(self, cr , uid, ids, order, company, context=None):
        currency_name = company.currency_id.name
        ntx = 0
        namespaces = \
            { None  : "urn:iso:std:iso:20022:tech:xsd:pain.001.001.02"
            , "xsi" : "http://www.w3.org/2001/XMLSchema-instance"
            }
        root = etree.Element("Document", nsmap = namespaces)
        ti = etree.SubElement(root, "pain.001.001.02")
        grp = etree.SubElement(ti, "GrpHdr")
        msgi = etree.SubElement(grp, "MsgId")
        msgi.text = time.strftime("%Y%m%d%H%M%S")
        cred = etree.SubElement(grp, "CreDtTm")
        cred.text = time.strftime("%Y-%m-%dT%H:%M:%S")
        ntxs = etree.SubElement(grp, "NbOfTxs")
        ntxs.text = "%s" % len (order.line_ids) ### negativ?
        ctrl = etree.SubElement(grp, "CtrlSum")
        ctrl.text = "%s" % order.total
        grpg = etree.SubElement(grp, "Grpg")
        grpg.text = "MIXD"
        init = etree.SubElement(grp, "InitgPty")
        initn = etree.SubElement(init, "Id")
        iorgid = etree.SubElement(initn, "OrgId")
        bkptyid = etree.SubElement(iorgid, "BkPtyId")
        bkptyid.text = order.mode.bank_id.iban.replace(" ", "").upper()[0:35]
        pmt = etree.SubElement(ti, "PmtInf")
        for date, p_banks in self._dates(order, company).iteritems() :
            pmti = etree.SubElement(pmt, "PmtInfId")
            pmti.text = time.strftime("%Y%m%d%H%M%S")
            pmtm = etree.SubElement(pmt, "PmtMtd")
            pmtm.text = "TRF"
            pmtt = etree.SubElement(pmt, "PmtTpInf")
            pmtts = etree.SubElement(pmtt, "SvcLvl")
            pmttsc = etree.SubElement(pmtts, "Cd")
            pmttsc.text = "SEPA"
            reqr = etree.SubElement(pmt, "ReqdExctnDt")
            reqr.text = date
            dbtr = etree.SubElement(pmt, "Dbtr")
            dbtrn = etree.SubElement(dbtr, "Nm")
            dbtrn.text = company.name[0:70]
            dbta = etree.SubElement(pmt, "DbtrAcct")
            dbtid = etree.SubElement(dbta, "Id")
            dbiban = etree.SubElement(dbtid, "IBAN")
            dbiban.text = order.mode.bank_id.iban.replace(" ", "").upper()
            curncy = etree.SubElement(dbta, "Ccy")
            curncy.text = currency_name
            dbtg = etree.SubElement(pmt, "DbtrAgt")
            finst = etree.SubElement(dbtg, "FinInstnId")
            ctrbic = etree.SubElement(finst, "BIC")
            ctrbic.text = order.mode.bank_id.bank.bic.replace(" ", "").upper()
            for p_bank, lines in p_banks.iteritems() :
                if [l for l in lines if l.amount <= 0.0] :
                    tmp_lines = [lines[0]]
                    amounts = {0 : sum(l.amount for l in lines)}
                    references = {0 : ""}
                    customer_data = {0 : None}
                    for i, line in enumerate(tmp_lines) :
                        invoice   = line.move_line_id.invoice
                        rf = []
                        if invoice.number    : rf.append(invoice.number)
                        if invoice.reference : rf.append(invoice.reference)
                        references[0] += " ".join(rf)
                    if not references[0] :
                        raise osv.except_osv \
                            ( _('Data Error !')
                            , _('A descriptive text for the payment is missing')
                            )
                else :
                    tmp_lines = lines
                    amounts = {}
                    references = {}
                    customer_data = {}
                    for i, line in enumerate(tmp_lines) :
                        invoice   = line.move_line_id.invoice
                        amounts[i] = l.amount
                        rf = []
                        if invoice.number            : rf.append(invoice.number)
                        if line.communication != "/" : rf.append(line.communication)
                        if line.communication2       : rf.append(line.communication2)
                        if invoice.reference         : rf.append(invoice.reference)
                        references[i] = " ".join(rf)
                        if not references[i] :
                            raise osv.except_osv \
                                ( _('Data Error !')
                                , _('A descriptive text for the payment is missing')
                                )
                        if self._invoice_customer_data() and invoice.customer_data :
                            customer_data[i] = invoice.customer_data
                        else :
                            customer_data[i] = "NOTPROVIDED"
    
                for i, line in enumerate(tmp_lines) :
                    ntx += 1
                    invoice   = line.move_line_id.invoice
                    cdtx = etree.SubElement(pmt, "CdtTrfTxInf")
                    pmtid = etree.SubElement(cdtx, "PmtId")
                    endend = etree.SubElement(pmtid, "EndToEndId") # z.B. Steuernummer[0:35]
                    endend.text = customer_data[i][0:35]
                    amtgr = etree.SubElement(cdtx, "Amt")
                    amtins = etree.SubElement(amtgr, "InstdAmt")
                    amtins.set("Ccy",currency_name)
                    amtins.text = "%s" % amounts[i]
                    cdagt = etree.SubElement(cdtx, "CdtrAgt")
                    cdagtf = etree.SubElement(cdagt, "FinInstnId")
                    cdagtfb = etree.SubElement(cdagtf, "BIC")
                    cdagtfb.text = p_bank.bank.bic.replace(" ", "").upper()
                    cdtrx = etree.SubElement(cdtx, "Cdtr")
                    cdtrxn = etree.SubElement(cdtrx, "Nm")
                    cdtrxn.text = line.partner_id.name[0:70]
                    cdtac = etree.SubElement(cdtx, "CdtrAcct")
                    cdtaid = etree.SubElement(cdtac, "Id")
                    cdtiban = etree.SubElement(cdtaid, "IBAN")
                    cdtiban.text = p_bank.iban.replace(" ", "").upper()
                    rmtin = etree.SubElement(cdtx, "RmtInf")
                    ustrdx = etree.SubElement(rmtin, "Ustrd")
                    ustrdx.text = references[i][0:140]
        ntxs.text = "%s" % ntx
        description = "Payment SEPA Credit Transfer V2"
        print "pain_001_001_02_austrian_002", etree.tostring(root, encoding="iso-8859-1")
        self._manage_attachments \
            ( cr, uid
            , order
            , base64.encodestring(etree.tostring(root, encoding="iso-8859-1"))
            , description
            , context=context
            )
    # end def _pain_001_001_02_austrian_002

    def _pain_001_001_03_austrian_001(self, cr , uid, ids, order, company, context=None):
        currency_name = company.currency_id.name
        ntx = 0
        namespaces = \
            { None : "ISO:pain.001.001.03:APC:STUZZA:payments:001"
            , "xsi" : "http://www.w3.org/2001/XMLSchema-instance"
            }
        root = etree.Element("Document", nsmap = namespaces)
        ti = etree.SubElement(root, "CstmrCdtTrfInitn")
        grp = etree.SubElement(ti, "GrpHdr")
        msgi = etree.SubElement(grp, "MsgId")
        msgi.text = time.strftime("%Y%m%d%H%M%S")
        cred = etree.SubElement(grp, "CreDtTm")
        cred.text = time.strftime("%Y-%m-%dT%H:%M:%S")
        ntxs = etree.SubElement(grp, "NbOfTxs")
        ctrl = etree.SubElement(grp, "CtrlSum")
        ctrl.text = "%s" % order.total
        init = etree.SubElement(grp, "InitgPty")
        initn = etree.SubElement(init, "Nm")
        initn.text = order.mode.bank_id.iban.replace(" ", "").upper()[0:35]
        pmt = etree.SubElement(ti, "PmtInf")
        for date, p_banks in self._dates(order, company).iteritems() :
            pmti = etree.SubElement(pmt, "PmtInfId")
            pmti.text = time.strftime("%Y%m%d%H%M%S")
            pmtm = etree.SubElement(pmt, "PmtMtd")
            pmtm.text = "TRF"
            ctrl = etree.SubElement(pmt, "CtrlSum")
            amount = 0.0
            for p_bank, lines in p_banks.iteritems():
                amount += sum(l.amount for l in lines)
            ctrl.text = "%s" % amount
            reqr = etree.SubElement(pmt, "ReqdExctnDt")
            reqr.text = date
            dbtr = etree.SubElement(pmt, "Dbtr")
            dbtrn = etree.SubElement(dbtr, "Nm")
            dbtrn.text = company.name[0:70]
            dbtri = etree.SubElement(dbtr, "Id")
            orgaid = etree.SubElement(dbtri, "OrgId")
            bicobei = etree.SubElement(orgaid, "BICOrBEI")
            bicobei.text = order.mode.bank_id.bank.bic.replace(" ", "").upper()
            dbta = etree.SubElement(pmt, "DbtrAcct")
            dbtid = etree.SubElement(dbta, "Id")
            dbiban = etree.SubElement(dbtid, "IBAN")
            dbiban.text = order.mode.bank_id.iban.replace(" ", "").upper()
            curncy = etree.SubElement(dbta, "Ccy")
            curncy.text = currency_name
            dbtg = etree.SubElement(pmt, "DbtrAgt")
            finst = etree.SubElement(dbtg, "FinInstnId")
            ctrbic = etree.SubElement(finst, "BIC")
            ctrbic.text = order.mode.bank_id.bank.bic.replace(" ", "").upper()
    
            for p_bank, lines in p_banks.iteritems() :
                if [l for l in lines if l.amount <= 0.0] :
                    tmp_lines = [lines[0]]
                    amounts = {0 : sum(l.amount for l in lines)}
                    references = {0 : ""}
                    customer_data = {0 : None}
                    for i, line in enumerate(tmp_lines) :
                        invoice = line.move_line_id.invoice
                        rf = []
                        if invoice.number    : rf.append(invoice.number)
                        if invoice.reference : rf.append(invoice.reference)
                        references[0] += " ".join(rf)
                    if not references[0] :
                        raise osv.except_osv \
                            ( _('Data Error !')
                            , _('A descriptive text for the payment is missing')
                            )
                else :
                    tmp_lines = lines
                    amounts = {}
                    references = {}
                    customer_data = {}
                    for i, line in enumerate(tmp_lines) :
                        invoice   = line.move_line_id.invoice
                        amounts[i] = l.amount
                        rf = []
                        if invoice.number            : rf.append(invoice.number)
                        if line.communication != "/" : rf.append(line.communication)
                        if line.communication2       : rf.append(line.communication2)
                        if invoice.reference         : rf.append(invoice.reference)
                        references[i] = " ".join(rf)
                        if not references[i] :
                            raise osv.except_osv \
                                ( _('Data Error !')
                                , _('A descriptive text for the payment is missing')
                                )
                        if self._invoice_customer_data() and invoice.customer_data :
                            customer_data[i] = invoice.customer_data
                        else :
                            customer_data[i] = "NOTPROVIDED"
                for i, line in enumerate(tmp_lines) :
                    ntx += 1
                    cdtx = etree.SubElement(pmt, "CdtTrfTxInf")
                    pmtid = etree.SubElement(cdtx, "PmtId")
                    endend = etree.SubElement(pmtid, "EndToEndId") # z.B. Steuernummer [0:35]
                    endend.text = customer_data[i][0:35]
                    amtgr = etree.SubElement(cdtx, "Amt")
                    amtins = etree.SubElement(amtgr, "InstdAmt")
                    amtins.set("Ccy",currency_name)
                    amtins.text = "%s" % amounts[i]
                    cdagt = etree.SubElement(cdtx, "CdtrAgt")
                    cdagtf = etree.SubElement(cdagt, "FinInstnId")
                    cdagtfb = etree.SubElement(cdagtf, "BIC")
                    cdagtfb.text = p_bank.bank.bic.replace(" ", "").upper()
                    cdtrx = etree.SubElement(cdtx, "Cdtr")
                    cdtrxn = etree.SubElement(cdtrx, "Nm")
                    cdtrxn.text = line.partner_id.name[0:70]
                    cdtac = etree.SubElement(cdtx, "CdtrAcct")
                    cdtaid = etree.SubElement(cdtac, "Id")
                    cdtiban = etree.SubElement(cdtaid, "IBAN")
                    cdtiban.text = p_bank.iban.replace(" ", "").upper()
                    rmtin = etree.SubElement(cdtx, "RmtInf")
                    ustrdx = etree.SubElement(rmtin, "Ustrd")
                    ustrdx.text = references[i][0:140]
        ntxs.text = "%s" % ntx
        description = "Payment SEPA Credit Transfer V3"
        print "pain_001_001_03_austrian_001", etree.tostring(root, encoding="iso-8859-1") ########################
        self._manage_attachments \
            ( cr, uid
            , order
            , base64.encodestring(etree.tostring(root, encoding="iso-8859-1"))
            , description
            , context=context
            )
    # end def _pain_001_001_03_austrian_001
# end class payment_order
payment_order()

class res_bank(osv.osv):
    _inherit = "res.bank"
    _ct_states = \
        ( ("02_austrian_002", "Version 2")
        , ("03_austrian_001", "version 3")
        )
    _columns = \
        { 'sepa_credit_transfer_protocol' : fields.selection
            (_ct_states, 'SEPA Credit Transfer Protocol Version', required=True),
        }
    _defaults = \
        { 'sepa_credit_transfer_protocol' : lambda *a: "03_austrian_001"}
# end class res_bank
res_bank()
