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
       font-size:10px;
           }
     td { margin: 0px; padding: 3px; border: 1px solid lightgrey;  vertical-align: top; }
     pre {font-family:helvetica; font-size:13;}
    </style>
    %for order in objects :
<br>
    <% setLang(order.partner_id.lang) %>
    <table >
        %if order.company_id.address_label_position == 'left':
         <tr>
         <td style="width:50%">
${_("Shipping Address")}   
<hr>
           <pre>
${order.address_id.address_label}
           <pre>
         </td>
         <td style="width:50%">
         %if order.address_id.phone :
${_("Phone")}: ${order.address_id.phone|entity} <br>
        %endif
        %if order.address_id.fax :
${_("Fax")}: ${order.address_id.fax|entity} <br>
        %endif
        %if order.address_id.email :
${_("Mail")}: ${order.address_id.email|entity} <br>
        %endif
        %if order.partner_id.vat :
${_("VAT")}: ${order.partner_id.vat|entity} <br>
        %endif
   
         </td>

        </tr>
        %endif

        %if order.company_id.address_label_position == 'right' or not order.company_id.address_label_position:
         <tr>
         <td style="width:50%">
         %if order.address_id.phone :
${_("Tel")}: ${order.address_id.phone|entity} <br>
        %endif
        %if order.address_id.fax :
${_("Fax")}: ${order.address_id.fax|entity} <br>
        %endif
        %if order.address_id.email :
${_("E-mail")}: ${order.address_id.email|entity} <br>
        %endif
        %if order.partner_id.vat :
${_("VAT")}: ${order.partner_id.vat|entity} <br>
        %endif

         </td>
         <td style="width:50%">
${_("Shipping Address")}
<hr>
           <pre>
${order.address_id.address_label}
           <pre>
         </td>
        </tr>
        %endif
    </table>

    <br />
    <br />

    %if order.state == 'draft' :
    <span class="title">${_("Quotation N°")} ${order.name or ''|entity}</span>
    %elif order.state == 'cancel' :
    <span class="title">${_("Sale Order Canceled")} ${order.name or ''|entity}</span>
    %else :
    <span class="title">${_("Order N°")} ${order.name or ''|entity}</span>
    %endif
    <br/>
    <table  style="width:100%">
        <tr>
          %if order.client_order_ref:
            <td>${_("Reference")}</td>
          %endif
            <td style="white-space:nowrap">${_("Order Date")}</td>
          %if order.carrier_id:
            <td style="white-space:nowrap">${_("Carrier")}</td>
          %endif
          %if order.user_id:
            <td style="white-space:nowrap">${_("Salesman")}</td>
          %endif
          %if order.payment_term :
            <td style="white-space:nowrap">${_("Payment Term")}</td>
          %endif
        </tr>
        <tr>
            %if order.client_order_ref:
            <td>
               ${order.client_order_ref:}
            </td>
            %endif
             <td>
            %if order.date:
               ${order.date or ''}</td>
            %endif
            %if order.carrier_id:
             <td>
               ${order.carrier_id.name }
             </td>
           %endif
           %if order.user_id :
             <td>${order.user_id.nam or ''}</td>
           %endif
          %if order.payment_term :
            <td style="white-space:nowrap">${order.payment_term}</td>
          %endif
    </table>
    <h1><br /></h1>
    <table style="width:100%">
        <thead>
          <tr>
            <th>${_("Description")}</th>
%if order.print_uom:
            <th style="text-align:center;">${_("Quantity")}</th><th class style="text-align:left;">${_("UoM")}</th>
%endif
%if order.print_uos:
            <th style="text-align:center;white-space:nowrap">${_("UoS Qty")}</th><th style="text-align:left;white-space:nowrap;">${_("UoS")}</th>
%endif
%if order.print_ean:
            <th style="text-align:center;">${_("EAN")}</th>
%endif
%if order.print_packing:
            <th style="text-align:center;">${_("Pack")}</th>
            <th style="text-align:center;">${_("Packaging")}</th>
%endif
         </tr>
        </thead>
        %for line in order.order_line :
        <tbody>
        <tr>
           <td>${line.name|entity}</td>
%if order.print_uom:
           <td style="white-space:nowrap;text-align:right;">${str(line.product_qty).replace(',000','') or '0'}</td>
           <td style="white-space:nowrap;text-align:left;">${line.product_uom.name or ''}</td>
%endif
%if order.print_uos:
           <td style="white-space:nowrap;text-align:right;">${str(line.product_uos_qty).replace(',000','') or '0'}</td>
           <td style="white-space:nowrap;text-align:left;">${line.product_uos.name or ''}</td>
%endif
%if order.print_ean:
           <td style="white-space:nowrap;text-align:left;">${line.product_packaging.ean or line.product_id.ean13 or ''}</td>
%endif
%if order.print_packing:
           <td style="white-space:normal;text-align:left;">${line.product_packaging.qty and line.product_qty/line.product_packaging.qty or ''}</td>
           <td style="white-space:normal;text-align:left;">${line.product_packaging and line.product_packaging.ul.name or ''} ${line.product_packaging and _(" / " or '')} ${line.product_packaging and line.product_packaging.qty or ''} ${line.product_packaging and line.product_id.uom_id.name or ''}</td>
%endif
        </tr>
        %if line.note :
        <tr><td colspan="6" style="border-style:none"><style="font-family:Helvetica;padding-left:20px;font-size:10;"white-space:normal;">${line.note |entity}</pre></td></tr>
        %endif
        %endfor
        </tbody>
    </table>

%if order.note and 'note_print' not in order._columns:
<br>
    <pre>${order.note}</pre>
%endif:
%if 'note_print' in order._columns and order.note_print:
<br>
    <pre>${order.note_print}</pre>
%endif:


    <p style="page-break-after:always"></p>
    %endfor 
</body>
</html>
