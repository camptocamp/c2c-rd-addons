--delete from c2c_budget_item;

-- ToDo add only missing !!!
 
insert into c2c_budget_item(active,code,name,style,type)
select True,code,name,'normal','normal'
from account_account
where type = 'other'
and user_type in (select id from account_account_type 
                   where code in ('income','expense')
;

-- we should insert inly views which have children with user_type income,exense
-- ToDo - in python should be easier
-- sql statemtns below

-- fill c2c_budget_item_account_rel
insert into c2c_budget_item_account_rel(account_id,budget_item_id)
select a.id,b.id
  from account_account a,
       c2c_budget_item b
 where a.code = b.code;

-- these are incomplete helper statements in sql
-- insert all views
insert into c2c_budget_item(active,code,name,style,type)
select True,code,name,'bold','view'
from account_account
where type = 'view'
; 

-- rebuid parent-child structure as for accounts
update c2c_budget_item u
set parent_id = (
select distinct bp.id
  from c2c_budget_item b,
       account_account a,
       account_account ap,
       c2c_budget_item bp
 where a.code = u.code
   and ap.id  = a.parent_id
   and bp.code = ap.code)
where exists (select bp.id
  from c2c_budget_item b,
       account_account a,
       account_account ap,
       c2c_budget_item bp
 where u.code = a.code
   and ap.id  = a.parent_id
   and bp.code = ap.code)
;

delete from c2c_budget_item
 where type = 'view'
   and id not in (select parent_id from c2c_budget_item 
                   where type = 'normal');
