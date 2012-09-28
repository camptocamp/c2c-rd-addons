 select name,src,value from ir_translation
 where name like '%product.template,name';

 select name,src,value from ir_translation
 where name like '%product.template,name'
 and res_id not in (select id from product_template);

/*

ADAPT, if multipla langugages are available
*/
 
 update product_template p
    set name = (select value
                  from ir_translation
                 where name like '%product.template,name%'
                   and res_id = p.id)
   where id in (select res_id from ir_translation
                 where name like '%product.template,name')
;

 update ir_translation
    set src = value
    where name like '%product.template,name'
;


  

                 