 
import netsvc
from osv import fields, osv


class account_payment_term(osv.osv):
    _inherit = "account.payment.term"
    _columns = {
         'is_discount': fields.boolean('Is Cash Discount', help="Check this box if this payment term is a cash discount. If cash discount is used the remaining amount of the invoice will not be paid")
    }
account_payment_term()
    
    
class account_payment_term_line(osv.osv):
    _inherit = "account.payment.term.line"

    _columns = {
        'is_discount': fields.related('payment_id','is_discount', type='boolean', string='Is Cash Discount', readonly=True) ,
        'discount': fields.float('Discount (%)', digits=(4,2), ),
        'discount_income_account_id': fields.property('account.account', type='many2one', relation='account.account', string='Discount Income Account',  view_load=True,
              help="This account will be used to post the cash discount income"),
        'discount_expense_account_id': fields.property('account.account', type='many2one', relation='account.account', string='Discount Expense Account',  view_load=True,
              help="This account will be used to post the cash discount expense"),
    }    

    def onchange_discount(self, cr, uid, ids, discount):
        if not discount: return {}
        result = {}
        result = {'value': { 'value_amount': round(1-(discount/100.0),2), }}
        return result
        
account_payment_term_line()
