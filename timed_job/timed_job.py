# -*- coding: utf-8 -*-
##############################################
#
# Copyright (C) 2011 Swing Entwicklung betrieblicher Informationssysteme GmbH (<http://www.swing-system.com>)
# Copyright (C) 2011 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
# all rights reserved
#    20-JUN-2011 (GK) created
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/> or
# write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################
import calendar
import datetime
import logging
import threading
import time
#import pooler
from openerp.osv import fields, osv
import openerp.tools
import sys
import traceback
from openerp.tools.translate import _
#from openerp.tools.save_eval import save_eval as eval

class timed_job(osv.osv):
    """Executes job at a specific point in time and repeats this at an exact time-interval."""
    _name           = "timed.job"
    _description    = "Timed Job"
    _order          = 'lastcall'
    _running        = set()
    _logger         = logging.getLogger(_name)
    _time_granule   = datetime.timedelta(seconds=10)
    _max_scheduler_delta = datetime.timedelta(hours=6) # if no active job, it will run again after this time
    _basic_select   = "SELECT * FROM timed_job WHERE numbercall<>0 AND active"
    _interval_types = \
        [ ('minutes', 'Minutes')
        , ('hours', 'Hours')
        , ('days', 'Days')
        , ('days_of_week','Days of Week')
        , ('days_of_month', 'Days of Month')
        ]
    _list_mask = \
        { 'minutes' : [('invisible', True)]
        , 'hours'   : [('invisible', True)]
        , 'days'    : [('invisible', True)]
        }
    _loop_mask = \
        { 'days_of_week'  : [('invisible', True)]
        , 'days_of_month' : [('invisible', True)]
        }

    def _nextcall (self, cr, uid, ids, field_name, arg, context) :
        res = {}
        for obj in self.browse (cr, uid, ids, context) :
            if obj.lastcall :
                last = datetime.datetime.strptime(obj.lastcall[0:19], '%Y-%m-%d %H:%M:%S')
            else :
                last = datetime.datetime.now()
            job = \
                { "state"           : obj.state
                , "interval_number" : obj.interval_number
                , "day_time"        : obj.day_time
                , "day_list"        : obj.day_list
                }
            res [obj.id] =  self._next(last + self._time_granule, job).strftime('%Y-%m-%d %H:%M:%S')
        return res
    # end def _nextcall

    _columns = \
        { 'active'              : fields.boolean('Active')
        , 'args'                : fields.text
            ('Arguments'
            , required = True
            , help     = "Arguments to be passed to the method."
            )
        , 'day_list'            : fields.char
            ('Day list'
            , size   = 64
            , states = _list_mask
            , help   = "comma separated list of day-numbers (depending on 'Interval unit')."
            )
        , 'day_time'            : fields.char
            ('Start Time'
            , required = True
            , size = 8
            , help = "Referential point in time where the Interval Unit starts.Format: '23:59:59'"
            )
        , 'function'            : fields.char
            ('Function'
            , size     = 64
            , required = True
            , help     = "Name of the method to be called on the object when this scheduler is executed."
            )
        , 'interval_number'     : fields.integer
            ('Interval Number'
            , states = _loop_mask
            , help   = "Repeat every 'Interval Unit'."
            )
        , 'lastcall'            : fields.datetime
            ('Last Execution Time'
            , readonly = True
            , help     = "When did this job finish (successfully) the last time?"
            )
        , 'model'               : fields.many2one
            ( 'ir.model'
            , 'Object'
            , required = True
            , ondelete = 'cascade'
            , help = "Object whose function will be called when this scheduler will run. e.g. 'res.partner'"
            )
        , 'name'                : fields.char('Name', size = 64, required = True)
        , 'nextcall'            : fields.function
           ( _nextcall
           , type   = 'datetime'
           , method = True
           , string = 'Next Execution Time'
           , store  = False
           )
        , 'numbercall'          : fields.integer
            ( 'Number of Calls'
            , help = "Number of time the function is called,\na negative number indicates no limit"
            )
        , 'repeat_missed'       : fields.boolean
            ( 'Repeat Missed'
            , help = "Enable this if you want to execute missed occurences as soon as the server restarts"
            )
        , 'notification_mail'   : fields.boolean
            ( 'Notification by Mail'
            , help = """Normally, if an error occurs, information is written to the server-log. If checked, an email is generated (using Mail-Template 'Notification Timed Job'). Note, that in this case the Job is marked as successful"""
            )
        , 'startup_predecessor' : fields.many2one
            ( 'timed.job'
            , 'Startup Predecessor'
            , help = "Job that has to be executed before this job can run (during startup)"
            )
        , 'state'               : fields.selection
            (_interval_types
            , 'Interval Unit'
            , required = True
            , help     = """
Depending on this interval unit the length of the interval can be specified:
 - "Minutes": every 'Interval Number' minutes beginning at 'Last Execution Time'
 - "Hours": every 'Interval Number' hours beginning at 'Last Execution Time'
 - "Days": every 'Interval Number' days beginning at 'Last Execution Time'
 - "Days of Week" : at the 'Day list' of days in the range 0..6. E.g. "1,2,7" means at monday, tuesday, sunday.
 - "Days of Month" : at the 'Day list' of days in the range -31..31. E.g. "1,15,-1" means at the first, the 15th and the last day of month.
"""
            )
        , 'user_id'             : fields.many2one('res.users', 'User', required = True)
        }

    _defaults = \
        { 'active'            : lambda *a : True
        , 'args'              : lambda *a : '()'
        , 'day_list'          : lambda *a : '1'
        , 'day_time'          : lambda *a : '00:00:00'
        , 'interval_number'   : lambda *a : 1
        , 'state'             : lambda *a : 'days'
        , 'numbercall'        : lambda *a : -1
        , 'repeat_missed'     : lambda *a : False
        , 'notification_mail' : lambda *a : False
        , 'user_id'           : lambda self, cr, uid, context : uid
        }

    def str2tuple(self, s):
        return eval('tuple(%s)' % (s or ''))

    def _check_args(self, cr, uid, ids, context=None):
        try :
            for obj in self.browse(cr, uid, ids, context):
                self.str2tuple(obj.args)
        except Exception:
            return False
        return True
    # end def _check_args

    def _check_list(self, cr, uid, ids, context=None):
        try :
            for obj in self.browse(cr, uid, ids, context):
                if obj.state == "days_of_week" :
                    days = obj.day_list.replace(" ", "").split(",")
                    for day in days :
                        if int(day) not in range(1,8) : 
                            return False
                elif obj.state == "days_of_month" :
                    days = obj.day_list.replace(" ", "").split(",")
                    for day in days :
                        if int(day) not in range(-31,32) : 
                            return False
        except Exception:
            return False
        return True
    # end def _check_list

    def _check_function(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context) :
            job_obj = self.pool.get(obj.model.model)
            functions = [f for f in dir(job_obj) if callable(getattr(job_obj, f))] # xxx can be improved
            if obj.function not in functions : 
                return False
        return True
    # end def _check_function

    def _check_predecessor(self, cr, uid, ids, context=None) :
        
        def contains(pre, obj) :
            if not pre : 
                return False
            if pre == obj :
                return True
            else :
                return contains(pre.startup_predecessor, obj)
        # end def contains

        for obj in self.browse(cr, uid, ids, context) :
            if contains(obj.startup_predecessor, obj) : return False
        return True
    # end def _check_predecessor

    _constraints = \
        [ ( _check_args
          , _('Invalid Arguments')
          , ['args']
          )
        , ( _check_list
          , _('Invalid Day list.\nA comma separated list of integers (in a valid range, depending on the Interval Unit) is expected')
          ,  ['day_list']
          )
        , ( _check_function
          , _('Invalid Function.\nA Function provided by this Object is expected')
          ,  ['function']
          )
        , ( _check_predecessor
          , _('Invalid Startup Predecessor.\nPossibly a circular dependency')
          ,  ['startup_predecessor']
          )
        ]

    def __init__(self, pool, cr) :
        self._logger.debug("Initialization") ##############
        res = super(timed_job, self).__init__(pool, cr)
        self._running = set()
        cr.execute("SELECT state FROM ir_module_module WHERE name='timed_job';")
        res = cr.dictfetchall()[0]
        if res['state'] != "to install" : # do not execute selects before installation
            self._thread(self._startup, cr.dbname)
        return res
    # end def __init__

    def _startup(self, dbname) :
#        self._logger.debug("_startup")
        
        def insert(job_dict, job) :
            if job['startup_predecessor'] and job['startup_predecessor'] in job_dict.keys() :
                pre = job_dict[job['startup_predecessor']]
                insert(job_dict, pre)
            self.job_startup_sequence.append(job)
            del job_dict[job['id']]            
        # end def insert

        now = datetime.datetime.now()
        try :
            db  = pooler.get_db(dbname)
        except Exception:
            self._logger.error("Get DB-pool for %s failed", dbname)
            raise
        cr        = db.cursor()
        try :
            cr.execute(self._basic_select + " AND (repeat_missed OR startup_predecessor IS NOT NULL)")
            jobs = cr.dictfetchall()
    
            job_dict = {}
            for job in jobs :
                job_dict[job['id']] = job
    
            self.job_startup_sequence = []
            for id in job_dict.keys() :
                if id in job_dict.keys() : # because the job_dict vanishes 
                    insert(job_dict, job_dict[id])
    
            for job in self.job_startup_sequence :
                if job['lastcall'] :
                    last = datetime.datetime.strptime(job['lastcall'][0:19], '%Y-%m-%d %H:%M:%S')
                else :
                    last = None
                self._process_job(cr.dbname, now, job, last)
    
            self._scheduler(cr.dbname)
        except Exception:
            cr.rollback()
            self._logger.error("Get DB-pool for %s failed during startup", dbname)
            raise
        finally:
            cr.close()
    # end def _startup

    def _start_timer(self, sec, fn, *args, **kwargs) :
        wait = max(0.0, sec)
        t = threading.Timer(wait+0.7, fn, args, kwargs)
        t.setDaemon(True)
        t.start()
    # end def _start_timer

    def _thread(self, fn, *args, **kwargs) :
        self._logger.debug("Thread started %s, %s, %s", fn, args, kwargs) ###################
        t = threading.Timer(0.0, fn, args, kwargs)
        t.setDaemon(True)
        t.start()
    # end def _thread

    def _update_db(self, cr, id, numbercall, now) :
        if numbercall != -1 :
            updn = ", numbercall=%s" % numbercall
        else :
            updn = ""
        sql = "UPDATE timed_job SET lastcall='%s'%s WHERE id=%s;" % (now, updn, id)
        cr.execute(sql)
        cr.commit()
    # end def _update_db
    
    def _days_of_month(self, date) :
        month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        return month_days[date.month - 1] + int (calendar.isleap(date.year) and date.month == 2)
    # end def _days_of_month
    
    def _next(self, last, job) :
      # FGF FIXME error during install - last = NULL
      if last:
        _interval_times = \
            { 'minutes'       : lambda interval : datetime.timedelta(minutes=interval)
            , 'hours'         : lambda interval : datetime.timedelta(hours=interval)
            , 'days'          : lambda interval : datetime.timedelta(days=interval)
            , 'days_of_week'  : lambda interval : datetime.timedelta(days=1)
            , 'days_of_month' : lambda interval : datetime.timedelta(days=1)
            }
        dt    = [int(d) for d in job['day_time'].split(":")]
        ref   = last.replace(hour=dt[0], minute=dt[1], second=dt[2], microsecond=0)
        days  = [int(i) for i in job['day_list'].replace(" ", "").split(",")]
        delta = _interval_times[job['state']](job['interval_number'])
        if   job['state'] in ["minutes", "hours"] :
            next = ref
            if ref > last :
                while next >  last : next -= delta
                return next + delta
            while next <=  last : next += delta
            return next
        elif job['state'] == "days" :
            if ref > last :
                return ref
            return ref + delta
        elif job['state'] == "days_of_week" :
            if last.isoweekday() in days :
                if ref > last :
                    return ref
            next = ref + delta
            while next.isoweekday() not in days :
                next += delta
            return next
        elif job['state'] == "days_of_month" :
            if last.day in [range(self._days_of_month(last)+1)[d] for d in days] :
                if ref > last :
                    return ref
            next = ref + delta
            while next.day not in [range(self._days_of_month(next)+1)[d] for d in days] :
                next += delta
            return next
        raise # illegal "state"
    # end def _next

    def _call(self, cr, uid, model_obj, func, args) :
        if not model_obj :
            self._logger.error("Model for %s%s not (yet) defined" % (func, args))
            return
        f = getattr(model_obj, func)
        t0 = time.time()
        c0 = time.clock()
        f(cr, uid, *args)
        c = time.clock() - c0
        t = time.time() - t0
        self._logger.debug \
            ("Job executed in %0.2f elapsed seconds and %0.2f CPU seconds for %s.%s%s from user-id %s"
            , t, c, model_obj._table, func, args, uid
            )
    # end def _call

    def _process_job(self, dbname, now, job, last) :
        if job['lastcall'] :
            next = self._next(last, job)
        else :
            next = now
        numbercall = job['numbercall']
        try :
            db  = pooler.get_db(dbname)
        except Exception:
            self._logger.error("Get DB-pool for %s failed", dbname)
            raise
        cr = db.cursor()
        try :
            model_obj = self.pool.get("ir.model")
            model     = model_obj.browse(cr, job['user_id'], job['model'])
            job_obj   = self.pool.get(model.model)

            ok = False
            if job['id'] in self._running : return
            self._running.add(job['id'])
            while next < (now + self._time_granule) and numbercall != 0:
                if numbercall > 0 :
                    numbercall -= 1
                if not ok or job['repeat_missed'] :
                    self._call(cr, job['user_id'], job_obj, job['function'], self.str2tuple(job['args']))
                    self._update_db(cr, job['id'], numbercall, now)
                    ok = True
                next = self._next(next, job)
        except Exception, exc :
            cr.rollback()
            if job['notification_mail'] :
                self._send_mail(cr, job['user_id'], job['id'])
                cr.commit()
            else :
                self._logger.error \
                    ( "Job processing of '%s' (ir.model(%s).%s %s) failed due to: %s\n%s"
                    , job['name'], job['model'], job['function'], job['args'], exc
                    , "\n".join(traceback.format_exception(*sys.exc_info()))
                    )
        finally:
            cr.close()
            if job['id'] in self._running : self._running.remove(job['id'])
    # end def _process_job

    def _scheduler(self, dbname) :
        if not datetime : return # during shutdown the time-feature may not exist anymore
        now = datetime.datetime.now()
        nextcall = now + self._max_scheduler_delta
        try :
            db  = pooler.get_db(dbname)
        except Exception:
            self._logger.error("Get DB-pool for %s failed", dbname)
            raise
        cr = db.cursor()
        try :
            cr.execute(self._basic_select)
            dbjobs = cr.dictfetchall()
            jobs = []
            for job in dbjobs :
                lastcall = now
                if job['lastcall'] :
                    lastcall = datetime.datetime.strptime(job['lastcall'][0:19], '%Y-%m-%d %H:%M:%S')
                execcall = thiscall = lastcall
                while execcall <= (now - self._time_granule) :
                    execcall = self._next(execcall, job)
                if (((now - self._time_granule) <= execcall <= (now + self._time_granule))) :
                    jobs.append((execcall, job))
                    execcall = self._next(execcall, job)
                nextcall = min(nextcall, execcall)
            delta = nextcall - datetime.datetime.now() # do not use variable "now"
            total_seconds = delta.seconds + delta.days * 24 * 3600 # use "delta.total_seconds()" in Py2.7
            self._start_timer(float(total_seconds), self._scheduler, dbname)
            for t, job in sorted(jobs, key=lambda x: x[0]) :
                if job['lastcall'] :
                    last = datetime.datetime.strptime(job['lastcall'][0:19], '%Y-%m-%d %H:%M:%S')
                else :
                    last = None
                self._thread(self._process_job, dbname, now, job, last)
        except Exception, ex :
            self._logger.error('Exception: %s', str(ex))
        finally :
            cr.close()
    # end def _scheduler

    def _send_mail(self, cr, uid, job_id) :
        job = self.browse(cr, uid, job_id)
        name = "Notification Timed Job"
        mail_obj = self.pool.get("email.template")
        tpl_ids = mail_obj.search(cr, uid, [("name", "=", name)])
        if tpl_ids :
            tpl = mail_obj.browse(cr, uid, tpl_ids[0])
#            msg_id = mail_obj.send_mail(cr, uid, tpl.id, job_id, force_send=False, context=context) # GKH don't know why this doesn't work
            values = mail_obj.generate_email(cr, uid, tpl.id, job_id)
            values["user_id"] = uid
            values["body_html"] = """<?xml version="1.0"?>\n<data>""" + ("</br>".join(traceback.format_exception(*sys.exc_info()))) + "</data>"
            values["mail_server_id"] = tpl.mail_server_id.id
#            values["partner_id"] = job.user_id.partner_id.id
            values["subtype"] = "html"
            del values["attachments"]
            del values["attachment_ids"]
            msg_obj = self.pool.get('mail.message')
            msg_obj.create(cr, uid, values)
        else  :
            self._logger.error("No Mail Template named '%s' defined", name)
    # end def _send_mail

    def create(self, cr, uid, vals, context=None) :
        res = super(timed_job, self).create(cr, uid, vals, context=context)
        cr.commit()
        self._scheduler(cr.dbname)
        return res
    # end def create

    def write(self, cr, uid, ids, vals, context=None) :
        res = super(timed_job, self).write(cr, uid, ids, vals, context=context)
        cr.commit()
        self._scheduler(cr.dbname)
        return res
    # end def write

    def unlink(self, cr, uid, ids, context=None) :
        res = super(timed_job, self).unlink(cr, uid, ids, context=context)
        return res
    # end def unlink

    def thread_watchdog(self, cr, uid, args=[]) :
        system_threads = \
            { '_MainThread'            : (True, False)
            , 'HttpDaemon'             : (True, False)
            , 'TinySocketServerThread' : (True, False)
#            , 'TinySocketClientThread' : (True, False)
            }
        threads = {}
        for t in threading.enumerate() :
            if t is not threading.currentThread() :
                threads[t.__class__.__name__] = t
        for n, t in system_threads.iteritems():
            if n not in threads : 
                self._logger.warning("Missing system-thread '%s'", n)
            else :
                if threads[n].isAlive() != t[0] or threads[n].isDaemon() != t[1] :
                    self._logger.warning("Strange property of system-thread '%s': %s", n, threads[n])
        for n, t  in threads.iteritems():
            if n not in system_threads:
                if not t.isAlive() or not t.isDaemon() :
                    self._logger.warning \
                        ("Strange property of thread '%s': %s daemon: %s alive: %s", n, t, t.isDaemon(), t.isAlive())
    # end def thread_watchdog

    def test(self, cr, uid, args=[]) :
        if len(args) < 2 :
            raise osv.except_osv \
                ( _('Test error !')
                , _('Function requires two arguments (e.g.: (2.0, "My two second duration test"))')
                )
        self._logger.debug("test: %s [%0.2f sec]", args[1], args[0])
        time.sleep(args[0])
    # end def test
# end class timed_job
timed_job()
