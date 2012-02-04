-- duplicates
-- drop table c2c_budget_line_duplicates;
create table c2c_budget_line_duplicates
as
select * from c2c_budget_line bl
 where state = 'product' 
   and budget_version_id in(4, 5,6)
   and  exists ( select 'x' from c2c_budget_line bl2
                  where bl2.id < bl.id
                    and bl2.budget_item_id = bl.budget_item_id
                    and bl2.budget_version_id = bl.budget_version_id
                    and bl2.amount = bl.amount
                    and bl2.date_planning = bl.date_planning
                    and bl2.period_id = bl.period_id
                    and bl2.date_due = bl.date_due) 
