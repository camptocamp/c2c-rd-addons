import time
import locale
from openerp.report import report_sxw
from openerp.osv import osv

class report_real_estate(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_real_estate, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'locale': locale,
        })
        
report_sxw.report_sxw('report.real.estate.location',
                       'stock.location', 
                       'addons/chricar_top/report/report_real_estate_location.mako',
                       parser=report_real_estate)

