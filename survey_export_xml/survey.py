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

class survey_survey(osv.osv):
    _inherit = 'survey.survey'

    _columns = {
        'template_id' : fields.many2one('xml.template', "Template"),  
      }
      
    def survey_export_xml(self, cr, uid, ids, context=None):
        """
        XML export of the structure using a template 
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of Survey IDs
        @param context: A standard dictionary for contextual values
        @return : Dictionary value for print survey form.
        """
        if context is None:
            context = {}
        for survey in self.browse(cr, uid, ids, context):
          if survey.template_id.id:
            xml_gen_obj = self.pool.get('xml.template')
            xml = xml_gen_obj.generate_xml(cr, uid, survey.template_id.id, survey = survey, _ = _)
            user_obj = self.pool.get('res.users')
            user_lang = user_obj.browse(cr, uid, uid, context=context).lang
            xml_gen_obj.attach_xml(cr, uid, survey.id  , survey , xml, 'questionaire_' + user_lang + '.xml', 'questionaire_' + user_lang + '.xml', description=False, pretty_print=True, context=None)
survey_survey()

class survey_question(osv.osv):
    _inherit = 'survey.question'

   
    def _get_type_sense(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for que in self.browse(cr, uid, ids):
            if len(que.answer_choice_ids) in (5,6):
                txt = 'FIVE_OPTIONS_QUESTION'
            elif len(que.answer_choice_ids) in (3,4):
                txt = 'THREE_OPTIONS_QUESTION'
            elif len(que.answer_choice_ids) == 2:
                txt = 'YES_NO_QUESTION'
            else:
                txt = '**ERROR**'
            res[que.id] = txt   
        return res
               
        
 
    _columns = {
        'type_sense' : fields.function(_get_type_sense, method=True, string="Type Sense")
      }

survey_question()
