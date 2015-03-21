# -*- coding: utf-8 -*-
{ 'sequence': 500,
"name"        : "ChriCar unique View ID"
, "version"     : "0.2"
, "author"      : "Network Gulf IT - India"
, "website"     : "http://www.chricar.at/ChriCar/index.html"
, "description" : """
This module is funded by

| ChriCar Beteiligungs- und Beratungs- GmbH
| http://www.chricar.at/ChriCar/index.html

Developed by

| Network Gulf IT - India
| http://www.networkgulf.com/

usage: get_id('your_view_name',param1,param2,param3,param4)

This function will always return the SAME unique id for a 
certain combination of parameters for a view.

Hint 1: you do not need this function if the unique id can easily be 
calculated during the grouping. Example:

- easy: group by product_id
- more complex: group by account_id, period_id
- very complex: group by account_id, period_id, currency_id

Hint 2: for large tables (100000 rec) performance gain of factor 10x and more
split the grouping operation and the get_id into 2 views

slow:

| select get_id(tablename,param1,param2,...), param1, param2, ... sum(field1), ...
| from
| group by get_id(tablename,param1,param2,...) ,param1,param2,...

fast:

1) view1:

| select ....
| from
| group by param1,param2,...

2) view2:

| select get_id('view1',param1,param2,...),* from view1;
| (no group by here)
"""
, "depends"      : ["base"]
, "init_xml"     : []
, "demo"         : []
, "data"   : []
, "auto_install" : False
, 'installable': False
, 'application'  : False
}
