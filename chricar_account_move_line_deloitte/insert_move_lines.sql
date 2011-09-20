
/* insert new move_lines*/

insert into account_move_line(account_id,date,journal_id,move_id,name,period_id,analytic_account_id,debit,credit,state)
-- no tax code account
select ac.id,am.date,am.journal_id,am.id,d.description,am.period_id, get_analytic_id(d.analytic_account),
       case when d.amount > 0 then d.amount else 0 end,
       case when d.amount < 0 then -d.amount else 0 end,
       'valid'
  from chricar_account_move_line_deloitte d,
       account_journal aj,
       account_move am,
       account_account ac
 where aj.name = 'Deloitte'
   and am.journal_id = aj.id
   and am.name = d.symbol||'-'||d.name
   and am.date = to_date(d.date,'DD.MM.YY')
;



