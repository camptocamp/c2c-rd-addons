import time
import locale
from openerp.report import report_sxw
from openerp.osv import osv

class report_webkit_html(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_webkit_html, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'locale': locale,
        })

report_sxw.report_sxw('report.account_account.tree_sum',
                       'account.account',
                       'addons/chricar_account_period_sum/report/report_account_account_tree_sum.mako',
                       parser=report_webkit_html)
