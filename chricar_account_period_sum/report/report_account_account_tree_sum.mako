<html>
  <head/>
  <body>

<%
chapter.__init__()
%>

    <p>
      <b> Account-Chart Sum </b>
    </p>

    <table class="basic_table" width="90%" style="text-align:left">
     <thead>
        <tr>
          <td>Level</td>
          <td>Chapter</td>
          <td>Code</td>
          <td>Name</td>
          <td align="right">Debit</td>
          <td align="right">Credit</td>
          <td align="right">Balance</td>
        </tr>
      </thead>


 %for account in objects :
     <tbody>
        <tr>
          <td>${account.level or ''|entity}  </td>
          <td>
              %if account.type == 'view':
                 ${chapter.get_structure(account.level) or ''|entity}
              %endif  
          </td>
          <td>${account.code or ''|entity}  </td>
          <td>${account.name or ''|entity}  </td>
          <td align="right">${account.debit or ''|entity} </td>
          <td align="right">${account.credit or ''|entity} </td>
          <td align="right">${account.balance or ''|entity} </td>
        </tr>
      </tbody>
 %endfor
    </table>



  </body>
</html>
