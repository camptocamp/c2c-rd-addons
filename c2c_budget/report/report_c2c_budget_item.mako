<html>
<head>
                <b>Budget Structure</b> requested by ${user.name}
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

<p>
Selection:
%if context['data'] :
<%doc>
    FIXME - print default or actual paramaters
            waiting for Nicalas to fix bug and pass form params
</%doc>
  <table>
            <tr>
            <td>budget: year to current month</td>
            <td>real: year to current month </td>
            </tr>
  </table>
%endif
<p>
<%
chapter.__init__()
%>

    <table  >

     <thead >
        <tr>
          <td>Level</td>
          <td>Chapter</td>
          <td>Code</td>
          <td>Name</td>
          <td align="right">Balance Budget</td>
          <td align="right">Balance Real</td>
          <td align="right">Real - Budget</td>
        </tr>
      </thead>

 %for account in objects :
     <tbody >
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
          <td align=right NOWRAP>${formatLang(account.balance_budget)  or ''|entity} </td>
          <td align=right NOWRAP>${formatLang(account.balance_real) or ''|entity} </td>
          <td align=right NOWRAP>${formatLang(account.balance_real-account.balance_budget) or ''|entity} </td>
        </tr>
            %endif
      </tbody>
 %endfor
    </table>


  </body>
</html>

