<html>
  <head/>
  <body>


<%def name="numbering(val,flag='init')">
   
</%def>

<%def name="level_decimal(level,parent_level)">
  % if level < parent_level :
       param = 'up' ${level},${parent_level}  /> 
  % endif
  % if level == parent_level :
       param = 'next' ${level},${parent_level}  />
  % endif
  % if level > parent_level :
       param = 'down' ${level},${parent_level}  />
  % endif
       
</%def>

    <p>
      <b> Account-Chart Sum </b>
    </p>

    <table class="basic_table" width="90%" style="text-align:left">
     <thead>
        <tr>
          <td>Level</td>
          <td>Num</td>
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
          <td><%self:level_decimal level="${account.level or 0}" parent_level="${account.parent_id.level or 0}"></%self:level_decimal></td>
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

