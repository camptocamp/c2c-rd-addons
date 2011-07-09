<html>
<head>
    <style type="text/css">
        ${css}
        pre {font-family:helvetica; font-size:12;}
    </style>
</head>
<body>
    <style  type="text/css">
     table {
       width: 100%;
       page-break-after:auto;
       border-collapse: collapse;
       cellspacing="0";
       font-size:12px;
           }
     td {width: 50%; margin: 0px; padding: 3px; border: 1px solid lightgrey;  vertical-align: top; }
     pre {font-family:helvetica; font-size:13;}
    </style>
    %for pick in objects :
    <% setLang(pick.partner_id.lang) %>
<br>
<br>
<br>
<br>
    <table >
        %if pick.company_id.address_label_position == 'left':
         <tr>
         <td>
           <pre>
${pick.address_id.address_label}
           <pre>
         </td>
         <td>
         %if pick.address_id.phone :
${_("Phone")}: ${pick.address_id.phone|entity} <br>
        %endif
        %if pick.address_id.fax :
${_("Fax")}: ${pick.address_id.fax|entity} <br>
        %endif
        %if pick.address_id.email :
${_("Mail")}: ${pick.address_id.email|entity} <br>
        %endif
        %if pick.partner_id.vat :
${_("VAT")}: ${pick.partner_id.vat|entity} <br>
        %endif
         </td>

        </tr>
        %endif

        %if pick.company_id.address_label_position == 'right' or not pick.company_id.address_label_position:
         <tr>
         <td>
         %if pick.address_id.phone :
${_("Tel")}: ${pick.address_id.phone|entity} <br>
        %endif
        %if pick.address_id.fax :
${_("Fax")}: ${pick.address_id.fax|entity} <br>
        %endif
        %if pick.address_id.email :
${_("E-mail")}: ${pick.address_id.email|entity} <br>
        %endif
        %if pick.partner_id.vat :
${_("VAT")}: ${pick.partner_id.vat|entity} <br>
        %endif
         </td>
         <td>
           <pre>
${pick.address_id.address_label}
           <pre>
         </td>
        </tr>
        %endif

    </table>
    <br />
    %if pick.type == 'out' :
    <span class="title">${_("Delivery Out")} ${pick.name or ''|entity}</span>
    %elif pick.type == 'in' :
    <span class="title">${_("Delivery In")} ${pick.name or ''|entity}</span>   
    %elif pick.type == 'production' :
    <span class="title">${_("Production")} ${pick.name or ''|entity}</span> 
    %elif pick.type == 'delivery' :
    <span class="title">${_("Delivery")} ${pick.name or ''|entity}</span> 
    %elif pick.type == 'internal' :
    <span class="title">${_("Internal Picking")} ${pick.name or ''|entity}</span> 
    %endif
    <br/>
    <br/>
    <table class="basic_table" width="90%">
        <tr><td>${_("Document")}</td>
            <td style="white-space:nowrap">${_("Picking Date")}</td>
          %if pick.carrier_id:
            <td style="white-space:nowrap">${_("Carrier")}</td>
          %endif
          %if pick.origin and pick.origin not in (pick.sale_id.name,pick.purchase_id.name):
            <td style="white-space:nowrap">${_("Origin")}</td>
          %endif
          %if  pick.sale_id or pick.purchase_id:
            <td style="white-space:nowrap">${_("Reference")}</td>
          %endif
          %if pick.sale_id.client_order_ref:
            <td style="white-space:nowrap">${_("Client Reference")}</td>
          %endif
        </tr>
        <tr><td>${pick.name or ''}</td>
          <td>
               %if pick.max_date:
               ${pick.max_date}
               %endif
          </td>
           %if pick.carrier_id:
          <td>${pick.carrier_id.name}</td>
           %endif          
          %if pick.origin and pick.origin not in (pick.sale_id.name,pick.purchase_id.name):
            <td style="white-space:nowrap">${pick.origin}</td>
          %endif

           %if pick.sale_id or pick.purchase_id:
         <td>${pick.sale_id.name or pick.purchase_id.name or ''}</td>
           %endif
         
        %if pick.sale_id.client_order_ref:
           <td>${pick.sale_id.client_order_ref}</td>
        %endif
          </tr>
    </table>
    <h1><br /></h1>
    <table class="list_table"  width="90%">
        <thead>
          <tr>
            <th>${_("Description")}</th>
       %if pick.print_uom:
            <th class>${_("Quantity UoM")}</th><th style="text-align:left;">${_("UoM")}</th>
       %endif
            <th class>${_("Quantity")}</th><th style="text-align:left;white-space:nowrap;">${_("UoS")}</th>
            <th style="text-align:left;">${_("Source Location")}</th>
            <th style="text-align:left;">${_("Destination Location")}</th>
         </tr>
        </thead>
        %for line in pick.move_lines :
        <tbody>
        <tr>
           <td>${line.name|entity}</td>
       %if pick.print_uom:
           <td style="white-space:nowrap;text-align:right;">${line.product_qty}</td>
           <td style="white-space:nowrap;text-align:left;">${line.product_uom.name or ''}</td>
       %endif
           <td style="white-space:nowrap;text-align:rigth;">${line.product_uos_qty or ''}</td>
           <td style="white-space:nowrap;text-align:left;">${line.product_uos.name or ''}</td>
           <td style="white-space:nowrap;text-align:left;">${line.location_id.name or ''}</td>
           <td style="white-space:nowrap;text-align:right;">${line.location_dest_id.name or ''}</td>
        </tr>
        %if line.note :
        <tr><td colspan="6" style="border-style:none"><pre style="font-family:Helvetica;padding-left:20px;font-size:10">${line.note |entity}</pre></td></tr>
        %endif
        %endfor
        </tbody>
    </table>
<br>
       %if pick.tractor_gross :
    <table class="list_table" style="width:40%;border:1px solid grey">
        <tr><th>${_("text")}</th><th style="text-align:left;">${_("Tractor")}</th><th style="text-align:left;">${_("Trailer")}</th></tr>
        <tr>
            <td style="border:1px solid grey">${_("Net")}</td>
            <td style="text-align:right;border:1px solid grey">${ formatLang(tractor_net)}</td>
            <td style="text-align:right;border:1px solid grey">${ formatLang(trailer_net) }</td>
        </tr>
        <tr>
            <td style="border-style:none">${_("Tare")}</td>
            <td style="text-align:right;border:1px solid grey">${ formatLang(tractor_tare)}</td>
            <td style="text-align:right;border:1px solid grey">${ formatLang(trailer_tare) }</td>
        </tr>
        <tr>
            <td style="border-style:none">${_("Gross")}</td>
            <td style="text-align:right;border:1px solid grey">${ formatLang(tractor_gross)}</td>
            <td style="text-align:right;border:1px solid grey">${ formatLang(trailer_gross) }</td>
        </tr>
        %endif
    </table>        
    %if pick.note_print:
    <pre>${pick.note_print}</pre>
    %endif:
    <p style="page-break-after:always"></p>
    %endfor
</body>
</html>
