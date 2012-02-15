
-- constant values have to replaced by paramters
 
insert into c2c_budget_line(amount,analytic_account_id,budget_item_id,budget_version_id,currency_id,name,period_id)
select -sum(l.debit-l.credit),l.analytic_account_id,b.id,v.id,c.id,'VJ Summe',np.id
  from account_move_line l,
       account_account a,
       c2c_budget_item b,
       c2c_budget_version v,
       account_period np,
       account_period p,
       account_fiscalyear f,
       res_currency c
where a.id = account_id
  and b.code = a.code
  and v.name = 'Bud 2011 ChriCar'
  and p.id = period_id
  and np.date_start = p.date_start + interval '1 year'
  and f.id = p.fiscalyear_id
  and f.code = '2010'
  and c.code ='EUR'
group by l.analytic_account_id,b.id,v.id,c.id,np.id; 

