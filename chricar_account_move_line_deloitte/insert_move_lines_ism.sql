
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
   and ac.code = d.account
;

insert into account_analytic_line(
account_id
,amount
,date
,general_account_id
,journal_id
--,move_id
,name)
-- account
select get_analytic_id(d.analytic_account),
-d.amount,
am.date,
ac.id,
aaj.id,
--am.id,
d.description
  from chricar_account_move_line_deloitte d,
       account_journal aj,
       account_analytic_journal aaj,
       account_move am,
       account_account ac
 where aj.name = 'Deloitte'
   and aaj.name = 'Deloitte'
   and am.journal_id = aj.id
   and am.name = d.symbol||'-'||d.name
   and am.date = to_date(d.date,'DD.MM.YY')
   and ac.code = d.account
   and get_analytic_id(d.analytic_account) is not null ;




insert into account_move_line(account_id,date,journal_id,move_id,name,period_id,analytic_account_id, credit,debit,state)
select account_id,amn.date,amn.journal_id,amn.id,'neutral',amn.period_id, analytic_account_id,
   case when sum(case when debit is null then 0 else debit end) > 0 then  sum(case when debit is null then 0 else debit end) else 0 end,
   case when sum(case when debit is null then 0 else debit end) < 0 then -sum(case when debit is null then 0 else debit end) else 0 end,
  'valid'
  from account_move_line aml,
       account_move am,
       account_journal aj,
       account_move amn,  -- neutral move
       account_journal ajn
 where aj.id = am.journal_id
   and aj.name not in ( 'Deloitte')
   and aml.move_id = am.id
   and am.period_id = amn.period_id
   and ajn.name = 'Deloitte neutral'
   and ajn.id = amn.journal_id
   and aml.state='valid'
   --and am.state='posted'
 group by account_id,amn.date,amn.journal_id,amn.id,amn.period_id,analytic_account_id
 having sum(case when debit is null then 0 else debit end) != 0
union all
select account_id,amn.date,amn.journal_id,amn.id,'neutral',amn.period_id, analytic_account_id,
   case when sum(case when credit is null then 0 else credit end) < 0 then -sum(case when credit is null then 0 else credit end) else 0 end,
   case when sum(case when credit is null then 0 else credit end) > 0 then  sum(case when credit is null then 0 else credit end) else 0 end,
   'valid'
  from account_move_line aml,
       account_move am,
       account_journal aj,
       account_move amn,  -- neutral move
       account_journal ajn
 where aj.id = am.journal_id
   and aj.name not in ( 'Deloitte')
   and aml.move_id = am.id
   and am.period_id = amn.period_id
   and ajn.name = 'Deloitte neutral'
   and ajn.id = amn.journal_id
   and aml.state='valid'
   --and am.state='posted'
 group by account_id,amn.date,amn.journal_id,amn.id,amn.period_id,analytic_account_id
having sum(case when credit is null then 0 else credit end) != 0
;

