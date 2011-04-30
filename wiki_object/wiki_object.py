# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2010 Camptocamp Austria (<http://www.camptocamp.at>)
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


from osv import fields, osv
import sys




class wiki_wiki(osv.osv):
    _inherit = "wiki.wiki"
    _columns = {
        'model_ids': fields.many2many('ir.model', 'ir_model_wiki_rel', 'wiki_id', 'object_id', 'Object')
    }


    def unsubscribe(self, cr, uid, ids, *args):
      if ids:
        for wiki in self.browse(cr, uid, ids):
          if wiki.model_ids:
           for model in wiki.model_ids :
            val_obj = self.pool.get('ir.values')
            
            wiki_id=self.pool.get('ir.actions.act_window').search(cr, uid, [('src_model','=',model.model),('res_model','=','wiki.wiki'),('name','=','Wiki')])
            
            if wiki_id:
                print >> sys.stderr, 'wiki del', wiki_id    
                self.pool.get('ir.actions.act_window').unlink(cr, uid,wiki_id )
                value = "ir.actions.act_window" + ',' + str(wiki_id[0])

            
      return True

    def subscribe(self, cr, uid, ids, *args):
      if ids:
        # FIXME do nt know how to call next line
        #self.unsubscribe(self, cr, uid, ids, False)
        for wiki in self.browse(cr, uid, ids):

          if wiki.model_ids:
           obj_model = self.pool.get('ir.model.data')
           for model in wiki.model_ids :
            val={
                 "name":'Wiki',
                 "res_model":'wiki.wiki',
                 "src_model": model.model,
                 "domain"   : "[('id','=',"+str(wiki.id)+")]"
            }
            action_id= self.pool.get('ir.actions.act_window').create(cr, uid, val)
            print >> sys.stderr, 'wiki ins', action_id, val
            keyword = 'client_action_relate'
            value = 'ir.actions.act_window,' + str(action_id)
            res = obj_model.ir_set(cr, uid, 'action', keyword, 'Wiki_' + model.model, [model.model], value, replace=True, isobject=True, xml_id=False)

      return True

wiki_wiki()

