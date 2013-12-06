## -*- coding: utf-8 -*-
<html>
<head>
    <style type="text/css">
        ${css}
        pre {font-family:helvetica; font-size:12;}
    </style>
</head>

<body>
     
    <%setLang(user.context_lang)%>
    <style  type="text/css">
     table {
       border-collapse: collapse;
       cellspacing="0";
       font-size:10px;
       page-break-inside:auto
           }
     tr { page-break-inside:avoid; vertical-align: top;}
     th {margin: 0px; padding: 3px; border: 1px solid grey;   }
     td {margin: 0px; padding: 3px; border: 1px solid lightgrey; page-break-inside:avoid;}
     
     
    </style>
    
    <%
    def carriage_returns(text):
        return text.replace('\n', '<br />')
        
    sorted_objects = sorted(objects, key=lambda o : o.location_id.complete_name )
    %>
    <%
    room = None
    room_total = 0
    total = 0
    %>
   
    <table>
      <thead>
           <tr style=font-weight:bold" >
             <th>${_("Pos")}</th>
             <th>${_("Description")}</th>
             <th style="text-align:right;">${_("Value")} </th>
             <th>${_("Image")} </th>
           <tr>
      </thead>
      <tbody>
        %for inv in sorted_objects :
        
        %if room and room != inv.location_id.complete_name:
           
           <tr style=font-weight:bold" >
             <td/>
             <td>${_("Summe")}</td>
             <td style="text-align:right;">${formatLang(room_total)} </td>
             <td/>
           <tr>
           <tr
           <td colspan="4"/>
           </tr>
           <%
           room_total = 0
           %>
        %endif
        
        %if not room or room != inv.location_id.complete_name: 
           <tr>
             <td/>
             <td style="font-weight:bold">${inv.location_id.name} </td>
             <td/>
             <td/>
           <tr>
           <%
           room = inv.location_id.complete_name
           %>    
        %endif
        
        <tr>
          <td>${inv.position} </td>
          <td>${inv.name|carriage_returns}
            %if inv.partner_id:
              <br> 
              ${inv.partner_id.name}
            %endif
            %if inv.value_ats:
              <br> 
              ATS: ${formatLang(inv.value_ats)}
            %endif
          </td>
          <td  style="text-align:right;">${formatLang(inv.value)} </td>
          <td>
           %if inv.image:
             ${helper.embed_image('png',inv.image, width=200)}
           %endif
          </td>
        </tr>
        <%
        room_total += inv.value
        total += inv.value
        %>
        
        
        
          %endfor

      </tbody>

      <tfoot>
           <tr style=font-weight:bold" >
             <td/>
             <td>${_("Summe")}</td>
             <td style="text-align:right;">${formatLang(room_total)} </td>
             <td/>
           <tr>

            <tr  style="font-weight:bold">
             <td/>
             <td>${_("Gesamtsumme")}</td>
             <td style="text-align:right;">${formatLang(total)} </td>
             <td/>
           <tr>
      </tfoot>
      
    <table>
</body>
</html>
