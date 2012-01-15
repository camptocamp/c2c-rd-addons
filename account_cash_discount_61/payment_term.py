 
import netsvc
from osv import fields, osv


class account_payment_term(osv.osv):
    _name = "account.payment.term"
    _columns = {
         'is_discount': fields.boolean('Is Cash Discount', help="Check this box if this payment term is a cash discount. If cash discount is used the remaining amount of the invoice will not be paid")
    }
account_payment_term()
    
    
class account_payment_term_line(osv.osv):
    _name = "account.payment.term.line"

    _columns = {
        'is_discount': fields.related('paymnet_id','is_discount', type='boolean', string='Is Cash Discount', readonly=True) ,
        'discount': fields.float('Discount (%)', digits_compute=dp.get_precision('Account'), required=True),
        'discount_income_account_id': fields.property('account.account', type='many2one', relation='account.account', string='Discount Invome Account', required=True, view_load=True,
              help="This account will be used to post the cash discount income"),
        'discount_expense_account_id': fields.property('account.account', type='many2one', relation='account.account', string='Discount Expense Account', required=True, view_load=True,
              help="This account will be used to post the cash discount expense"),
    }    
        
account_payment_term_line()