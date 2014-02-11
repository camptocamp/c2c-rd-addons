# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2008-08-13
#
###############################################
from openerp.osv import fields, osv
import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime

# name should hold a unique period name like YYYYMM
# and special names like YYYY00 for balance carried forward
# this should make selection of periods unique, which is not the case in 4.2.2

class account_fiscalyear(osv.osv):
    _inherit = "account.fiscalyear"
    def create_period(self,cr, uid, ids, context={}, interval=1):
        for fy in self.browse(cr, uid, ids, context):
            dt = fy.date_start
            ds = mx.DateTime.strptime(fy.date_start, '%Y-%m-%d')
            while ds.strftime('%Y-%m-%d')<fy.date_stop:
                de = ds + RelativeDateTime(months=interval, days=-1)
                self.pool.get('account.period').create(cr, uid, {
                                        'name': ds.strftime('%Y%m'),
                                        'code': ds.strftime('%Y%m'),
                                        'date_start': ds.strftime('%Y-%m-%d'),
                                        'date_stop': de.strftime('%Y-%m-%d'),
                                        'fiscalyear_id': fy.id,
                                })
                ds = ds + RelativeDateTime(months=interval)
        return True

#    def init(self, cr):
#       cr.execute("""
#       update account_period
#          set name = to_char(date_start,'YYYYMM'),
#              code = to_char(date_start,'YYYYMM')
#        where name not like  to_char(date_start,'YYYYMM')||'%'
#           or code not like to_char(date_start,'YYYYMM')||'%';
#       """)


account_fiscalyear()
