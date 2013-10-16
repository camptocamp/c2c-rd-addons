<html>
%if context['data'] and context['data'].get('form'):
  <%form = True%>
%else:
  <%form = False%>
%endif


<head>
<b>Projects</b> requested by ${user.name}
</head>

  <body>
    <style  type="text/css">
     table {
       border-collapse: collapse;
       cellspacing="0";
       font-size:10px;
           }
     td {margin: 0px; padding: 3px; border: 1px solid lightgrey;  vertical-align: top; }
    </style> 

<%setLang(user.context_lang)%>

<%
    def partner_tasks(tasks, percentage):
       projects = {}
       task_details = {}
       for task in tasks:
           task_details[task.name] = {'amount_budget': task.amount_budget, 'amount_budget_share': task.amount_budget*percentage, 'years':task.years, 'years_tax':task.years_tax}
           if not projects.get(task.project_id.name):
               projects[task.project_id.name] = {}
           projects[task.project_id.name].update(task_details) 
       return projects
%>

<%
    def company_projects(projects, percentage):
       all_proj = []
       for project in projects:
        if project.location_id: 
         all_tasks = []
         for task in project.tasks:
           task_details = {'task_name': task.name, 'amount_budget': task.amount_budget, 'amount_budget_share': task.amount_budget*percentage, 'years':task.years, 'years_tax':task.years_tax, 'date_start': task.date_start}
           all_tasks.append(task_details)
         all_proj.append({'proj_name':project.name, 'proj_amount_budget':project.amount_budget, 'proj_amount_budget_share':project.amount_budget*percentage ,'tasks':all_tasks})

       return all_proj
%>

<%
    def partner_shares(partner, percentage, lines, level):
        level = level + 1
        for share in partner.participation_current_ids:
           percentage_current = percentage * share.percentage/100
           if share.partner_company_id:
             comp = {'comp_name': share.partner_id.name, 'share': percentage_current, 'level':level, 'comp_amount_budget':share.partner_company_id.amount_budget,'comp_amount_budget_share':share.partner_company_id.amount_budget*percentage_current/100, 'projects': []  }
             if share.partner_company_id.company_project_ids:
                 projects = (company_projects(share.partner_company_id.company_project_ids, percentage_current/100))
                 comp['projects'] = projects
                 lines.append(comp)
             # find participations of the current company
             if share.partner_id.participation_current_ids:
                partner_shares(share.partner_id, percentage_current, lines, level)
        return lines
%>


<%
    amount_budget_tot = 0.0
    amount_budget_share_tot = 0.0
%>

% for partner in objects:
<%
    lines = []
    level = 0
    lines = partner_shares(partner, 100, lines, level)
%>

<!--
<table>
     <tbody >
        <tr>
          <td> 
            ${lines} 
        </td>
       </tr>

     </tbody >
</table>
-->


<h4> Projects affecting: ${partner.name} </h4>

<table>
     <thead >
        <tr>
          <td>Company/Project/Task</td>
          <td>Share</td>
          <td>Budget</td>
          <td>Budget share</td>
          <td>Year start</td>
          <td>Year</td>
          <td>Year Tax</td>
        </tr>
      </thead>
     <tbody >

%for comp in lines:
<tr></tr>
<tr>
<td> L${comp['level']} ${comp['comp_name']} </td>
<td style="text-align:right;"> ${comp['share']} </td>
     <td style="text-align:right;">
${formatLang(round((comp['comp_amount_budget']),0))}
     </td>
     <td style="text-align:right;">
${formatLang(round((comp['comp_amount_budget_share']),0))}
     </td>
</tr>
<%
    amount_budget_tot += round((comp['comp_amount_budget']),0)
    amount_budget_share_tot += round((comp['comp_amount_budget_share']),0) 
%>
%for proj in sorted(comp['projects']):

<tr>
     <td>
       * Projekt: ${proj['proj_name']} 
     </td>
     <td>     </td>
     <td style="text-align:right;">
${formatLang(round((proj['proj_amount_budget']),0))}
     </td>
     <td style="text-align:right;">
${formatLang(round((proj['proj_amount_budget_share']),0))}
     </td>

</tr>

%for task in sorted(proj['tasks']):
     <tr>
     <td>
      ** Task: ${task['task_name']} 
     </td>
     <td>     </td>
     <td style="text-align:right;">
${formatLang(round((task['amount_budget'] ),0))}
     </td>
     <td style="text-align:right;">
${formatLang(round((task['amount_budget_share'] ),0))}
     </td>
     <td style="text-align:right;">
${task['date_start']}
     </td>
     <td style="text-align:right;">
${formatLang(round((task['years'] ),0))}
     </td>
     <td style="text-align:right;">
${formatLang(round((task['years_tax'] ),0))}
     </td>

     </tr>
%endfor


%endfor


%endfor

     <tr>
     <td>
     Total
     </td>
     <td>     </td>
     <td style="text-align:right;">
${formatLang(round((amount_budget_tot ),0))}
     </td>
     <td style="text-align:right;">
${formatLang(round((amount_budget_share_tot ),0))}
     </td>

     </tr>

     </tbody >

</table>
% endfor


</html>

