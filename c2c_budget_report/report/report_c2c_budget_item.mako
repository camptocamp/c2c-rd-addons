## -*- coding: utf-8 -*-
<html>
%if context['data'] and context['data'].get('form'):
  <%form = True%>
%else:
  <%form = False%>
%endif

<head>
                <b>Budget Structure</b> requested by ${user.name}
</head>

  <body>
    <%setLang(user.context_lang)%>
    <style  type="text/css">
     table {
       border-collapse: collapse;
       cellspacing="0";
       font-size:10px;
           }
     td {margin: 0px; padding: 3px; border: 1px solid lightgrey;  vertical-align: top; }
    </style>

<p>
Selection:
%if form :

  <table>
            <tr>
            <td>current year: ${context['data']['form']['period_from_name']} - ${context['data']['form']['period_to_name']}</td>
            <td>budget year: ${context['data']['form']['period_budget_from_name']} - ${context['data']['form']['period_budget_to_name']}</td>
%if context['data']['form']['print_budget_1000'] == 1:
            <td>budget year in 1000</td>
%endif
<% print_view_only = False %>
%if form and context['data']['form']['print_views_only'] == 1:
            <td>print only views</td>
<% print_view_only = True %>
%endif
            </tr>
  </table>

%else:
  <table>
            <tr>
            <td>current: all posted</td>
            <td>budget: year to current month </td>
            </tr>
  </table>
%endif
</p>



<%chapter = helper.chapter() %>


    <table  >

     <thead >
        <tr>
          <td>Level</td>
          <td>Chapter</td>
          <td>Code</td>
          <td>Name</td>
          <td align="right">Balance Real</td>
          <td align="right">Balance Budget</td>
          <td align="right">Real - Budget</td>
          <td align="right">Diff %</td>
        </tr>
      </thead>

 %for account in objects :
     <tbody >
    %if (print_view_only == True and account.type == 'view') or print_view_only == False :        
        %if (account.balance_budget !=0 or account.balance_real ):
        <tr>
          <td>${account.level or ''|entity}  </td>
          <td>
              %if account.type == 'view':
                 ${chapter.get_structure(account.level) or ''|entity}
              %endif
          </td>
          <td>${account.code or ''|entity}  </td>
          <td>
              %if account.type == 'view' :
                <b>
              %endif
               ${account.name or ''|entity}  </td>
              %if account.type == 'view' :
                </b>
              %endif
          <td align=right NOWRAP>${formatLang(account.balance_real) or ''|entity} </td>
          <td align=right NOWRAP>${formatLang(account.balance_budget)  or ''|entity} </td>
          <td align=right NOWRAP>${formatLang(account.balance_real-account.balance_budget) or ''|entity} </td>
 %if account.balance_budget != 0 :
          <td align=right NOWRAP>${formatLang((account.balance_real-account.balance_budget)*100/account.balance_budget ) or ''|entity} </td>
 %else:
          <td align=right NOWRAP>${_('NA')} </td>
 %endif
        </tr>
        %endif
       %endif
      </tbody>
 %endfor
    </table>


  </body>
</html>

