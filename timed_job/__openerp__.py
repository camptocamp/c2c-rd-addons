# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Swing Entwicklung betrieblicher Informationssysteme GmbH (<http://www.swing-system.com>)
#    Copyright (C) 2011 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{ 'sequence': 500,
'name'         : "Executes Jobs periodically at a specific point in time and repeats this at a time-interval"
, 'version'      : "1.1"
, 'category'     : "Tools"
, 'description'  : """Executes job at a specific point in time and repeats this at a time-interval.

Main features:
- Executes a function "Function" on object "Object" with arguments "Arguments"
- Starts the function at precise time "Start Time" (or on following periods, see below)
- Periodic execution according to specified, precise intervals (see below)
- Jobs may be executed in parallel, according to their start time
- Double-start protection (do not execute the same job more than once in parallel)
- The termination of the last successfull execution is stored ("Last Execution Time")
- Jobs are terminated when the server terminates
- Insertion, deletion of jobs take immediate effect
- Optionally, the missed executions can be repeated after a server outage ("Repeat Missed")
- Optionally, a fixed number of execution times can be specified ("Number of Calls")
- Optionally, a notification mail will be sent in case of errors
- Optionally, an execution dependency between jobs during server-startup can be specified ("Startup Predecessor")
This specifies the job that has to be executed in advance during a server-startup.


Interval Types:
- 'Minutes'       : Jobs are executed at "Interval Number" minutes relative to "Start Time"
- 'Hours'         : Jobs are executed at "Interval Number" hours relative to "Start Time"
- 'Days'          : Jobs are executed at "Interval Number" days at "Start Time"
- 'Days of Week'  : Jobs are executed at specified weekday (according to ISO-numbering: 1=monday, 2=tuesday, ..., 7=sunday) at "Start Time"
- 'Days of Month' : Jobs are executed at specified day of month at "Start Time" (1=first day, 2=second day, -1=ultimo). 


Notes:
Carefully planned time-triggered jobs can be very resource-efficient.

When using interval type 'Days', it is assumed that the start day is irrelevant. 
Note that - depending on the calendar and on the interval - this day will shift anyway over years.
The implementation calculates the interval relative to the "Last execution time".
Therefore, by deleting/reinserting of a job this day can be specified.

With "Startup Predecessor" complex dependency trees can be specified. 
Circular dependencies are (obviously) not allowed.

"Repeat Missed" and "Startup Predecessor" have a necessary - but not obvious - drawback:
During server startup, those jobs have to be executed prior to any other job - this may take a long time.
Use those features judiciously.

Depending on the log_level of the server, information (elapsed time / CPU time) about the executed jobs are written to the server log.

The specified 'Function' must be known to the 'Object'.

The object 'Timed Job' provides two convenience functions for testing and sanity:
- test(self, cr, uid, args=[]) : for testing 
- args[0] is a floating point number of seconds that this function will last
- args[1] is a String that will be written to the server log

- thread_watchdog(self, cr, uid, args=[]) : checks all threads and their states and writes anomalies to the server log


Programmatic interface :
- _time_granule: A datetime.timedelta (default 10sec) that specifies the sparse time base (a value of 0 will not work!)
- _max_scheduler_delta: A datetime.timedelta (default 6hours) that specifies the maximum interval for the scheduler to be executed
"""
, "author"       : "Swing Entwicklung betrieblicher Informationssysteme GmbH"
, "website"      : "http://www.swing-system.com"
, 'depends'      : ["email_template"]
, 'data'   : 
[ "security/ir.model.access.csv"
, "timed_job_view.xml"
]
, 'test'         : []
, "init_xml"     : ["email_template_data.xml"]
, 'demo_xml'     : ["timed_job_demo.xml"]
, 'installable': False
, 'application'  : False 
, 'auto_install' : False
}
