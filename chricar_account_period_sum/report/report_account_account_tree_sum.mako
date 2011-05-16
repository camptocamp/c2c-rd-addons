<html>
  <head/>
  <body>


    <p>
      <b> Account-Chart Sum </b>
    </p>

    <table class="basic_table" width="90%" style="text-align:left">
     <thead>
        <tr>
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

