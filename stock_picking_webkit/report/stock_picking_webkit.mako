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
     td { margin: 0px; padding: 3px; border: 1px solid lightgrey;  vertical-align: top; }
     pre {font-family:helvetica; font-size:13;}
    </style>
    %for pick in objects :
<br>
    <% setLang(pick.partner_id.lang) %>
    <table >
        %if pick.company_id.address_label_position == 'left':
         <tr>
         <td style="width:50%">
${_("Shipping Address")}   
<hr>
           <pre>
${pick.address_id.address_label}
           <pre>
         </td>
         <td style="width:50%">
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
        %if pick.partner_customer_id and  pick.address_id and pick.partner_customer_id.id != pick.address_id.partner_id.id :
${_("Customer")}: ${pick.partner_customer_id.name|entity} <br>
        %endif
   
         </td>

        </tr>
        %endif

        %if pick.company_id.address_label_position == 'right' or not pick.company_id.address_label_position:
         <tr>
         <td style="width:50%">
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
        %if pick.partner_customer_id and pick.address_id and pick.partner_customer_id.id != pick.address_id.partner_id.id :
${_("Customer")}: ${pick.partner_customer_id.name|entity} <br>
        %endif

         </td>
         <td style="width:50%">
${_("Shipping Address")}
<hr>
           <pre>
${pick.address_id.address_label}
           <pre>
         </td>
        </tr>
        %endif
    </table>

    <br />
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
%if pick.state == 'cancel':
   <span class="title"> ${pick.state} </span>
%endif 
    <br/>
    <br/>
    <table  style="width:90%">
        <tr>
          %if pick.origin and pick.origin not in [ pick.sale_id.name,pick.purchase_id.name]  :
            <td>${_("Document")}</td>
          %endif
            <td style="white-space:nowrap">${_("Picking Date")}</td>
          %if pick.carrier_id:
            <td style="white-space:nowrap">${_("Carrier")}</td>
          %endif
          %if pick.sale_id or pick_purchase_id:
            <td style="white-space:nowrap">${_("Reference")}</td>
          %endif
          %if pick.total_gross:
            <td>${_("Weight")}</td>
          %endif
        </tr>
        <tr>
            %if pick.origin and pick.origin not in [ pick.sale_id.name,pick.purchase_id.name]  :
            <td>
               ${pick.origin}
            </td>
            %endif
             <td>
            %if pick.max_date:
               ${pick.max_date}</td>
            %endif
            %if pick.carrier_id:
             <td>
               ${pick.carrier_id }
             </td>
           %endif
           %if pick.sale_id or pick_purchase_id:
             <td>${pick.sale_id.name or pick.purchase_id.name or ''}</td>
           %endif
          %if pick.total_gross:
         <td>${pick.total_gross}</td></tr>
           %endif
    </table>
    <h1><br /></h1>
    <table style="width:90%">
        <thead>
          <tr>
            <th>${_("Description")}</th>
%if pick.print_uom:
            <th style="text-align:center;">${_("Quantity")}</th><th class style="text-align:left;">${_("UoM")}</th>
%endif
            <th style="text-align:center;white-space:nowrap">${_("UoS Qty")}</th><th style="text-align:left;white-space:nowrap;">${_("UoS")}</th>
            <th style="text-align:center;">${_("Source Location")}</th>
            <th style="text-align:center;">${_("Destination Location")}</th>
         </tr>
        </thead>
        %for line in pick.move_lines :
        <tbody>
        <tr>
           <td>${line.name|entity}</td>
%if pick.print_uom:
           <td style="white-space:nowrap;text-align:right;">${str(line.product_qty).replace(',000','') or '0'}</td>
           <td style="white-space:nowrap;text-align:left;">${line.product_uom.name or ''}</td>
%endif
           <td style="white-space:nowrap;text-align:right;">${str(line.product_uos_qty).replace(',000','') or '0'}</td>
           <td style="white-space:nowrap;text-align:left;">${line.product_uos.name or ''}</td>
           <td style="white-space:nowrap;text-align:left;">${line.location_id.name or ''}</td>
           <td style="white-space:nowrap;text-align:left;">${line.location_dest_id.name or ''}</td>
        </tr>
        %if line.note :
        <tr><td colspan="6" style="border-style:none"><pre style="font-family:Helvetica;padding-left:20px;font-size:10">${line.note |entity}</pre></td></tr>
        %endif
        %endfor
        </tbody>
    </table>
<br>
       %if pick.tractor_gross :
    <table style="text-align:right;border:1px solid grey;width:40%">
        <tr style="text-align:left;border:1px solid grey;"><th>${_("Weight")}</th> <th>${_("Tractor")}</th>  <th>${_("Trailer")}</th> </tr>
        <tr>
            <td style="text-align:left;">${_("Net")}</td>
            <td>${ formatLang(pick.tractor_net or '')}</td>
            <td>${ formatLang(pick.trailer_net or '') }</td>
        </tr>
        <tr>
            <td style="text-align:left;">${_("Tare")}</td>
            <td >${ formatLang(pick.tractor_tare or '')}</td>
            <td i>${ formatLang(pick.trailer_tare or '') }</td>
        </tr>
        <tr>
            <td style="text-align:left;">${_("Gross")}</td>
            <td >${ formatLang(pick.tractor_gross or '')}</td>
            <td >${ formatLang(pick.trailer_gross or '') }</td>
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
