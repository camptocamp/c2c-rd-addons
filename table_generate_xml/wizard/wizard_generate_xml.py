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
from osv import fields,osv
from tools.translate import _
import wizard
import pooler
from lxml import etree
import base64

class wizard_generate_xml(wizard.interface):

    _init_form = \
"""<?xml version="1.0"?>
<form string="Generate XML files">
  <separator colspan="4" string="Generate XML"/>
  <field 
    name="model_ids" 
    domain="[('state','=','base')]" 
    height="200" 
    width="500" 
    nolabel="1"/>
</form>
"""
    _init_fields = \
        { 'model_ids': 
            { 'string'   :'Model'
            , 'type'     :'many2many'
            , 'required' : True
            , 'relation' : 'ir.model' 
            }
        }
    _filter_form = \
"""<?xml version="1.0"?>
<form string="Select Filter">
  <field name="attribute" colspan="1" nolabel="1"/>
  <field name="compare" colspan="1" nolabel="1"/>
  <field name="value" colspan="2" nolabel="1"/>
</form>"""
    _filter_fields = \
        { 'attribute': 
            { 'string'    : 'Attribute'
            , 'type'      : 'selection'
            , 'selection' : []
            }
        , 'compare': 
            { 'string'    : 'Comparison'
            , 'type'      : 'selection'
            , 'selection' : 
                [ ('=','Equal')
                , ('!=', 'Not Equal')
                , ('>', 'Greater')
                , ('>=', 'Greater or Equal')
                , ('<', 'Less')
                , ('<=', 'Less or Equal')
                , ('in', 'In')
                ]
            }
        , 'value': 
            { 'string'    : 'Value'
            , 'type'      : 'char', 'size': 64
            }
        }

    def _remove_attachments(self, cr, uid, model, description, context=None):
        pool      = pooler.get_pool(cr.dbname)
        attachment_obj = pool.get('ir.attachment')
        att_ids = attachment_obj.search \
            ( cr, uid
            , [ ('res_model', '=', model._table_name)
              , ('res_id', '=', model.id)
              , ('description', '=', description)
              , ('datas_fname', '=', "%s.xml" % description)
              ]
            )
        if att_ids :
            attachment_obj.unlink(cr, uid, att_ids, context=context)
    # end def _remove_attachments

    def _manage_attachments(self, cr, uid, model, text, description, context=None):
        pool      = pooler.get_pool(cr.dbname)
        attachment_obj = pool.get('ir.attachment')
        self._remove_attachments(cr, uid, model, description, context=context)
        title = description.lower().replace(" ", "_")
        vals  = \
            { 'name'         : title
            , 'datas'        : text
            , 'datas_fname'  : "%s.xml" % description
            , 'res_model'    : model._table_name
            , 'res_id'       : model.id
            , 'description'  : description
            }
        attachment_obj.create(cr, uid, vals, context=context)
    # end def _manage_attachments

    def _add_filter(self, form) :
        if form and form['attribute'] and form['compare'] :
            if self.table_obj._columns[form['attribute']]._type in ("int", "float", "boolean") :
                value = form['value'].upper()
            else :
                value = "'%s'" % form['value']
            self._filters.append((form['attribute'], form['compare'], value))
    # end def _add_filter
        
    def _generate(self, cr, uid, data, res_get=False) :
        pool      = pooler.get_pool(cr.dbname)
        model_obj = pool.get('ir.model')
        if data['model'] == 'ir.model':
            model_id = data['ids'][0]
        else :
            model_id = data['form']['model_ids'][0][2][0] 
        model = model_obj.browse(cr, uid, model_id)
        self.table_obj = pool.get(model.model)
        if self.table_obj :
            self._add_filter(data['form'])
            xml = model_obj.generate_tree(cr, uid, self.table_obj, search=self._filters)
            self._manage_attachments \
                ( cr, uid
                , model
                , base64.encodestring(etree.tostring(xml, encoding="iso-8859-1", pretty_print=True))
                , self.table_obj._name
                )
        return {'result' : {'type' : 'state', 'state' : 'end'}}
    # end def _generate

    def _filter(self, cr, uid, data, res_get=False) :
        pool      = pooler.get_pool(cr.dbname)
        model_obj = pool.get('ir.model')
        if data['model'] == 'ir.model':
            model_id = data['ids'][0]
        else :
            model_id = data['form']['model_ids'][0][2][0]
        model = model_obj.browse(cr, uid, model_id)
        self.table_obj = pool.get(model.model)
        self._filter_fields['attribute']['selection'] = []
        if self.table_obj :
            for k,v in self.table_obj._columns.iteritems() :
                if v._type in ("many2many", "one2many", "related", "function") : continue
                if hasattr(v, "_fnct") and v._fnct : continue
                self._filter_fields['attribute']['selection'].append((k,k))
        return {'result' : {'type' : 'state', 'state' : 'add_filter'}}
    # end def _filter

    def _decide(self, cr, uid, data, res_get=False) :
        self._filters = []
        if data['model'] == 'ir.model':
            return 'filter'
        else :
            return 'form'
    # end def _decide

    def _filter2(self, cr, uid, data, res_get=False) :
        form = data['form']
        self._add_filter(form)
        if form['result']['state'] == 'add_filter' :
            return 'filter'
        else :
            return 'generate'
    # end def _filter2

    states = \
        { 'init' : 
            { 'actions' : []
            , 'result'  : 
              { 'type'       : 'choice'
              , 'next_state' : _decide
              }
            }
        , 'form' :
            { 'actions' : []
            , 'result'  : 
              { 'type'   : 'form'
              , 'arch'   : _init_form
              , 'fields' : _init_fields
              , 'state'  : [('end', 'Cancel'), ('generate', 'Generate'), ('filter', 'Filter')]
              }
            }
        , 'filter' :
            { 'actions' : [_filter]
            , 'result'  : 
              { 'type'   : 'form'
              , 'arch'   : _filter_form
              , 'fields' : _filter_fields
              , 'state'  : [('end', 'Cancel'), ('generate', 'Generate'), ('add_filter', 'Next Filter')]
              }
            }
        , 'add_filter' :
            { 'actions' : []
            , 'result'  : 
              { 'type'       : 'choice'
              , 'next_state' : _filter2
              }
            }
        , 'generate' :
            { 'actions' : []
            , 'result'  :
              { 'type'   : 'action'
              , 'action' : _generate
              , 'state'  : 'end'
              }
            }
        }
# end class wizard_generate_xml
wizard_generate_xml ('ir.model.wizard_generate_xml')
