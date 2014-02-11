from openerp.osv import fields,osv

class chricar_view_id(osv.osv):
    _name = "chricar_view_id"
    _columns = {'name': fields.char('Name', size=32)}

    def init(self, cr):
        #install plpgsql languge in to the data database
        cr.execute("SELECT true FROM pg_catalog.pg_language WHERE lanname = 'plpgsql';")
        if not cr.fetchall():
            cr.execute("create language plpgsql;")

        #Create a table to record the unique ids for the view
        cr.execute("SELECT count(*) FROM pg_class WHERE relname = 'unique_view_id'")
        if cr.fetchone()[0] == 0:
#            cr.execute("""CREATE TABLE unique_view_id (id serial, view_name varchar(128) NOT NULL, id_1 integer, id_2 integer, id_3 integer);""")
            cr.execute("""CREATE TABLE unique_view_id (id serial, view_name varchar(128) NOT NULL,
                            id_1 integer NOT NULL default 0,
                            id_2 integer NOT NULL default 0,
                            id_3 integer NOT NULL default 0,
                            id_4 integer NOT NULL default 0);""")
            cr.execute("""create unique index unique_view_id_1 on unique_view_id(view_name,id_1,id_2,id_3,id_4);""")

        # create a funtion wich will return a unique ID
        cr.execute("""
CREATE OR REPLACE FUNCTION get_id(view varchar, id1 integer, id2 integer, id3 integer, id4 integer ) RETURNS integer AS $$
  DECLARE
    res_id integer;
  BEGIN
    SELECT id INTO res_id FROM unique_view_id
      WHERE 
        view_name=view
        AND id_1=coalesce(id1,0)
        AND id_2=coalesce(id2,0)
        AND id_3=coalesce(id3,0)
        AND id_4=coalesce(id4,0);
    IF not found THEN
      INSERT INTO unique_view_id( view_name, id_1, id_2, id_3, id_4)
              VALUES(view,
                  coalesce(id1,0),
                  coalesce(id2,0),
                  coalesce(id3,0),
                  coalesce(id4,0));
          SELECT id INTO res_id FROM unique_view_id
            WHERE 
              view_name=view
              AND id_1=coalesce(id1,0)
              AND id_2=coalesce(id2,0)
              AND id_3=coalesce(id3,0)
              AND id_4=coalesce(id4,0);
    END IF;
    RETURN coalesce(res_id);
  END;
$$ LANGUAGE plpgsql;""")

chricar_view_id()
