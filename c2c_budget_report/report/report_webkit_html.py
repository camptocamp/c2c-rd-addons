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

report_sxw.report_sxw('report.c2c_budget.item.chart',
                       'c2c_budget.item',
                       'addons/c2c_budget_report/report/report_c2c_budget_item.mako',
                       parser=report_webkit_html)

