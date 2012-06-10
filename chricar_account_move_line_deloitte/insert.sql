/*
Task:
* the accounting company sends data (move_lines) as xls named
<company_name>_Buchungszeilen_<period_from>-<period_to>_<fiscal_year>.xls
** the name is indicative and might vary slightely from company to company and month to month
** the files are stored in directories
*** Deloitte/Company/fiscal year
* the sheet name is "Protokoll Belegkreise"
** some column headers have trailing blanks which have to be removed.
** only lines with filed account not null must be imported.
** remove empty/invisible column J
** decimal digits !! decimal separator !
* currently the conversion xls to csv is done manualy and the cvs is imported into
chricar_account_move_line_deloitte
* the scripts below are used to create the necesary OpenERP resources and neutralized those moves created by OPENERP itself
** it's sort of a hybrid system - currenlty the accountant does all the work but will gradually switch using OpenERP as main accoutning system.

missing:
* error handling
* crawl through the directories and import new/altered xls files (later - because want to wait for better multi company support in 5.2)

to be discussed:
* how to import xls
** using http://www.python-excel.org/
** using http://search.cpan.org/~ken/xls2csv-1.06/script/xls2csv
*/
/*
fill the table with all available symbols
- manually delete the  one you want to have imported
or
- set start stop date for deny

insert into chricar_account_move_import_deny(code,name)
select distinct symbol,symbol from chricar_account_move_line_deloitte;

update chricar_account_move_import_deny
   set date_start = to_date('20091001','YYYYMMDD');

*/
/* create default tax codes
insert into chricar_account_tax_code_deloitte(code,name,percent,account_id)
select distinct tax_code,'St '||substr(tax_code,length(tax_code)-1),substr(tax_code,length(tax_code)-1)::numeric/100,801
 from chricar_account_move_line_deloitte
where tax_code is not null;

*/

/*
xls2csv
- remove trailing spaces in column header
- remove empty/invisible column J
*/


/*
* replace year by auto detecting the periods from move_lines in xls
* keep this as function ?
** faster than OpenERP ?
** easier to extend (for me)
*/

/* function to return analytic_account_id */
CREATE OR REPLACE FUNCTION  get_analytic_id(analytic_code varchar)
   RETURNS integer AS $$

   DECLARE
   id_p integer;
   BEGIN
   select into id_p id from account_analytic_account
    where code = analytic_code;
   RETURN id_p;
   END;
$$ LANGUAGE plpgsql;

/* select get_analytic_id('1012'); */

CREATE OR REPLACE FUNCTION  import_doloitte_moves_function(year_i varchar)
   RETURNS void AS $$
   BEGIN

/* missing accounts*/
/*
select account from chricar_account_move_line_deloitte where substr(account,1,1) not in ('2','3')
       except select code from account_account
union
select counter_account from chricar_account_move_line_deloitte where substr(counter_account,1,1) not in ('2','3')
       except select code from account_account
;
*/
/* insert missing analytic accounts*/

UPDATE chricar_account_move_line_deloitte set analytic_account = null where analytic_account='';

insert into account_analytic_account(code,name,company_id,state,type)
select distinct analytic_account,analytic_account,c.id,'open','normal'
  from chricar_account_move_line_deloitte d,
       res_company c
where d.analytic_account is not null
  and not exists (select code from account_analytic_account where code = d.analytic_account);


/* insert missing accounts*/
insert into account_account(code,company_id,currency_mode,name,type,user_type,active,parent_left,parent_right)
select distinct account,1,'current','Deloitte neu','other',
       case when substr(account,1,1) = '2' then 7
            when substr(account,1,1) = '3' then 7
            when substr(account,1,1) = '4' then 4
            when substr(account,1,1) = '7' then 5
            when substr(account,1,1) = '8' then 5
            when substr(account,1,1) = '9' then 9
       end as user_type,true,0,1
  from chricar_account_move_line_deloitte
 where length(account) < 5
   and account not in (select code from account_account where type != 'view');

/* insert missing counter accounts*/
insert into account_account(code,company_id,currency_mode,name,type,user_type,active,parent_left,parent_right)
select distinct counter_account,1,'current','Deloitte neu','other',
       case when substr(counter_account,1,1) = '2' then 7
            when substr(counter_account,1,1) = '3' then 7
            when substr(counter_account,1,1) = '4' then 4
            when substr(counter_account,1,1) = '7' then 5
            when substr(counter_account,1,1) = '8' then 5
            when substr(counter_account,1,1) = '9' then 9
        end as user_type,true,0,1
  from chricar_account_move_line_deloitte
 where length(counter_account) < 5
   and counter_account not in (select code from account_account where type != 'view');

/* optionally update account name from opening  balance deloitte */
/*
update account_account set name =( select name from chricar_account_opening_deloitte where code=account)
 where code in (select account from chricar_account_opening_deloitte)
   and name != ( select name from chricar_account_opening_deloitte where code=account)
;
*/

/* optionally check if opening balance is 0*/
/* currently a problem - is not 0 */
/*
select sum(amount) from chricar_account_opening_deloitte;
*/

/* optionally insert opening balance into chricar_account_move_line_deloitte
Do not run this statement if the above does not return 0 - except you know what you are doing
this is a one time action
*/
-- delete from chricar_account_move_line_deloitte where name='20081231';
/*
insert into chricar_account_move_line_deloitte(account,date,symbol,name,counter_account,amount,description)
select account,replace(date,'2008','08'),'IN','20081231',null,amount,'Saldenübernahme'
  from chricar_account_opening_deloitte;
*/


/* delete Deloite moves of the year (periods) which are imported
should be autodetected from the xls periods
*/

/*
MUST NOT PROCEED if next statement returns lines !!!!
*/
select tax_code as "missing tax code"
  from chricar_account_move_line_deloitte
 where tax_code is not null
except select code from chricar_account_tax_code_deloitte;




delete from account_move
 where journal_id in (select id from account_journal where name ='Deloitte')
   and period_id in ( select distinct p.id from account_period p,
                                       chricar_account_move_line_deloitte d
                                 where to_date(d.date,'DD.MM.YY') between p.date_start and p.date_stop)
;

/* show excluded symbolos*/
select * from chricar_account_move_import_deny;


/* insert new moves*/
insert into account_move(date,journal_id,name,period_id,state)
select distinct to_date(d.date,'DD.MM.YY'),aj.id,symbol||'-'||d.name, ap.id,'draft'
  from chricar_account_move_line_deloitte d,
       account_journal aj,
       account_period ap
 where aj.name = 'Deloitte'
   and to_date(date,'DD.MM.YY') between ap.date_start and ap.date_stop
   and symbol not in (select code
                        from chricar_account_move_import_deny
                       where to_date(date,'DD.MM.YY') between case when date_start is null then to_date(date,'DD.MM.YY') else date_start end
                                                          and case when date_stop  is null then to_date(date,'DD.MM.YY') else date_stop end);


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
       account_account ac,
       account_account_type at
 where aj.name = 'Deloitte'
   and am.journal_id = aj.id
   and am.name = d.symbol||'-'||d.name
   and am.date = to_date(d.date,'DD.MM.YY')
   and ac.code = case when d.account = substr(d.account,1,4) then d.account
                      when length(d.account) > 4 then substr(d.account,1,2)||'00 Deloitte'
                 end
   and at.id = ac.user_type
   and (at.close_method != 'none' or tax_code is null)
union all
-- tax code account - net
select ac.id,am.date,am.journal_id,am.id,d.description,am.period_id, get_analytic_id(d.analytic_account),
       case when d.amount > 0 then round( d.amount / (1+tc.percent),2) else 0 end,
       case when d.amount < 0 then round(-d.amount / (1+tc.percent),2) else 0 end,
       'valid'
  from chricar_account_move_line_deloitte d,
       account_journal aj,
       account_move am,
       account_account ac,
       account_account_type at,
       chricar_account_tax_code_deloitte tc
 where aj.name = 'Deloitte'
   and am.journal_id = aj.id
   and am.name = d.symbol||'-'||d.name
   and am.date = to_date(d.date,'DD.MM.YY')
   and ac.code = case when d.account = substr(d.account,1,4) then d.account
                      when length(d.account) > 4 then substr(d.account,1,2)||'00'
                 end
   and tc.code = d.tax_code
   and at.id = ac.user_type
   and at.close_method = 'none'
union all
-- tax code account - tax - avoid rounding differnces !!!
select tc.account_id,am.date,am.journal_id,am.id,d.description,am.period_id, get_analytic_id(d.analytic_account),
       case when d.amount > 0 then  d.amount - round( d.amount / (1+tc.percent),2) else 0 end,
       case when d.amount < 0 then -d.amount - round(-d.amount / (1+tc.percent),2) else 0 end,
       'valid'
  from chricar_account_move_line_deloitte d,
       account_journal aj,
       account_move am,
       account_account ac,
       account_account_type at,
       chricar_account_tax_code_deloitte tc
 where aj.name = 'Deloitte'
   and am.journal_id = aj.id
   and am.name = d.symbol||'-'||d.name
   and am.date = to_date(d.date,'DD.MM.YY')
   and ac.code = case when d.account = substr(d.account,1,4) then d.account
                      when length(d.account) > 4 then substr(d.account,1,2)||'00'
                 end
   and tc.code = d.tax_code
   and at.id = ac.user_type
   and at.close_method = 'none'
   and percent > 0

union all
-- counter account
-- no tax code account
select ac.id,am.date,am.journal_id,am.id,d.description,am.period_id, get_analytic_id(d.analytic_account),
       case when d.amount < 0 then -d.amount else 0 end,
       case when d.amount > 0 then  d.amount else 0 end,
       'valid'
  from chricar_account_move_line_deloitte d,
       account_journal aj,
       account_move am,
       account_account ac,
       account_account_type at
 where aj.name = 'Deloitte'
   and am.journal_id = aj.id
   and am.name = d.symbol||'-'||d.name
   and am.date = to_date(d.date,'DD.MM.YY')
   and ac.code = case when d.counter_account = substr(d.counter_account,1,4) then d.counter_account
                      when length(d.counter_account) > 4 then substr(d.counter_account,1,2)||'00'
                 end
   and at.id = ac.user_type
   and (at.close_method != 'none' or tax_code is null)
union all
-- tax code account - net
select ac.id,am.date,am.journal_id,am.id,d.description,am.period_id, get_analytic_id(d.analytic_account),
       case when d.amount < 0 then round(-d.amount / (1+tc.percent),2) else 0 end,
       case when d.amount > 0 then round( d.amount / (1+tc.percent),2) else 0 end,
       'valid'
  from chricar_account_move_line_deloitte d,
       account_journal aj,
       account_move am,
       account_account ac,
       account_account_type at,
       chricar_account_tax_code_deloitte tc
 where aj.name = 'Deloitte'
   and am.journal_id = aj.id
   and am.name = d.symbol||'-'||d.name
   and am.date = to_date(d.date,'DD.MM.YY')
   and ac.code = case when d.counter_account = substr(d.counter_account,1,4) then d.counter_account
                      when length(d.counter_account) > 4 then substr(d.counter_account,1,2)||'00'
                 end
   and tc.code = d.tax_code
   and at.id = ac.user_type
   and at.close_method = 'none'
union all
-- tax code account - tax - avoid rounding differnces !!!
select tc.account_id,am.date,am.journal_id,am.id,d.description,am.period_id, get_analytic_id(d.analytic_account),
       case when d.amount < 0 then -d.amount - round(-d.amount / (1+tc.percent),2) else 0 end,
       case when d.amount > 0 then  d.amount - round( d.amount / (1+tc.percent),2) else 0 end,
       'valid'
  from chricar_account_move_line_deloitte d,
       account_journal aj,
       account_move am,
       account_account ac,
       account_account_type at,
       chricar_account_tax_code_deloitte tc
 where aj.name = 'Deloitte'
   and am.journal_id = aj.id
   and am.name = d.symbol||'-'||d.name
   and am.date = to_date(d.date,'DD.MM.YY')
   and ac.code = case when d.counter_account = substr(d.counter_account,1,4) then d.counter_account
                      when length(d.counter_account) > 4 then substr(d.counter_account,1,2)||'00'
                 end
   and tc.code = d.tax_code
   and at.id = ac.user_type
   and at.close_method = 'none'
   and percent > 0
;

/*
Update move to trigger calc of sum
*/

update account_move
   set state = 'posted'
 where state != 'posted'
   and (date,journal_id,name,period_id,state)
    in (select distinct to_date(d.date,'DD.MM.YY'),aj.id,symbol||'-'||d.name, ap.id,'draft'
  from chricar_account_move_line_deloitte d,
       account_journal aj,
       account_period ap
 where aj.name = 'Deloitte'
   and to_date(date,'DD.MM.YY') between ap.date_start and ap.date_stop
   and symbol not in (select code
                        from chricar_account_move_import_deny
                       where to_date(date,'DD.MM.YY') between case when date_start is null then to_date(date,'DD.MM.YY') else date_start end
                                                          and case when date_stop  is null then to_date(date,'DD.MM.YY') else date_stop end));



delete from account_analytic_line
 where journal_id in (select id from account_analytic_journal where name ='Deloitte')
   and date >=  ( select min(to_date(d.date,'DD.MM.YY'))
                    from chricar_account_move_line_deloitte d)
   and date <=  ( select max(to_date(d.date,'DD.MM.YY'))
                    from chricar_account_move_line_deloitte d);


/*
create analytic lines
*/
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
       account_analytic_journal aj,
       account_analytic_journal aaj,
       account_move am,
       account_account ac,
       account_account_type at
 where aj.name = 'Deloitte'
   and aaj.name = 'Deloitte'
   and am.journal_id = aj.id
   and am.name = d.symbol||'-'||d.name
   and am.date = to_date(d.date,'DD.MM.YY')
   and ac.code = case when d.account = substr(d.account,1,4) then d.account
                      when length(d.account) > 4 then substr(d.account,1,2)||'00'
                 end
   and at.id = ac.user_type
   and (at.close_method != 'none' or tax_code is null)
   and d.analytic_account is not null
union all
-- tax code account - net
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
       account_account ac,
       account_account_type at,
       chricar_account_tax_code_deloitte tc
 where aj.name = 'Deloitte'
   and aaj.name = 'Deloitte'
   and am.journal_id = aj.id
   and am.name = d.symbol||'-'||d.name
   and am.date = to_date(d.date,'DD.MM.YY')
   and ac.code = case when d.account = substr(d.account,1,4) then d.account
                      when length(d.account) > 4 then substr(d.account,1,2)||'00'
                 end
   and tc.code = d.tax_code
   and at.id = ac.user_type
   and at.close_method = 'none'
   and d.analytic_account is not null
union all
-- counter account
select get_analytic_id(d.analytic_account),
d.amount,
am.date,
ac.id,
aaj.id,
--am.id,
d.description
  from chricar_account_move_line_deloitte d,
       account_analytic_journal aj,
       account_analytic_journal aaj,
       account_move am,
       account_account ac,
       account_account_type at
 where aj.name = 'Deloitte'
   and aaj.name = 'Deloitte'
   and am.journal_id = aj.id
   and am.name = d.symbol||'-'||d.name
   and am.date = to_date(d.date,'DD.MM.YY')
   and ac.code = case when d.counter_account = substr(d.counter_account,1,4) then d.counter_account
                      when length(d.counter_account) > 4 then substr(d.counter_account,1,2)||'00'
                 end
   and at.id = ac.user_type
   and (at.close_method != 'none' or tax_code is null)
   and d.analytic_account is not null
union all
-- tax code account - net
select get_analytic_id(d.analytic_account),
d.amount,
am.date,
ac.id,
aaj.id,
--am.id,
d.description
  from chricar_account_move_line_deloitte d,
       account_journal aj,
       account_analytic_journal aaj,
       account_move am,
       account_account ac,
       account_account_type at,
       chricar_account_tax_code_deloitte tc
 where aj.name = 'Deloitte'
   and aaj.name = 'Deloitte'
   and am.journal_id = aj.id
   and am.name = d.symbol||'-'||d.name
   and am.date = to_date(d.date,'DD.MM.YY')
   and ac.code = case when d.counter_account = substr(d.counter_account,1,4) then d.counter_account
                      when length(d.counter_account) > 4 then substr(d.counter_account,1,2)||'00'
                 end
   and tc.code = d.tax_code
   and at.id = ac.user_type
   and at.close_method = 'none'
   and d.analytic_account is not null
;






/*
Neutralize moves generated by OpenERP itself and are replaced by Deloitte moves
*/

delete from account_move where journal_id in (select id from account_journal where name = 'Deloitte neutral');


insert into account_move(date,journal_id,name,period_id,state)
select to_date(substr(to_char(date_stop,'YYYYMMDD'),1,6)||'01','YYYYMMDD'),aj.id,ap.name||' neutral',ap.id,'draft'
 from account_move am,
      account_journal aj,
      account_journal ajd,
      account_period ap
where am.journal_id in (select id from account_journal where name = 'Deloitte')
  and aj.name = 'Deloitte neutral'
  and date between ap.date_start and ap.date_stop
group by to_date(substr(to_char(date_stop,'YYYYMMDD'),1,6)||'01','YYYYMMDD'),aj.id,ap.id,ap.name||' neutral'
order by  to_date(substr(to_char(date_stop,'YYYYMMDD'),1,6)||'01','YYYYMMDD')
;


insert into account_move_line(account_id,date,journal_id,move_id,name,period_id,analytic_account_id, credit,debit,state)
select account_id,amn.date,amn.journal_id,amn.id,'neutral',amn.period_id, analytic_account_id,
   case when sum(case when debit is null then 0 else debit end) > 0 then  sum(case when debit is null then 0 else debit end) else 0 end as cred,
   case when sum(case when debit is null then 0 else debit end) < 0 then -sum(case when debit is null then 0 else debit end) else 0 end as deb,
  'valid'
  from account_move_line aml,
       account_move am,
       account_journal aj,
       account_move amn,  -- neutral move
       account_journal ajn
 where aj.id = am.journal_id
   and aj.name not in ( 'Deloitte')
   and aj.is_opening_balance = False
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
   and aj.is_opening_balance = False
   and aml.move_id = am.id
   and am.period_id = amn.period_id
   and ajn.name = 'Deloitte neutral'
   and ajn.id = amn.journal_id
   and aml.state='valid'
   --and am.state='posted'
 group by account_id,amn.date,amn.journal_id,amn.id,amn.period_id,analytic_account_id
having sum(case when credit is null then 0 else credit end) != 0
;


update account_move
   set state = 'posted'
 where state != 'posted'
   and journal_id in (select id from account_journal where name = 'Deloitte neutral')
;

insert into account_move_line(account_id,date,journal_id,move_id,name,period_id,analytic_account_id, credit,debit,state)
select account_id,amn.date,amn.journal_id,amn.id,'neutral',amn.period_id, analytic_account_id,
   case when sum(case when debit is null then 0 else debit end) > 0 then  sum(case when debit is null then 0 else debit end) else 0 end as cred,
   case when sum(case when debit is null then 0 else debit end) < 0 then -sum(case when debit is null then 0 else debit end) else 0 end as deb,
  'valid'
  from account_move_line aml,
       account_move am,
       account_journal aj,
       account_move amn,  -- neutral move
       account_journal ajn
 where aj.id = am.journal_id
   and aj.name not in ( 'Deloitte')
   and aj.is_opening_balance = False
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
   and aj.is_opening_balance = False
   and aml.move_id = am.id
   and am.period_id = amn.period_id
   and ajn.name = 'Deloitte neutral'
   and ajn.id = amn.journal_id
   and aml.state='valid'
   --and am.state='posted'
 group by account_id,amn.date,amn.journal_id,amn.id,amn.period_id,analytic_account_id
having sum(case when credit is null then 0 else credit end) != 0
;


update account_move
   set state = 'posted'
 where state != 'posted'
   and journal_id in (select id from account_journal where name = 'Deloitte neutral')
;



/* check debit=credit

select ap.name,sum(debit) as Debit,sum(credit) as Credit ,sum(debit-credit) as Balance
  from account_move_line aml,
       account_period ap
 where ap.id=aml.period_id
 group by ap.name
order by ap.name
;

select move_id,sum(debit) as Debit,sum(credit) as Credit ,sum(debit-credit) as Balance
  from account_move_line aml
 group by move_id
having sum(debit-credit)  != 0
;

select id,name from account_move where id in
(select move_id
  from account_move_line aml
 group by move_id
having sum(debit-credit)  != 0)
;
*/

   RETURN ;
   END;
$$ LANGUAGE plpgsql;

/* put this in a wizard - long running - needs progress bar*/
--select import_doloitte_moves_function('2009');
