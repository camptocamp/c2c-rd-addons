<html>
<head>
    <style type="text/css">
        ${css}
        pre {font-family:helvetica; font-size:12;}
    </style>
</head>

<body>
<%
    
    objects_sorted = sorted(objects, key=lambda o : o.project_id.name)
    objects_sorted = sorted(objects_sorted, key=lambda o : o.date_start )
    
    task_ids = []
    project_ids = []
    for o in objects_sorted:
        task_ids.append(o.id)
        if o.project_id.id not in project_ids:
            project_ids.append(o.project_id.id)

    
    import datetime
    import time
    from googlegantt import GanttChart, GanttCategory
    from tools.translate import _
    import base64
    

   
    chart_title = _('Gantt Chart')
    chart_width = 950
    chart_heigth = max((len(task_ids) + len(project_ids)) * 30,100)
    now = datetime.datetime.today()
    now_c = now.strftime('%Y-%m-%d  %H:%M:%S')
    tomorrow = now +  datetime.timedelta(days=1)
    tomorrow_d = tomorrow.date()
    now_d = now.date()
    
    gc = GanttChart(chart_title,  width=chart_width,  height=chart_heigth, progress=now.date())
    
    
    on_time = GanttCategory(_('On Time'), '0c0')
    late = GanttCategory(_('Late'), 'c00')
    undefined = GanttCategory(_('Undefined'), 'dd0')
    upcoming = GanttCategory(_('Upcoming'), '00c')
    project = GanttCategory(_('Project'), 'ff0')
   
    def date_convert(d, delta=None):
        try:
            d_tuple = datetime.datetime.strptime(d, '%Y-%m-%d  %H:%M:%S').date() 
        except:
            if delta:
               d_tuple = tomorrow_d
            else:
               d_tuple = now_d
            
        return d_tuple

    project_name = ''

    for task in objects_sorted:
        
        if task.project_id.name != project_name:
            project_start = task.date_start
            project_end = task.date_end
            
            for t in task.project_id.tasks:
                if (not t.date_start or  t.date_start < project_start) and t.id in task_ids:
                    project_start = t.date_start 
                if (not t.date_end or t.date_end  > project_end) and t.id in task_ids:
                    project_end = t.date_end 
            
            project_name = task.project_id.name.encode('ascii', 'replace')
            project_start =  date_convert(project_start) 
            project_end =   date_convert(project_end,1)

            gc.add_task(project_name, project_start,project_end, category=project)
            
        if not task.date_start  or  not task.date_end :
            categ = undefined    
        elif task.date_end  > now_c:
            categ = late
        elif task.date_start  > now_c:
            categ = upcoming
        else: 
            categ = on_time
        
        gc.add_task(task.name.encode('ascii', 'replace'), date_convert(task.date_start), date_convert(task.date_end,1) , category=categ)
    
    #file_name = '/tmp/t.png'
    
    image = gc.get_image(file_name)
    
    pic = base64.encodestring(file(file_name, 'rb').read())
    import os
    os.remove(file_name)
%>
 
${helper.embed_image('png', pic )}




</body>
</html>
