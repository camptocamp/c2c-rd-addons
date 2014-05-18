# -*- coding: utf-8 -*- 
##############################################################################
#
# Copyright (c) ChriCar Beteiligungs- und Beratungs- GmbH - http://www.camptocamp.com
# Author: Ferdinand Gassauer
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


        
from openerp.osv import fields, osv


class c2c_budget_item(osv.osv):
    """ camptocamp budget item. This is a link between 
    budgets and financial accounts. """
    _inherit = "c2c_budget.item"

    def init(self, cr):
       # this is copied from a working solution
       # should be rewritten in python
       # FIXME - this works only on potgresql 9.1 upwards            
       #try:
       #   cr.execute("""
       #   create extension if not exists tablefunc;
       #   """)
       #except:
          # must be created manualy using - replace version and path !!!
          # \i /usr/share/postgresql/8.4/contrib/tablefunc.sql
#          pass

       cr.execute("""
create or replace function c2c_budget_sequence()
   RETURNS void AS $$
   DECLARE
      level_p integer;
      id_p integer;
      parent_id_p integer;
      start_pos_p varchar;
      r record;
      o record;
   BEGIN
      update c2c_budget_item set sequence = 0;
      select into start_pos_p id::varchar from c2c_budget_item where parent_id is null;

-- postgres tablefunc.sql must be loaded

          CREATE EXTENSION  if not exists tablefunc;
          create table c2c_budget_item_sequence as
          SELECT * FROM connectby('c2c_budget_item','id','parent_id',        'code', start_pos_p , 0, '~')
                AS t(keyid integer, parent_keyid integer, level int, branch text, pos int);

          update c2c_budget_item i
             set sequence = ( select pos from c2c_budget_item_sequence where keyid = i.id);

          drop table c2c_budget_item_sequence;

   RETURN ;
   END;
$$ LANGUAGE plpgsql;
          """)

       cr.execute("""
          select  c2c_budget_sequence();
          """)
      
c2c_budget_item()
