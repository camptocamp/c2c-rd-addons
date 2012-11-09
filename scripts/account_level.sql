-- not very sophisticated :-(

update account_account set level = 0;
update account_account a set level = level +1 where parent_id is null and level= 0;
update account_account a set level = 2  where parent_id in (select id from account_account b where  b.level = 1);
update account_account a set level = 3  where parent_id in (select id from account_account b where  b.level = 2);
update account_account a set level = 4  where parent_id in (select id from account_account b where  b.level = 3);
update account_account a set level = 5  where parent_id in (select id from account_account b where  b.level = 4);
update account_account a set level = 6  where parent_id in (select id from account_account b where  b.level = 5);
update account_account a set level = 7  where parent_id in (select id from account_account b where  b.level = 6);
update account_account a set level = 8  where parent_id in (select id from account_account b where  b.level = 7);
update account_account a set level = 9  where parent_id in (select id from account_account b where  b.level = 8);
update account_account a set level = 10  where parent_id in (select id from account_account b where  b.level = 9);
update account_account a set level = 11  where parent_id in (select id from account_account b where  b.level = 10);
update account_account a set level = 12  where parent_id in (select id from account_account b where  b.level = 11);


update c2c_budget_item set level = 0;
update c2c_budget_item set level = level +1 where parent_id is null and level= 0;

update c2c_budget_item set level = 2  where parent_id in (select id from c2c_budget_item b where  b.level = 1);
update c2c_budget_item set level = 3  where parent_id in (select id from c2c_budget_item b where  b.level = 2);
update c2c_budget_item set level = 4  where parent_id in (select id from c2c_budget_item b where  b.level = 3);
update c2c_budget_item set level = 5  where parent_id in (select id from c2c_budget_item b where  b.level = 4);
update c2c_budget_item set level = 6  where parent_id in (select id from c2c_budget_item b where  b.level = 5);
update c2c_budget_item set level = 7  where parent_id in (select id from c2c_budget_item b where  b.level = 6);
update c2c_budget_item set level = 8  where parent_id in (select id from c2c_budget_item b where  b.level = 7);
update c2c_budget_item set level = 9  where parent_id in (select id from c2c_budget_item b where  b.level = 8);
update c2c_budget_item set level = 10  where parent_id in (select id from c2c_budget_item b where  b.level = 9);
update c2c_budget_item set level = 11  where parent_id in (select id from c2c_budget_item b where  b.level = 10);


