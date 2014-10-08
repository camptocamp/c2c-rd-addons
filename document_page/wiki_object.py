# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2010 Camptocamp Austria (<http://www.camptocamp.at>)
#    Copyright (C) 2011 Camptocamp (<http://www.camptocamp.com>)
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

from openerp.osv import fields, osv


class document_page(osv.osv):
    _inherit = "document.page"

    _columns = {
        'model_ids': fields.many2many('ir.model', 'ir_model_wiki_rel', 'wiki_id', 'object_id', 'Object'),
    }

    def _activate_wiki_link(self, cr, uid, model_ids, context=None):
        self.pool.get('ir.model').write(cr, uid,
                                        model_ids,
                                        {'wiki_link': True},
                                        context=context)
        return True

    def create(self, cr, uid, vals, context=None):
        res_ids = super(document_page, self).create(cr, uid, vals, context=context)
        if vals.get('model_ids'):
            model_ids = self.read(cr, uid, res_ids, ['model_ids'], context=context)['model_ids']
            self._activate_wiki_link(cr, uid, model_ids, context=context)
        return res_ids

    def write(self, cr, uid, ids, vals, context=None):
        res = super(document_page, self).write(cr, uid, ids, vals, context=context)
        if vals.get('model_ids'):
            wikis = self.read(cr, uid, ids, ['model_ids'], context=context)
            model_ids = []
            [model_ids.extend(wiki['model_ids']) for wiki in wikis]
            self._activate_wiki_link(cr, uid, model_ids, context=context)
        return res

document_page()
