 
-- orphaned c2c_budget_lines
select * from c2c_budget_line bl
 where state = 'product' 
   and bl.id not in  ( select budget_line_id from chricar_budget_lines_sales 
                       union 
                       select budget_line_id from chricar_budget_lines_production) 
;
/*
delete from c2c_budget_line bl
 where state = 'product' 
   and bl.id not in  ( select budget_line_id from chricar_budget_lines_sales 
                       union 
                       select budget_line_id from chricar_budget_lines_production) 
;
*/
