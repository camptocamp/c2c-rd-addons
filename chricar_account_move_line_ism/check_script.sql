select account_id,p.name , period_id,journal_id,sum(debit-credit) 
from account_move_line l,account_period p 
where p.id=l.period_id and l.state='valid' 
group by account_id,period_id,journal_id,p.name 
order by account_id,period_id,journal_id;


create view chricar_deloite_compare
as
select account_id,p.name , period_id,sum(debit-credit)  as bal11, 0 as bal12, 0 as bal7
from account_move_line l,account_period p 
where p.id=l.period_id and l.state='valid'  and journal_id = 11
group by account_id,period_id,p.name 
union 
select account_id,p.name , period_id,0 as bal11,-sum(debit-credit) as bal12, 0 as bal7
from account_move_line l,account_period p 
where p.id=l.period_id and l.state='valid'  and journal_id = 12
group by account_id,period_id,p.name 

union 
select account_id,p.name , period_id,0 as bal11,0 as bal12,sum(debit-credit) as bal7
from account_move_line l,account_period p 
where p.id=l.period_id and l.state='valid'  and journal_id = 7
group by account_id,period_id,p.name 
order by account_id,period_id
;

select account_id,a.name, c.name , period_id, sum(bal11) as bal11,sum(bal12) as bal12,sum(bal7) as bal7, sum(bal7-bal11) as Diff
from chricar_deloite_compare c, account_account a
where a.id = c.account_id
  and c.name like '2012%'
--  and c.name not in ('201201','201202','201203','201204')
group by account_id,a.name,c.name , period_id
having (sum(bal7) !=0 and ( sum(bal11) !=0 or sum(bal12) !=0))
and (sum(bal7) != sum(bal11))
;

select account_id,a.name, c.name , period_id, sum(bal11) as bal11,sum(bal12) as bal12,sum(bal7) as bal7
from chricar_deloite_compare c, account_account a
where a.id = c.account_id
  and c.name like '2012%'
  and c.name not in ('201201','201202','201203','201204')
group by account_id,a.name,c.name , period_id
having  (sum(bal7) != sum(bal11))
;
