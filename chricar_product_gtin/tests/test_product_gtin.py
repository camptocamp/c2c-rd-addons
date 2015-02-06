# -*- encoding: utf-8 -*-
#
# OpenERP, Open Source Management Solution
# This module copyright (C) 2013 Savoir-faire Linux
# (<http://www.savoirfairelinux.com>).
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

from openerp.tests import common
from openerp.exceptions import ValidationError


class TestProductGtin(common.TransactionCase):
    def setUp(self):
        super(TestProductGtin, self).setUp()
        self.product_model = self.env['product.product']

    def testCodeValidity(self):
        product = self.product_model.create(
            {'name': 'p_name'}
        )

        # Verify EAN-8 code
        product.ean13 = '96385074'
        validity = product._check_ean_key()
        self.assertTrue(validity)

        # Verify EAN-13 code
        product.ean13 = '7501054530107'
        validity = product._check_ean_key()
        self.assertTrue(validity)

        # Verify UPC-A code
        product.ean13 = '07501054530107'
        validity = product._check_ean_key()
        self.assertTrue(validity)

        # Verify GTIN-14 code
        product.ean13 = '98765432109213'
        validity = product._check_ean_key()
        self.assertTrue(validity)

        # Verify non-valid code, invalid EAN-8
        with self.assertRaises(ValidationError):
            product.ean13 = '12345678'

        # Verify non-valid code, lenght
        with self.assertRaises(ValidationError):
            product.ean13 = '123456789'
