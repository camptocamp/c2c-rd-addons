# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
import openerp.tools.sql as sql

# SO
class report_sale_order_board(osv.osv):
    _name        = "report.sale.order.board"
    _description = "New Sale Orders per ISO week"
    _auto        = False
    _columns     = \
        { 'week'                : fields.char('Week', size=8, readonly=True, help="ISO-Week")
        , 'so_untaxed_draft'    : fields.float('draft', size=16, readonly=True, help="Untaxed sale order draft per ISO Week")
        , 'so_untaxed_progress' : fields.float('progress', size=16, readonly=True, help="Untaxed sale order progress per ISO Week")
        , 'so_untaxed_done'     : fields.float('done', size=16, readonly=True, help="Untaxed sale order done per ISO Week")
        }
      
    def init(self, cr):
        sql.drop_view_if_exists(cr, 'report_sale_order_board')
        cr.execute("""
CREATE view report_sale_order_board as
  select 
      to_char(date_order,'IYYYIW')::int as id,
      to_char(date_order,'IYYY-IW') as week,
      sum(case when state='draft' then amount_untaxed else 0 end) as so_untaxed_draft,
      sum(case when state='progress' then amount_untaxed else 0 end) as so_untaxed_progress,
      sum(case when state='done' then amount_untaxed else 0 end) as so_untaxed_done
    from sale_order
    where state != 'cancel'
    group by to_char(date_order,'IYYYIW')::int,
             to_char(date_order,'IYYY-IW') order by 1 desc limit 13;
 """)

report_sale_order_board()
 
# PO
class report_purchase_order_board(osv.osv):
    _name        = "report.purchase.order.board"
    _description = "New Purchase Orders per ISO week"
    _auto        = False
    _columns = \
        { 'week'                : fields.char('Week', size=8, readonly=True, help="ISO-Week")
        , 'po_untaxed_draft'    : fields.float('draft', size=16, readonly=True, help="Untaxed draft purchase order per ISO Week")
        , 'po_untaxed_progress' : fields.float('progress', size=16, readonly=True, help="Untaxed progress purchase order per ISO Week")
        , 'po_untaxed_done'     : fields.float('done', size=16, readonly=True, help="Untaxed done purchase order per ISO Week")
        }

    def init(self, cr):
        sql.drop_view_if_exists(cr, 'report_purchase_order_board')
        cr.execute("""
CREATE view report_purchase_order_board as
  select 
      to_char(date_order,'IYYYIW')::int as id,
      to_char(date_order,'IYYY-IW') as week,
      sum(case when state='draft' then amount_untaxed else 0 end) as po_untaxed_draft,
      sum(case when state='progress' then amount_untaxed else 0 end) as po_untaxed_progress,
      sum(case when state='done' then amount_untaxed else 0 end) as po_untaxed_done
    from purchase_order
    where state != 'cancel'
    group by to_char(date_order,'IYYYIW')::int,
             to_char(date_order,'IYYY-IW')
    order by 1 desc limit 13;
 """)

report_purchase_order_board()


#Invoice 
class report_invoice_board(osv.osv):
    _name        = "report.invoice.board"
    _description = "New Invoices per ISO week"
    _auto        = False
    _columns     = \
        { 'week'                 : fields.char('Week', size=8, readonly=True, help="ISO-Week")
        , 'in_invoice_untaxed'   : fields.float('In Invoice Untaxed', size=16, readonly=True, help="Untaxed In invoice untaxed per ISO Week")
        , 'in_invoice_residual'  : fields.float('In Invoice Residual', size=16, readonly=True, help="Untaxed In invoice residual per ISO Week")
        , 'out_invoice_untaxed'  : fields.float('Out Invoice Untaxed', size=16, readonly=True, help="Untaxed Out invoice untaxed per ISO Week")
        , 'out_invoice_residual' : fields.float('Out Invoice Residual', size=16, readonly=True, help="Untaxed Out invoice residual per ISO Week")
        , 'in_refund_untaxed'    : fields.float('In Refund Untaxed', size=16, readonly=True, help="Untaxed In refund untaxed per ISO Week")
        , 'in_refund_residual'   : fields.float('In Refund Residual', size=16, readonly=True, help="Untaxed In refund residual per ISO Week")
        , 'out_refund_untaxed'   : fields.float('Out Refund Untaxed', size=16, readonly=True, help="Untaxed Out refund untaxed per ISO Week")
        , 'out_refund_residual'  : fields.float('Out Refund Residual', size=16, readonly=True, help="Untaxed Out refund residual per ISO Week")
        }

    def init(self, cr):
        sql.drop_view_if_exists(cr, 'report_invoice_board')
        cr.execute("""
CREATE view report_invoice_board as
  select 
      to_char(date_invoice,'IYYYIW')::int as id,
      to_char(date_invoice,'IYYY-IW') as week,
      sum(case when type ='in_invoice' then -amount_untaxed else 0 end) as in_invoice_untaxed,
      sum(case when type ='in_invoice' and amount_total != 0 then -round(residual * amount_untaxed / amount_total) else 0 end) as in_invoice_residual,

      sum(case when type ='out_invoice' then amount_untaxed else 0 end) as out_invoice_untaxed,
      sum(case when type ='out_invoice' and amount_total != 0 then round(residual * amount_untaxed / amount_total) else 0 end) as out_invoice_residual,

      sum(case when type ='in_refund' then amount_untaxed else 0 end) as in_refund_untaxed,
      sum(case when type ='in_refund' and amount_total != 0 then round(residual * amount_untaxed / amount_total) else 0 end) as in_refund_residual,

      sum(case when type ='out_refund' then -amount_untaxed else 0 end) as out_refund_untaxed,
      sum(case when type ='out_refund' and amount_total != 0 then -round(residual * amount_untaxed / amount_total) else 0 end) as out_refund_residual
    from account_invoice
    where date_invoice is not null
    group by to_char(date_invoice,'IYYYIW')::int,
             to_char(date_invoice,'IYYY-IW')
    order by 1 desc limit 13;
 """)

report_invoice_board()

#Liquidity change + balance
# drop view chricar_liqu_balance_change cascade;
class report_finance_base_board(osv.osv):
    _name        = "report.finance.base.board"
    _description = "Financial changes per ISO week"
    _auto        = False
    _columns     = \
        { 'week'                     : fields.char('Week', size=8, readonly=True, help="ISO-Week")
        , 'bank_balance_change'      : fields.float('Bank Balance change', size=16, readonly=True, help="Bank balance change per ISO Week")
        , 'payable_balance_change'   : fields.float('Payable Balance change', size=16, readonly=True, help="Payable balance change per ISO Week")
        , 'receivable_balance_change': fields.float('Receivable Balance change', size=16, readonly=True, help="Receivable balance change per ISO Week"),
      }
      
    def init(self, cr):
        sql.drop_view_if_exists(cr, 'report_finance_board')
        sql.drop_view_if_exists(cr, 'report_finance_base_board')
        cr.execute("""
CREATE view report_finance_base_board as 
  select 
      to_char(date,'IYYYIW')::int as id,
      to_char(date,'IYYY-IW') as week,
      sum(case when t.code ='cash' then debit-credit else 0 end) as bank_balance_change,
      sum(case when a.type = 'payable' and partner_id is not null then debit-credit else 0 end) as payable_balance_change,
      sum(case when a.type = 'receivable' and partner_id is not null then debit-credit else 0 end) as receivable_balance_change
    from account_move_line l,
      account_account a,
      account_account_type t
    where 
      a.id = l.account_id
      and t.id = a.user_type
      and (t.code = 'cash' or a.type in('payable','receivable'))
      and l.state = 'valid'
    group by to_char(date,'IYYYIW')::int,
             to_char(date,'IYYY-IW')
    order by 1 desc limit 13;
 """)
report_finance_base_board()

class report_finance_board(osv.osv):
    _name        = "report.finance.board"
    _description = "Financial changes and state per ISO week"
    _auto        = False
    _columns     = \
        { 'week'                     : fields.char('Week', size=8, readonly=True, help="ISO-Week")
        , 'bank_balance_change'      : fields.float('Bank Balance change', size=16, readonly=True, help="Bank balance change per ISO Week")
        , 'payable_balance_change'   : fields.float('Payable Balance change', size=16, readonly=True, help="Payable balance change per ISO Week")
        , 'receivable_balance_change': fields.float('Receivable Balance change', size=16, readonly=True, help="Receivable balance change per ISO Week")
        , 'bank_balance'             : fields.float('Bank Balance', size=16, readonly=True, help="Bank balance per ISO Week")
        , 'payable_balance'          : fields.float('Payable Balance', size=16, readonly=True, help="Payable balance per ISO Week")
        , 'receivable_balance'       : fields.float('Receivable Balance', size=16, readonly=True, help="Receivable balance per ISO Week")
        , 'liquid_balance'           : fields.float('Liquid Balance', size=16, readonly=True, help="Receivable balance per ISO Week")
        }

    def init(self, cr):
        sql.drop_view_if_exists(cr, 'report_finance_board')
        cr.execute("""
CREATE view report_finance_board as
  select 
      b.id,
      week,
      bank_balance_change,
      payable_balance_change,
      receivable_balance_change,
      sum(case when t.code = 'cash' then debit-credit else 0 end) as bank_balance,
      sum(case when a.type = 'payable' and partner_id is not null then debit-credit else 0 end) as payable_balance,
      sum(case when a.type = 'receivable' and partner_id is not null then debit-credit else 0 end) as receivable_balance,
      sum(case when t.code = 'cash' then debit-credit
                when a.type in ('payable', 'receivable') and partner_id is not null then debit-credit else 0 end) as liquid_balance
    from 
      report_finance_base_board b,
      account_move_line l,
      account_account a,
      account_account_type t,
      account_fiscalyear fy
    where 
      a.id = l.account_id
      and t.id = a.user_type
      and (t.code = 'cash' or a.type in('payable','receivable'))
      and to_char(l.date,'IYYY-IW')  <= week
      and l.date between fy.date_start and fy.date_stop
      and fy.state !='done'
      and l.state = 'valid'
   group by 
     b.id,week,
     bank_balance_change,
     payable_balance_change,
     receivable_balance_change
   order by 1 desc limit 13;
 """)
report_finance_board()
