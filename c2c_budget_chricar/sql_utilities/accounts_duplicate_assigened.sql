-- duplicate assignments
select  account_id from c2c_budget_item_account_rel group by account_id having count(*) >1;
 
