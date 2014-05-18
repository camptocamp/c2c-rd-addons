# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import tempfile
import base64
from PIL import Image
import io, StringIO


import logging

try:
    import qrcode
    qr_mod = True
except:
    qr_mod = False

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def _iban_qrcode(self, cr, uid, ids, name, args, context=None):
        _logger = logging.getLogger(__name__)

        res = {}
        min_size = 150
        size = min_size, min_size
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.type == 'out_invoice' and inv.number and qr_mod == True:
                service = 'BCD'
                version = '001'
                code    = '1'
                function = 'SCT'
                bic     = inv.company_id.company_bank_id and inv.company_id.company_bank_id.bank.bic or ''
                partner = inv.company_id.name
                iban    = inv.company_id.company_bank_id and inv.company_id.company_bank_id.acc_number.replace(' ','') or ''
                currency = ''.join([inv.currency_id.name, str(inv.residual)])
                usage  = ''
                ref    = ', '.join([inv.number, inv.date_invoice or ''])
                display = _('This QR-Code will be used to initialize bank payment, you will need to confirm this payment using your E-banking system')

                lf ='\n'
                qr_string = lf.join([service,version,code,function,bic,partner,iban,currency,usage,ref,display])
                _logger.debug('FGF QR string %s', qr_string)
                if len(qr_string) > 331:
                    raise osv.except_osv (_('Error'), _('QR string "%s" length %s exceeds 331 bytes') % (qr_string, len(qr_string)))
                #qr = qrencode.encode_scaled(qr_string,min_size,2)
                #f = tempfile.TemporaryFile(mode="r+")
                #qrCode = qr[2]
                #qrCode.save(f,'png')
                #f.seek(0)
                #qr_pic = base64.encodestring(f.read())            
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=5,
                    border=4,
                )
                qr.add_data(qr_string)
                qr.make(fit=True)

                qr_pic = qr.make_image()
                _logger.debug('FGF QR pic %s', qr_pic)
                f = tempfile.TemporaryFile(mode="r+")
                qr_pic.save(f,'png')
                f.seek(0)
                qr_pic1 = base64.encodestring(f.read())            


                #image_stream = io.BytesIO(qr_pic.decode('base64'))
                #image_stream = qr_pic
                #img = Image.open()
                #img.thumbnail((120, 100), Image.ANTIALIAS)
                #img_stream = StringIO.StringIO()
                #img.save(img_stream, "JPEG")
                #res[inv.id] = img_stream.getvalue().encode('base64')

                
                res[inv.id] = qr_pic1
            else:
                res[inv.id] = False
        return res


    _columns = {
        'iban_qr_code': fields.function(_iban_qrcode, method=True, string='IBAN QR', type='binary'),
    }
account_invoice()
