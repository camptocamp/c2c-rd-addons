

-- postgres tablefunc.sql must be loaded
-- debian:  \i /usr/share/postgresql/8.4/contrib/tablefunc.sql
/*
create or replace function c2c_budget_sequence_company(company_id_i int )
   RETURNS void AS $$
   DECLARE
      level_p integer;
      id_p integer;
      parent_id_p integer;
      start_pos_p varchar;
      r record;
      o record;
   BEGIN
      update c2c_budget_item set sequence = 0;
      select into start_pos_p id::varchar from c2c_budget_item where company_id = company_id_i and parent_id is null;

-- postgres tablefunc.sql must be loaded

          create table c2c_budget_item_sequence as
          SELECT * FROM connectby('c2c_budget_item','id','parent_id',        'code', start_pos_p , 0, '~')
                AS t(keyid integer, parent_keyid integer, level int, branch text, pos int);

          update c2c_budget_item i
             set sequence = ( select pos from c2c_budget_item_sequence where keyid = i.id);

          drop table c2c_budget_item_sequence;

   RETURN ;
   END;
$$ LANGUAGE plpgsql;

-- to start
select  c2c_budget_sequence_company(company_id);
*/

create extension if not exists tablefunc;
 
create or replace function c2c_budget_sequence()
   RETURNS void AS $$
   DECLARE
      level_p integer;
      id_p integer;
      parent_id_p integer;
      start_pos_p varchar;
      r record;
      o record;
   BEGIN
      update c2c_budget_item set sequence = 0;
      select into start_pos_p id::varchar from c2c_budget_item where parent_id is null;

-- postgres tablefunc.sql must be loaded

          create table c2c_budget_item_sequence as
          SELECT * FROM connectby('c2c_budget_item','id','parent_id',        'code', start_pos_p , 0, '~')
                AS t(keyid integer, parent_keyid integer, level int, branch text, pos int);

          update c2c_budget_item i
             set sequence = ( select pos from c2c_budget_item_sequence where keyid = i.id);

          drop table c2c_budget_item_sequence;

   RETURN ;
   END;
$$ LANGUAGE plpgsql;

-- to start
select  c2c_budget_sequence();
