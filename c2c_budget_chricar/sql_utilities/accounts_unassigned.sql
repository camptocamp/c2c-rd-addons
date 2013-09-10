-- check if all income/expense accounts are assigned
select a.id, a.code, a.name,t.name,t.code
 from account_account a, account_account_type t
where a.user_type = t.id
  and t.code in ('income','expense')
  and a.id not in (select account_id from c2c_budget_item_account_rel)
  and exists (select 'x' from account_move_line m where m.account_id=a.id);
 
