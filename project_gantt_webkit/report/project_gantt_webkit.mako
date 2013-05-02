<html>
<head>
    <style type="text/css">
        ${css}
        pre {font-family:helvetica; font-size:12;}
    </style>
</head>

<body>

%for task in objects:

<%
    from googlegantt import GanttChart, GanttCategory
    chart_title = 'test'
    chart_width = 650
    chart_heigth = 200
    now = datetime.datetime.today()
    chart_date = now.strftime('(%Y,%m,%d)')


    gc = GanttChart(chart_title, chart_width, chart_height, progress=chart_date)

    on_time = GanttCategory(_('On Time'), '0c0')
    late = GanttCategory(_('Late'), 'c00')
    upcoming = GanttCategory(_('Upcoming'), '00c')
    project = GanttCategory(_('Project'), '00c')

    objects_sorted = objects_sorted
    # sort by project start, task start
    
    
    project_name = ''
    
    for task in objects_sorted:
        if task.project_id.project_name != project_name
            project_name = task.project_id.project_name
            project_start = 
            project_end = 
            gc.add_task(project_name, project_start,project_end, category=project)
        if task.date_end > now:
            categ = 'late'
        elif task.date_start > now:
            categ = 'upcoming'
        else: 
            categ = 'on_time'
        gc.add_task(task.name, task.date_start,task.date_end, category=categ)
        

    #url = gc.get_url()
    #print url
    #webbrowser.open('%s' % url)
    image = gc.get_image('tmp.png')
%>

${helper.embed_image('png', image, width=250)}

%endfor


</body>
</html>
