# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    24-MAY-2011 (GK) created
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/> or
# write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################
import wizard
import osv
import pooler
import tools
from tools.translate import _
import logging

class wizard_remove_duplicate(wizard.interface):
    _logger = logging.getLogger(__name__)

    
    _init_model_form = \
'''<?xml version="1.0"?>
<form string="Select model">
  <field name="model"/>
</form>'''
    
    _init_model_fields = \
        { 'model': 
            { 'string'   : 'Model'
            , 'type'     : 'many2one'
            , 'relation' : 'ir.model'
            , 'help'     : 'Select table where you want to merge entries'
            , 'required' : True
            }
        }
    _init_old_form = \
'''<?xml version="1.0"?>
<form string="Select two (or more) duplicates">
  <field name="old_ids" nolabel="1" width="600" height="300"/>
</form>'''
    
    _init_old_fields = \
        { 'old_ids': 
            { 'string'   : ''
            , 'type'     : 'many2many'
            , 'required' : True
            }
        }
    _init_new_form = \
'''<?xml version="1.0"?>
<form string="Select single remaining entry">
  <field name="new_id" nolabel="1" width="600"/>
</form>'''    
    _init_new_fields = \
        { 'new_id': 
            { 'string'   : ''
            , 'type'     : 'many2one'
            , 'required' : True
            }
        }
    
    def _decide(self, cr, uid, data, res_get=False) :
        if data['model'] == 'ir.model' :
            return 'old_form'
        else :
            return 'model_form'
    # end def _decide

    def _remove(self, cr, uid, data, res_get=False) :
        if data['model'] == 'ir.model' :
            id = data['ids'][0]
        else :
            id = data['form']['model']
        new_id  = data['form']['new_id']
        self.old_ids.remove(new_id)
        self._remove_from_table(cr, uid, id, new_id, self.old_ids)
        return {}
    # end def _remove

    def _select_duplicates(self, cr, uid, data, res_get=False) :
        self.old_ids = data['form']['old_ids'][0][2]
        self._init_new_fields['new_id']['ids'] = self.old_ids
        self._init_new_fields['new_id']['domain'] = "[('id','in',%s)]" % self.old_ids
        return {}
    # end def _select_duplicates

    def _set_relation(self, cr, uid, data, res_get=False) :
        pool      = pooler.get_pool(cr.dbname)
        model_obj = pool.get('ir.model')
        if data['model'] == 'ir.model':
            model_id = data['ids'][0]
        else :
            model_id = data['form']['model'] 
        model = model_obj.browse(cr, uid, model_id)
        self.table_obj = pool.get(model.model)
        self._init_old_fields['old_ids']['relation'] = model.model
        self._init_new_fields['new_id']['relation'] = model.model
        return {}
    # end def _set_relation

    def _remove_from_attachment(self, cr, uid, model_name, new_id, old_ids) :
        pool    = pooler.get_pool(cr.dbname)
        att_obj = pool.get('ir.attachment')
        for old_id in old_ids :
            ids = att_obj(cr, uid, [('res_model', '=', model_name),('res_id', '=', old_id)])
            att_obj.write(cr, uid, ids, {'res_id' : new_id})
        
    # end def _remove_from_attachment

    def _remove_from_table(self, cr, uid, id, new_id, old_ids) :
        pool      = pooler.get_pool(cr.dbname)
        model_obj = pool.get('ir.model')
        model     = model_obj.browse(cr, uid, id)
        table_obj = pool.get(model.model)

        test_id = table_obj.browse(cr, uid, new_id)
        if not (test_id and test_id.id == new_id) :
            raise wizard.except_wizard \
                ( _('Input Error !')
                , _('New ID %s is not contained in model %s.') % (new_id, model.model)
                )
        
        test_ids = table_obj.browse(cr, uid, old_ids)
        if not (test_ids and set(x.id for x in test_ids) == set(old_ids)) :
            raise wizard.except_wizard \
                ( _('Input Error !')
                , _('Old IDs %s are not contained in model %s.') % (old_ids, model.model)
                )
        for m in model_obj.browse(cr, uid, model_obj.search(cr, uid, [('model', '!=', model.model)])) :
            t_obj = pool.get(m.model)
            if not t_obj : continue
            for name, spec in t_obj._columns.items() :
                if "2one" in spec._type and spec._obj == model.model :
                    t_obj.write(cr, uid, old_ids, {name : new_id})
                if "reference" == spec._type :
                    for old_id in old_ids :
                        ids = t_obj.search(cr, uid, [(name, '=', '%s,%s' % (model.model, old_id))])
                        t_obj.write(cr, uid, ids, {name : '%s,%s' % (model.model, new_id)})
        self._remove_from_attachment(cr, uid, model.model, new_id, old_ids)
        t_obj.unlink(cr, uid, old_ids)
    # end def _remove_from_table

    states = \
        { 'init' : 
            { 'actions' : []
            , 'result'  : 
              { 'type'       : 'choice'
              , 'next_state' : _decide
              }
            }
        , 'model_form' :
            { 'actions' : []
            , 'result'  : 
              { 'type'   : 'form'
              , 'arch'   : _init_model_form
              , 'fields' : _init_model_fields
              , 'state'  : [('end', 'Cancel'), ('old_form', 'Select Set of Duplicates')]
              }
            }
        , 'old_form' :
            { 'actions' : [_set_relation]
            , 'result'  : 
              { 'type'   : 'form'
              , 'arch'   : _init_old_form
              , 'fields' : _init_old_fields
              , 'state'  : [('end', 'Cancel'), ('new_form', 'Select Remaining')]
              }
            }
        , 'new_form' :
            { 'actions' : [_select_duplicates]
            , 'result'  : 
              { 'type'   : 'form'
              , 'arch'   : _init_new_form
              , 'fields' : _init_new_fields
              , 'state'  : [('end', 'Cancel'), ('remove', 'Remove Duplicates')]
              }
            }
        , 'remove' :
            { 'actions' : []
            , 'result'  :
              { 'type'   : 'action'
              , 'action' : _remove
              , 'state'  : 'end'
              }
            }
        }
# end class wizard_remove_duplicate
wizard_remove_duplicate('ir.wizard_remove_duplicate')
