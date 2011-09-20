

/*
DO NOT FORGET
edit csv file - remove 1 line and 3 line 
*/


delete from chricar_account_move_line_deloitte;


insert into ism_konto("MAND","TYP","KONTO")
select j."MAND", j."TYP",  j."KONTO" from ism_journal j
except select k."MAND", k."TYP",  k."KONTO" from ism_konto k;


insert into chricar_account_move_line_deloitte(account,description,analytic_account,amount,date,symbol,name) 
select k.code,"TEXT","STELLE",
case when j."SH" = 'S' then "BETRAG" else -"BETRAG" end as BETRAG,
"DATUM_BU","BUCH","BELEG" from ism_journal j, ism_konto k
where k."TYP" = j."TYP"
  and k."KONTO" = j."KONTO"
  and k.code is not null
union all
select
case when j."TYP" = 'D' then '200' else '331' end,
"TEXT","STELLE",
case when j."SH" = 'S' then "BETRAG" else -"BETRAG" end as BETRAG,
"DATUM_BU","BUCH","BELEG"
from ism_journal j
where j."TYP" in ('D','K')
;




