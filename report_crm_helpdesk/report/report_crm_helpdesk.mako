<html>
  <head/>
  <body>

%for crm in objects :
    <p>
      <b> CRM Helpdesk - Cases </b>
    </p>
    <table class="basic_table" width="90%" style="text-align:left">
      <tr>
        <td>Case:</td>
        <td> ${crm.name or ''|entity} </td>
        <td>Date:</td>
        <td> ${crm.date or ''|entity} </td>
      </tr>
      <tr>
        <td>Partner:</td>
        <td> ${crm.partner_id.title or ''|entity}    ${crm.partner_id.name |entity}   </td>
        <td>Mail:</td>
        <td> ${crm.email_from or ''|entity}  </td>
      </tr>
    </table>
    <p>
      <b> CRM - Messages</b>
    </p>
    <table class="list_table" width="90%">
%for msg in crm.message_ids:
      <tbody>
        <tr>
          <td>${msg.date or ''|entity}  </td>
          <td>${msg.name or ''|entity}  </td>
          <td>
            <p>${msg.message or ''|entity}  </p>
          </td>
          <td>
       %if  msg.description:
          <table  class="text_table">

            %for line in msg.description.split('\n'):  
              <tr><td>${line or ''|entity}</td></tr>
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
