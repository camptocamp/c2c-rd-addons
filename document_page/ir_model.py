# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2011 Camptocamp SA
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
from openerp.tools.translate import _
from openerp import SUPERUSER_ID


class ir_model(osv.osv):
    _inherit = 'ir.model'

    _columns = {
        'wiki_link': fields.boolean('Wiki Link', help='If active, a link to a wiki page will be displayed on this model.'),
        'wiki_ids': fields.many2many('document.page', 'ir_model_wiki_rel', 'object_id', 'wiki_id', 'Wiki pages'),
    }

    def create(self, cr, uid, vals, context=None):
        res = super(ir_model, self).create(cr, SUPERUSER_ID, vals, context=context)
        if vals.get('wiki_link'):
            self._activate_wiki_link(cr, SUPERUSER_ID, res, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('wiki_link'):
            self._activate_wiki_link(cr, SUPERUSER_ID, ids, context=context)
        elif 'wiki_link' in vals and not vals['wiki_link']:
            self._deactivate_wiki_link(cr, SUPERUSER_ID, ids, context=context)
        return super(ir_model, self).write(cr, uid, ids, vals, context=context)

    def _activate_wiki_link(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        model_data_obj = self.pool.get('ir.model.data')
        act_window_obj = self.pool.get('ir.actions.act_window')
        for model in self.browse(cr, uid, ids, context=context):
            if model.wiki_link:
                continue
            vals = {'name': _('Wiki'),
                    'res_model': 'document.page',
                    'src_model': model.model,
                    'type' : 'ir.actions.act_window',
                    'domain': "[('model_ids', '=', %s)]" % (model.id,)}
            action_id = act_window_obj.create(cr, uid, vals, context=context)
            model_data_obj.ir_set(cr, uid,
                                  'action',
                                  'client_action_relate',
                                  _('Wiki'),
                                  [vals['src_model']],
                                  "ir.actions.act_window,%s" % (action_id,),
                                  replace=True,
                                  isobject=True,
                                  xml_id=False)
        return True

    def _deactivate_wiki_link(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]

        act_window_obj = self.pool.get('ir.actions.act_window')
        ir_values_obj = self.pool.get('ir.values')

        for model in self.browse(cr, uid, ids, context=context):
            if not model.wiki_link:
                continue
            action_ids = act_window_obj.search(cr, uid,
                                               [('type', '=', 'ir.actions.act_window'),
                                                ('res_model', '=', 'document.page'),
                                                ('src_model', '=', model.model)],
                                               context=context)
            ir_value_names = ["ir.actions.act_window,%s" % (action_id,) for action_id in action_ids]
            ir_values_ids = ir_values_obj.search(cr, uid,
                                                 [('model', '=', model.model),
                                                  ('value', 'in', ir_value_names)],
                                                 context=context)
            ir_values_obj.unlink(cr, SUPERUSER_ID, ir_values_ids, context=context)
            act_window_obj.unlink(cr, SUPERUSER_ID, action_ids, context=context)
            self.write(cr, SUPERUSER_ID, [model.id] ,{'wiki_link': None})

        return True

ir_model()
