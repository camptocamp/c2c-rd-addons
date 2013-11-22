## -*- coding: utf-8 -*-
<html>
  <head/>
  <body>
<style  type="text/css">
     table {
       border-collapse: collapse;
       page-break-after:auto;
       cellspacing="5";
       font-size:12px;
           }
td {margin: 0px; padding: 3px; border: 1px solid lightgrey;  vertical-align: top; }
</style>
%for crm in objects :
    <p>
      <b> CRM Helpdesk - Cases </b>
    </p>
    <table class="basic_table"  style="text-align:left">
      <tr>
        <td>Case:<br>
        Date:<br>
        Partner:<br>
        Mail:</td>
        <td> ${crm.name or ''|entity} <br>
        ${crm.date or ''|entity} <br>
        ${crm.partner_id.title or ''|entity}    ${crm.partner_id.name |entity}   <br>
        ${crm.email_from or ''|entity}  </td>
      </tr>
    </table>
    <p>
      <b> CRM - Messages</b>
    </p>
    <table class="list_table"  >
%for msg in crm.message_ids:
      <tbody 
        <tr>
          <td>${msg.date or ''|entity}  </td>
          <td>${msg.subject or ''|entity}  </td>
        </tr>
        <tr>
          <td>
            <p>${msg.subject or ''|entity}  </p>
          </td>
          <td>
       %if  msg.body_text:
          <table> 
            %for line in msg.body_text.split('\n'):  
              <tr><td style="border:white" ">${line or ''|entity}</td></tr>
            %endfor
         </table>
        %else:
               <p>
      <b> test </b>
    </p>
        %endif
          </td>
        </tr>
      </tbody>
 %endfor
    </table>
%endfor
  </body>
</html>
