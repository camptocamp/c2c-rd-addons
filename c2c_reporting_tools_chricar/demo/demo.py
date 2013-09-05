# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) Camptocamp SA
# Author: Arnaud WÃŒst
#
#
#    This file is part of the c2c_report_tools module.
#
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from c2c_reporting_tools.reports.standard_report import StandardReport
from c2c_reporting_tools.flowables.simple_row_table import *

from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle


from c2c_reporting_tools.translation import _
from c2c_reporting_tools.flowables.timebox_chart import  *
from datetime import datetime
from  time import gmtime


class mySandbox(StandardReport):     
    
    
    def get_story(self):
        story = []
        
        #
        # timebox chart demo
        #
        
        timebox = TimeBoxesChartBuilder('My timebox chart!', datetime(2008, 10, 01), datetime(2008, 11,15))
        
        id_1 = timebox.append_Y_item("my first item", indent=0)
        id_2 = timebox.append_Y_item("my second item", indent=3, color="#ff0000")
        
        timebox.add_period(id_1, datetime(2008, 10, 15), datetime(2008, 10,25), '#99cc00', 'my box')
        timebox.add_period(id_2, datetime(2008,  9, 20), datetime(2008, 10,10), 'red', 'another box')
        timebox.add_period(id_1, datetime(2008, 10, 20), datetime(2008, 10,25), '#0f0', 'my second box')
        
        story.append(timebox.get_flowable(self.width))
        
        
        
        #spacer
        story.append(Spacer(100,100))
        
        
               
        
        #
        # simple row table demo
        #
        builder = SimpleRowsTableBuilder("My simple table")
        
        #columns
        builder.add_text_column('My txt column')
        builder.add_num_column('My num column', "10%", 2)
        builder.add_date_column('My date column', format="%d.%m.%Y")        
        builder.add_money_column('my money column', width='200', currency='CHF', decimals=3)
                
        #row 1
        builder.add_text_cell('my first row')
        builder.add_num_cell(128)
        builder.add_date_cell(gmtime())
        builder.add_money_cell(12.2, 'CHF')

        #row 2
        builder.add_text_cell('my second row')
        builder.add_num_cell(10000)
        builder.add_date_cell(gmtime())
        builder.add_money_cell(33, 'CHF')
     
        #row 3
        builder.add_text_cell('<b>TOTAL</b>')
        builder.add_subtotal_num_cell()
        builder.add_empty_cell()
        builder.add_subtotal_money_cell('CHF')
        
        
        story.append(builder.get_table())        
        
        return story
    
    
    
mySandbox('report.sandbox_c2c_reporting_tools', "Sandbox with c2c reporting tools", 'hr.holidays', StandardReport.A4_PORTRAIT)        