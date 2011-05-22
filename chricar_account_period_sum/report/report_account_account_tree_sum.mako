<html>
<head>
                <b>Account-Chart Sum</b>
</head>

  <body>
    <style>
     table {
       border-collapse: collapse;
       cellspacing="0"
           }
     td {margin: 0px; padding: 3px; border: 1px solid grey; }
    </style> 

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
          <td align="right">Opening Balance</td>
          <td align="right">Debit</td>
          <td align="right">Credit</td>
          <td align="right">Balance</td>
          <td align="right">Balance Prev</td>
        </tr>
      </thead>


 %for account in objects :
     <tbody >
        <tr>
          <td>${account.level or ''|entity}  </td>
          <td>
              %if account.type == 'view':
                 ${chapter.get_structure(account.level) or ''|entity}
              %endif  
          </td>
          <td>${account.code or ''|entity}  </td>
          <td>${account.name or ''|entity}  </td>
          <td align="right">${formatLang(account.opening_balance_sum) or ''|entity} </td>
          <td align="right">${formatLang(account.debit_sum) or ''|entity} </td>
          <td align="right">${formatLang(account.credit_sum) or ''|entity} </td>
          <td align="right">${formatLang(account.balance_sum) or ''|entity} </td>
          <td align="right">${account.balance_prev_sum or ''|entity} </td>
        </tr>
      </tbody>
 %endfor
    </table>


  </body>
</html>
