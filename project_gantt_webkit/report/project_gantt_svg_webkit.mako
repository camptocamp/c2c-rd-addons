<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <style type="text/css">
        body {font-family:Helvetica,sans-serif;font-size:8pt;}
        ${css}
    </style>
  </head>

  <body>
<%
import datetime
from tools.translate import _

def datum(date, now) :
    if date :
        return datetime.datetime.strptime(date, date_fmt).date()
    else :
        return now
# end def datum    

def category(task, now) :
    c_now = datetime.datetime.strftime(now, date_fmt)
    if not task.date_start or not task.date_end : return "gold" # "#DD0"
    elif task.date_start > c_now : return "blue" #"#00C"
    elif task.date_end > c_now : return "firebrick" #"#C00"
    else : return "lightgreen" # "#0C0"
# end def category

def title(name) :
    if len(name) > 13 :
        return name[:13] + "..."
    else :
        return name
# en def title

def duration(task, now) :
    return (datum(task.date_end, now) -  datum(task.date_start, now)).days
# end def duration

def scale(timespan) :
    if timespan < 90 :
        return 15, 15, 1, 7
    elif timespan < 400 :
        return 5, 15, 7, 21
    else :
        return 1, 15, 30, 100    
# end def scale

date_fmt = "%Y-%m-%d %H:%M:%S"
months = [_("Jan"), _("Feb"), _("Mar"), _("Apr"), _("May"), _("Jun"), _("Jul"), _("Aug"), _("Sep"), _("Oct"), _("Nov"), _("Dec")]
workingday = ["white", "white", "white", "white", "white", "silver", "silver"]
color = ["white", "white", "silver"]
now = datetime.datetime.now().date()
first = min(datum(task.date_start, now) for task in objects if task.date_start)
last  = max(datum(task.date_end,   now) for task in objects if task.date_end)
timespan = (last-first).days
dx, dy, d, space = scale(timespan) 
%>
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${(timespan + space)*dx} ${len(objects)+3)*dy}">

%if timespan < 90 :
    <% month = 0 %>
    %for actual in [first + datetime.timedelta(days=i) for i in range(0, timespan, d)] :
        <% x0 = ((actual-first).days)*dx + space*dx %>
        %if actual.month != month :
            <text x="${x0}" y="${dy}">${months[actual.month-1]}'${actual.year % 100}</text>
            <% month = actual.month %>
        <rect x="${x0}" y="${dy}" width="${dx}" height="${(len(objects)+1)*dy}" fill="${workingday[actual.isoweekday()-1]}" style="opacity:0.2"/>
        <text x="${x0}" y="${int(dy+(dy*0.8))}">${actual.day}</text>
%elif timespan < 400 :
    <% month = 0 %>
    %for actual in [first + datetime.timedelta(days=i) for i in range(0, timespan, d)] :
        <% x0 = ((actual-first).days)*dx + space*dx %>
        %if actual.month != month :
            <text x="${x0}" y="${dy}">${months[actual.month-1]}'${actual.year % 100}</text>"""
            <% month = actual.month %>
        <rect x="${x0}" y="${dy}" width="${d*dx}" height="${(len(objects)+1)*dy}" fill="${color[actual.isocalendar()[1] % 3]}" style="opacity:0.2"/>
        <text x="${x0}" y="${int(dy+(dy*0.8))}">${_('cw')}${actual.isocalendar()[1]+1}</text>
%else :
    <% first = datetime.date(first.year, first.month, 1) 
    year = 0 %>
    %for actual in [datetime.date(first.year + (first.month + i-1)/12, ((first.month + i - 1) % 12)+1, 1) for i in range(0, timespan/d)] :
        <% x0 = ((actual-first).days)*dx + space*dx %>
        %if actual.year != year :
            <text x="${x0}" y="${dy}">${actual.year}</text>
            <% year = actual.year %>
        <rect x="${x0}" y="${dy}" width="${d*dx}" height="${(len(objects)+1)*dy}" fill="${color[actual.month % 3]}" style="opacity:0.2"/>
        <text x="${x0}" y="${int(dy+(dy*0.8))}">${months[actual.month-1]}</text>"""
%for i in range(0, len(objects), 3) :
    <rect x="0" y="${(i+2)*dy+4}" width="${((last-first).days + space)*dx}" height="${dy}" fill="whitesmoke" style="opacity:0.4"/>

%for i, task in enumerate(sorted(objects, key=lambda o: (datum(o.date_start, now), o.name))) :
    <text x="0" y="${(i+3)*dy}">${title(task.name)}</text>
    <rect x="${((datum(task.date_start, now) - first).days + space)*dx}" y="${(i+3)*dy-dy/2}" width="${max(dx, duration(task, now)*dx)}" height="${int(dy*0.5)}" fill="${category(task, now)}"/>
<rect x="${((now - first).days + space)*dx}" y="${dy}" width="${max(1,int(dx*0.5))}" height="${(len(objects)+1)*dy}" fill="blue" style="opacity:0.2"/>

  </svg>
  </body>
</html>

