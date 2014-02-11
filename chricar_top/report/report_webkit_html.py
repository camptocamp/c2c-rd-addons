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

report_sxw.report_sxw('report.chricar.real.estate.sale.folder',
                       'chricar.top',
                       'addons/chricar_top/report/report_top_sales_folder.mako',
                       parser=report_webkit_html)
