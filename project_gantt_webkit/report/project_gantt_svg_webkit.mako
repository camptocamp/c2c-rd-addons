## -*- coding: utf-8 -*-
<%
import datetime
from tools.translate import _
from xml.sax.saxutils import escape

def datum(date) :
    now = datetime.datetime.now().date()
    if date and not date == "False" :
        return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").date()
    else :
        return now
# end def datum    

def category(task, now) :
    c_now = datetime.datetime.strftime(now, date_fmt)
    if not task.date_start or not task.date_end : return "gold"
    elif task.date_start > c_now : return "blue" #"#00C"
    elif task.date_end > c_now : return "firebrick" #"#C00"
    else : return "lightgreen" # "#0C0"
# end def category

def title(name) :
    if len(name) > 26 :
        words = name.split(" ")
        for i in range(len(words)) :
            if len(words[i]) > 26 :
                words[i] = words[i][0:26-3] + "..."
        result = []
        line = ""
        i = 0
        while i < len(words) :
            while (i < len(words)) and (len(line) + len(words[i]) + 1) < 26 :
                line = line + " " + words[i]
                i += 1
            result.append(escape(line))
            if i < len(words) :
                line = words[i]
            else :
                line = ""
            i += 1
        if line :
            result.append(escape(line))
    else :
        result = [escape(name)]
    return result
# end def title

def lines(tasks) :
    return sum(len(title(t.name)) for t in tasks)
# end def lines

def duration(task, now) :
    return (datum(task.date_end) -  datum(task.date_start)).days
# end def duration

def scale(timespan) :
    if timespan < 90 :
        return 15, 15, 1, 13
    elif timespan < 400 :
        return 5, 15, 7, 44
    else :
        return 1, 15, 30, 201
# end def scale

def page_size(header) :
    fmt = header.format
    orient = header.orientation
    format = \
    { 'A0' : (841, 1189)
    , 'A1' : (594, 841)
    , 'A2' : (420, 594)
    , 'A3' : (297, 420)
    , 'A4' : (210, 297)
    , 'A5' : (148, 210)
    , 'A6' : (105, 148)
    , 'A7' : (74, 105)
    , 'A8' : (52, 74)
    , 'A9' : (37, 52)
    , 'B0' : (1000, 1414)
    , 'B1' : (707, 1000)
    , 'B2' : (500, 707)
    , 'B3' : (353, 500)
    , 'B4' : (250, 353)
    , 'B5' : (176, 250)
    , 'B6' : (125, 176)
    , 'B7' : (88, 125)
    , 'B8' : (62, 88)
    , 'B9' : (33, 62)
    , 'B10': (31, 44)
    , 'C5E': (163, 229)
    , 'Comm10E'  : (105, 241)
    , 'DLE'      : (110, 220)
    , 'Executive': (190, 254)
    , 'Folio'    : (210, 330)
    , 'Ledger'   : (431, 279)
    , 'Legal'    : (215, 355)
    , 'Letter'   : (215, 279)
    , 'Tabloid'  : (279, 431)
    }
    if orient == "Portrait" :
        return (int(format[fmt][0] - (header.margin_left + header.margin_right)), int(format[fmt][1] - (header.margin_top + header.margin_bottom)))
    else :
        return (int(format[fmt][1] - (header.margin_left + header.margin_right)), int(format[fmt][0] - (header.margin_top + header.margin_bottom)))
# end def page_size

date_fmt = "%Y-%m-%d %H:%M:%S"
months = [_("Jan"), _("Feb"), _("Mar"), _("Apr"), _("May"), _("Jun"), _("Jul"), _("Aug"), _("Sep"), _("Oct"), _("Nov"), _("Dec")]
workingday = ["white", "white", "white", "white", "white", "silver", "silver"]
color = ["white", "white", "silver"]
now = datetime.datetime.now().date()
#tasks = [t for t in objects if t.date_start and t.date_end]
tasks = [t for t in sorted(objects, key=lambda o: (o.project_id.name, datum(o.date_start), o.name))]
first = min(datum(task.date_start) for task in tasks if task.date_start)
last  = max(datum(task.date_end)   for task in tasks if task.date_end)
tomm = 2.0
chunks = []
chunk = []
for task in tasks :
    project_name = task.project_id.name
    if lines(chunk + [task]) * tomm < page_size(webkit_header)[1] :
        chunk.append(task)
    else :
        chunks.append(chunk)
        chunk = [task]
chunks.append(chunk)
timespan = (last-first).days
dx, dy, d, space = scale(timespan)
%>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>Gantt Chart ${webkit_header.format} ${webkit_header.orientation}</title>
  </head>
      <body style="font-family:Helvetica,sans-serif;font-size:8pt;">
%for tasks in chunks :
        <p style="page-break-inside:avoid">
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          version="1.1" 
          viewBox="0 0 ${(timespan + space)*dx} ${(lines(tasks)+3)*dy}" 
          width="${page_size(webkit_header)[0]}mm"
          height="${int((lines(tasks)+3+len(set([t.project_id.name for t in tasks])))*dy/((timespan + space)*(dx*1.0)/page_size(webkit_header)[0]))}mm"
          preserveAspectRatio="xMinYMin meet">

    %if timespan < 90 :
        <% month = 0 %>
        %for actual in [first + datetime.timedelta(days=i) for i in range(0, timespan, d)] :
            <% x0 = ((actual-first).days + space)*dx %>
            %if actual.month != month :
                <text x="${x0}" y="${dy}">${months[actual.month-1]}'${actual.year % 100}</text>
                <% month = actual.month %>
            %endif
            <rect x="${x0}" y="${dy}" width="${dx}" height="${(lines(tasks)+1+len(set([t.project_id.name for t in tasks])))*dy}" fill="${workingday[actual.isoweekday()-1]}" style="opacity:0.2"/>
            <text x="${x0}" y="${int(dy+(dy*0.8))}">${actual.day}</text>

        %endfor

    %elif timespan < 400 :
        <% month = 0 %>
        %for actual in [first + datetime.timedelta(days=i) for i in range(0, timespan, d)] :
            <% x0 = ((actual-first).days + space)*dx %>
            %if actual.month != month :
                <text x="${x0}" y="${dy}">${months[actual.month-1]}'${actual.year % 100}</text>"""
                <% month = actual.month %>
            %endif

            <rect x="${x0}" y="${dy}" width="${d*dx}" height="${(lines(tasks)+1+len(set([t.project_id.name for t in tasks])))*dy}" fill="${color[actual.isocalendar()[1] % 3]}" style="opacity:0.2"/>
            <text x="${x0}" y="${int(dy+(dy*0.8))}">${_('cw')}${actual.isocalendar()[1]+1}</text>

        %endfor

    %else :
        <% first = datetime.date(first.year, first.month, 1) %>
        <% year = 0 %>
        %for actual in [datetime.date(first.year + (first.month + i-1)/12, ((first.month + i - 1) % 12)+1, 1) for i in range(0, timespan/d)] :
            <% x0 = ((actual-first).days + space)*dx %>
            %if actual.year != year :
                <text x="${x0}" y="${dy}">${actual.year}</text>
                <% year = actual.year %>
            %endif

            <rect x="${x0}" y="${dy}" width="${d*dx}" height="${(lines(tasks)+1+len(set([t.project_id.name for t in tasks])))*dy}" fill="${color[actual.month % 3]}" style="opacity:0.2"/>
            <text x="${x0}" y="${int(dy+(dy*0.8))}">${months[actual.month-1]}</text>
        %endfor

    %endif

    %for i in range(0, lines(tasks)+len(set([t.project_id.name for t in tasks])), 3):
        <rect x="0" y="${(i+2)*dy+4}" width="${((last-first).days + space)*dx}" height="${dy}" fill="whitesmoke" style="opacity:0.4"/>
    %endfor

    <% i = 0 %>
    %for task in tasks :
        %if task.project_id.name != project_name :
            <% project_name = task.project_id.name %>
            <text x="0" y="${(i+3)*dy}" style="fill:blue">${project_name}</text>
            <% i += 1 %>
        %endif

        %for name in title(task.name) :
            <text x="0" y="${(i+3)*dy}">${name}</text>
            <% i += 1 %>
        %endfor

        <rect x="${((datum(task.date_start) - first).days + space)*dx}" y="${(i+2)*dy-dy/2}" width="${max(dx, duration(task, now)*dx)}" height="${dy/2}" fill="${category(task, now)}"/>

    %endfor

        <rect x="${((now - first).days + space)*dx}" y="${dy}" width="${max(1,int(dx*0.5))}" height="${(lines(tasks)+1)*dy}" fill="blue" style="opacity:0.2"/>
      </svg>
      </p>
%endfor
  </body>
</html>

