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
from osv import fields, osv
from tools.translate import _
import base64
from lxml import etree

class wizard_generate_xml(osv.osv_memory):
    _name = "ir.model.generate.xml"
    _description = "Generate XML"

#    _init_form = \
#"""<?xml version="1.0"?>
#<form string="Generate XML files">
#  <separator colspan="4" string="Generate XML"/>
#  <field 
#    name="model_ids" 
#    domain="[('state','=','base')]" 
#    height="200" 
#    width="500" 
#    nolabel="1"/>
#</form>
#"""
#    _init_fields = \
#        { 'model_ids': 
#            { 'string'   :'Model'
#            , 'type'     :'many2many'
#            , 'required' : True
#            , 'relation' : 'ir.model' 
#            }
#        }
#    _filter_form = \
#"""<?xml version="1.0"?>
#<form string="Select Filter">
#  <field name="attribute" colspan="1" nolabel="1"/>
#  <field name="compare" colspan="1" nolabel="1"/>
#  <field name="value" colspan="2" nolabel="1"/>
#</form>"""
#    _filter_fields = \
#        { 'attribute': 
#            { 'string'    : 'Attribute'
#            , 'type'      : 'selection'
#            , 'selection' : []
#            }
#        , 'compare': 
#            { 'string'    : 'Comparison'
#            , 'type'      : 'selection'
#            , 'selection' : 
#                [ ('=','Equal')
#                , ('!=', 'Not Equal')
#                , ('>', 'Greater')
#                , ('>=', 'Greater or Equal')
#                , ('<', 'Less')
#                , ('<=', 'Less or Equal')
#                , ('in', 'In')
#                ]
#            }
#        , 'value': 
#            { 'string'    : 'Value'
#            , 'type'      : 'char', 'size': 64
#            }
#        }

    _selection = \
        [ ('=',  _('Equal'))
        , ('!=', _('Not Equal'))
        , ('>',  _('Greater'))
        , ('>=', _('Greater or Equal'))
        , ('<',  _('Less'))
        , ('<=', _('Less or Equal'))
        , ('in', _('In'))
        ]
    _columns = \
        { 'attribute' : fields.char     ('Attribute', size=64, required=True)
        , 'compare'   : fields.selection(_selection, 'Comparison', required=True)
        , 'value'     : fields.char     ('Value', size=64, required=True)
        }
    _defaults = \
        { 'attribute' : lambda *a: 'id'
        , 'compare'   : lambda *a: '='
        , 'value'     : lambda *a: ''
        }
    
    _filters = []

    def _manage_attachments(self, cr, uid, model, text, name, description, context=None):
        pool = pooler.get_pool(cr.dbname)
        attachment_obj = pool.get('ir.attachment')
        title = name.lower().replace(" ", "_")
        vals  = \
            { 'name'         : title
            , 'datas'        : text
            , 'datas_fname'  : "%s.xml" % name
            , 'res_model'    : model._table_name
            , 'res_id'       : model.id
            , 'description'  : "%s" % (description, )
            }
        attachment_obj.create(cr, uid, vals, context=context)
    # end def _manage_attachments

    def _table_obj(self, cr, uid, context) :
        model_obj = self.pool.get('ir.model')
        ids = context['active_ids']
        if len(ids) > 1 :
            raise osv.except_osv \
                ( _('Data Error !')
                , _('You can only select a single table for generation')
                )
        return model_obj.browse(cr, uid, ids[0]), self.pool.get(model.model)
    # end def _table_obj

    def add_filter(self, cr, uid, ids, context) :
        print "add_filter", context, self._filters ######################
        model, table_obj = self._table_obj(cr, uid, context)
        if context and context['attribute'] and context['compare'] :
            if table_obj._columns[context['attribute']]._type in ("int", "float", "boolean") :
                value = context['value'].upper()
            else :
                value = "'%s'" % context['value']
            self._filters.append((context['attribute'], context['compare'], value))
    # end def add_filter
        
    def generate(self, cr, uid, ids, context) :
        print "generate", context, self._filters ######################
        model_obj = self.pool.get('ir.model')
        model, table_obj = self._table_obj(cr, uid, context)
        if table_obj is not None and not isinstance(table_obj, osv.osv_memory) :
            xml = model_obj.generate_tree(cr, uid, table_obj, search=self._filters)
            self._manage_attachments \
                ( cr, uid
                , model
                , base64.encodestring(etree.tostring(xml, pretty_print=True))
                , table_obj._name
                , " and ".join('"%s" %s %s' % (s[0], s[1], s[2]) for s in self._filters)
                )
        return {'type' : 'ir.actions.act_window_close'}
    # end def generate

    def filter(self, cr, uid, data, res_get=False) :
        print "filter" ######################
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
                if v._type in ("many2many", "one2many", "related", "function") : 
                    continue
                if hasattr(v, "_fnct") and v._fnct : continue
                self._filter_fields['attribute']['selection'].append((k,k))
        return {}
    # end def filter

    def decide(self, cr, uid, ids, context) :
        print "decide", context ######################
        self._filters = []
        if context['model'] == 'ir.model':
            return 'filter'
        else :
            return 'form'
    # end def decide

    def decide2(self, cr, uid, data, res_get=False) :
        print "decide2" ######################
        form = data['form']
        self.add_filter(form)
        return 'filter'
    # end def decide2

# end class wizard_generate_xml
wizard_generate_xml ()
