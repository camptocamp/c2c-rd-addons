select account_id,amn.date,amn.journal_id,amn.id,'neutral',amn.period_id,credit,'valid'
select aj.name,sum(credit)
  from account_move_line aml,
       account_move am,
       account_journal aj,
       account_move amn,  -- neutral move
       account_journal ajn
 where aj.id = am.journal_id
   and aj.name != 'Deloitte'
   and aml.move_id = am.id
   and am.period_id = amn.period_id
   and ajn.name = 'Deloitte neutral'
   and ajn.id = amn.journal_id
   and aml.state='valid' and account_id=18 and am.period_id=42
group by aj.name
;
select account_id,amn.date,amn.journal_id,amn.id,'neutral',amn.period_id,credit,am.state,aj.name,am.to_check,am.type,aml.move_id
--select aj.name,sum(credit)
  from account_move_line aml,
       account_move am,
       account_journal aj,
       account_move amn,  -- neutral move
       account_journal ajn
 where aj.id = am.journal_id
   and aj.name != 'Deloitte'
   and aml.move_id = am.id
   and am.period_id = amn.period_id
   and ajn.name = 'Deloitte neutral'
   and ajn.id = amn.journal_id
--   and am.state='posted'
   and aml.state='valid'
and account_id=18 and am.period_id=42
--group by aj.name
;

update account_move
set to_check=False
where to_check is  null
  and state='draft';

select am.id,am.period_id,am.ref,aml.name , am.date,aml.period_id,aml.date, aml.date- am.date
  from account_move am,
       account_move_line aml
 where am.id = aml.move_id
   and am.period_id != aml.period_id
order by am.ref;

update account_move_line aml
  set date = (select date from account_move am
                         where aml.move_id = am.id
                           and aml.date != am.date)
where id in (select aml.id from account_move am,
       account_move_line aml
 where am.id = aml.move_id
   and am.period_id != aml.period_id
   and aml.date != am.date);

update account_move amd
  set period_id = (select id from account_period where amd.date between date_start and date_stop)
where period_id != (select id from account_period where amd.date between date_start and date_stop);

update account_move_line amd
  set period_id = (select id from account_period where amd.date between date_start and date_stop)
where period_id != (select id from account_period where amd.date between date_start and date_stop)
  and date is not null;

