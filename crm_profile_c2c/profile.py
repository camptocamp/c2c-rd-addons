# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
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

class question(osv.osv):
    """ Question """

    _inherit="crm_profiling.question"
    _order = "sequence,name"
   
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name','sequence'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if not record['sequence']:
                seq = '[0000] '
            if record['sequence']:
                seq = '['+str(record['sequence']).zfill(4)+'] '
            name = seq +name
            res.append((record['id'],name ))
        return res

    _columns={
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying the questions"),
        }
question()


class answer(osv.osv):
    _inherit="crm_profiling.answer"
    _order = "sequence,name"
    _columns={
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying the answer"),
        # must be per partner 
        # 'comment' : fields.text("Comment"),
        }
        
answer()

class questionnaire(osv.osv):
    """ Questionnaire """

    _inherit="crm_profiling.questionnaire"
    
    def build_form(self, cr, uid, data, context=None):
        """
            @param self: The object pointer
            @param cr: the current row, from the database cursor,
            @param uid: the current user’s ID for security checks,
            @param data: Get Data
            @param context: A standard dictionary for contextual values """
        partner_id = context.get('active_id')
        query = """
        select name, id, sequence
          from crm_profiling_question
         where id in ( select question from profile_questionnaire_quest_rel where questionnaire = %s)
           and id not in (select question_id from partner_question_rel r, crm_profiling_answer a where r.partner = %s and a.id=r.answer)
         order by sequence,id"""
        res = cr.execute(query, (data['form']['questionnaire_name'],partner_id))
        result = cr.fetchall()
        quest_fields={}
        quest_form='''<?xml version="1.0"?>
            <form string="%s">''' % _('Questionnaire')
        for name, oid, sequence in result:
           
            quest_form = quest_form + '<field name="quest_form%d"/><newline/>' % (oid,)
            quest_fields['quest_form%d' % (oid,)] = {'string': name + ' ['+str(sequence).zfill(4)+']', 'type': 'many2one', \
                        'relation': 'crm_profiling.answer', 'domain': [('question_id','=',oid)] }
        quest_form = quest_form + '''</form>'''
        return quest_form, quest_fields


questionnaire()
