## -*- coding: utf-8 -*-
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
    
     th { margin: 0px; padding: 3px; border: 1px solid Grey;  vertical-align: top; }
     pre {font-family:helvetica; font-size:13;}
    </style>
    <%
    def carriage_returns(text):
        return text.replace('\n', '<br />')
    %>

    %for pick in objects :
    
    <style  type="text/css">
    %if 'print_cell_borders' in pick.company_id._columns and pick.company_id.print_cell_borders:
       td { margin: 0px; padding: 3px; border: 1px solid #E3E3E3;  vertical-align: top; }
    %else:
       td { margin: 0px; padding: 3px; border: 1px solid White;  vertical-align: top; }
    %endif    
    </style>
    
<br>
    <%setLang(pick.partner_id and pick.partner_id.lang) or pick.partner_id and setLang(pick.partner_id.lang) or setLang(pick.company_id.partner_id.lang)%>

    
    <table >
    <!--
    Left Address
    -->
        %if pick.company_id.address_label_position == 'left':
         <tr style="min-hight:4cm">
         <td style="width:50% ;min-height:100px;">
${_("Shipping Address")}   
<hr>
${pick.partner_id and pick.partner_id.address_label|carriage_returns or ''}
         </td>
         <td style="width:50%">
    %if 'print_address_info' in pick.company_id._columns and pick.company_id.print_address_info:
        %if pick.partner_id.phone :
${_("Phone")}: ${pick.partner_id.phone|entity} <br>
        %endif
        %if pick.partner_id.fax :
${_("Fax")}: ${pick.partner_id.fax|entity} <br>
        %endif
        %if pick.partner_id.email :
${_("Mail")}: ${pick.partner_id.email|entity} <br>
        %endif
        %if (pick.partner_id and pick.partner_id.vat) or (pick.partner_id and pick.partner_id.vat):
${_("VAT")}: ${pick.partner_id and pick.partner_id.vat or pick.partner_id.partner_id.vat|entity} <br>
        %endif
        %if pick.partner_id and pick.sale_id and pick.sale_id.partner_id and pick.partner_id.address_label != pick.sale_id.partner_id.address_label:
        <b>${_("Ordering Contact")}</b><br>
        ${pick.sale_id.partner_id.address_label|carriage_returns or ''}
        %endif
     %endif
         </td>

        </tr>
        %endif

        %if pick.company_id.address_label_position == 'right' or not pick.company_id.address_label_position:
         <tr style="min-hight:4cm">
         <td style="width:50%">
%if 'print_address_info' in pick.company_id._columns and pick.company_id.print_address_info:
        %if pick.partner_id.phone :
${_("Phone")}: ${pick.partner_id.phone|entity} <br>
        %endif
        %if pick.partner_id.fax :
${_("Fax")}: ${pick.partner_id.fax|entity} <br>
        %endif
        %if pick.partner_id.email :
${_("E-mail")}: ${pick.partner_id.email|entity} <br>
        %endif
        %if (pick.partner_id and pick.partner_id.vat) or (pick.partner_id and pick.partner_id.vat):
${_("VAT")}: ${pick.partner_id and pick.partner_id.vat or pick.partner_id.partner_id.vat|entity} <br>
        %endif
%if pick.partner_id and pick.sale_id and pick.sale_id.partner_id and pick.partner_id.address_label != pick.sale_id.partner_id.address_label:
        <b>${_("Ordering Contact")}</b><br>
        ${pick.sale_id.partner_id.address_label|carriage_returns or ''}
%endif
%endif

         </td>
         <td style="width:50%">
${_("Shipping Address")}
<hr>
${pick.partner_id and pick.partner_id.address_label|carriage_returns or ''}
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
    <span class="title">${_("Internal Packing")} ${pick.name or ''|entity}</span> 
    %endif
%if pick.state != 'done':
   <span class="title"> ${pick.state} </span>
%endif 
    <br/>

    <table  style="width:100%">
      <thead style="border:1px solid #E3E3E3">
        <tr>
          %if pick.origin and pick.origin not in [ pick.sale_id.name]  :
            <th>${_("Document")}</th>
          %endif
            <th style="white-space:nowrap">${_("Packing Date")}</th>
          %if pick.carrier_id:
            <th style="white-space:nowrap">${_("Carrier")}</th>
          %endif
          %if pick.carrier_tracking_ref:
            <th style="white-space:nowrap">${_("Carrier Ref")}</th>
          %endif
          %if pick.sale_id :
            <th style="white-space:nowrap">${_("Reference")}</th>
          %endif
          %if pick.sale_id and pick.sale_id.client_order_ref :
            <th style="white-space:nowrap">${_("Client Ref")}</th>
          %endif
          %if pick.volume:
            <th style="white-space:nowrap">${_("Volume")}</th>
          %endif
          %if 'number_of_packages_computed' in pick._columns and pick.number_of_packages_computed and pick.number_of_packages_computed != 0:
             <th style="white-space:nowrap">${_("N° Packages")}</th>
          %endif
          %if pick.weight:
             <th style="white-space:nowrap">${_("Weight")}</th>
          %endif
          %if pick.backorder_id:
             <th style="white-space:nowrap">${_("Back Order")}</th>
          %endif
          %if pick.sale_id and pick.sale_id.incoterm:
             <th style="white-space:nowrap">${_("Incoterm")}</th>
          %endif
          %if 'consignment_note' in pick._columns and pick.consignment_note:
             <th style="white-space:nowrap">${_("CMR")}</th>
          %endif

        </tr>
        </thead>
        <tr>
            %if pick.origin and pick.origin not in [ pick.sale_id.name]  :
            <td>
               ${pick.origin}
            </td>
            %endif
             <td>
            %if pick.max_date:
               ${pick.max_date and pick.max_date[:10] or ''}</td>
            %endif
            %if pick.carrier_id:
             <td>
               ${pick.carrier_id.name }
             </td>
           %endif
            %if pick.carrier_tracking_ref:
             <td>
               ${pick.carrier_tracking_ref}
             </td>
           %endif
           %if pick.sale_id :
             <td>${pick.sale_id.name or ''}</td>
           %endif
          %if pick.sale_id and pick.sale_id.client_order_ref :
            <td style="white-space:nowrap">${pick.sale_id.client_order_ref}</td>
          %endif
          %if pick.volume:
            <td style="white-space:nowrap;text-align:right;">${pick.volume}</td>
          %endif
          %if 'number_of_packages_computed' in pick._columns and pick.number_of_packages_computed and pick.number_of_packages_computed != 0:
             <td style="white-space:nowrap;text-align:right;">${pick.number_of_packages_computed}</td>
          %endif
          %if pick.weight:
             <td style="white-space:nowrap;text-align:right;">${pick.weight}</td>
          %endif
          %if pick.backorder_id:
             <td style="white-space:nowrap">${pick.backorder_id.name}</td>
          %endif
          %if pick.sale_id and pick.sale_id.incoterm:
             <td style="white-space:nowrap">${pick.sale_id.incoterm.name}</td>
          %endif
          %if 'consignment_note' in pick._columns and pick.consignment_note:
             <td style="white-space:nowrap">${pick.consignment_note}</td>
          %endif
    </table>
    <h1> </h1>
    <table style="width:100%">
    <thead style="border:1px solid #E3E3E3">
          <tr>
%if pick.print_code:
            <th>${_("Code")}</th>
            <th>${_("Description")}</th>
%else:
            <th>${_("Description")}</th>
%endif
%if pick.print_uom:
            <th style="text-align:center;">${_("Quantity")}</th><th class style="text-align:left;">${_("UoM")}</th>
%endif
%if pick.print_uos:
            <th style="text-align:center;white-space:nowrap">${_("UoS Qty")}</th><th style="text-align:left;white-space:nowrap;">${_("UoS")}</th>
%endif
%if pick.print_ean:
            <th style="text-align:center;">${_("EAN")}</th>
%endif
%if pick.print_lot:
            <th style="text-align:center;">${_("Lot")}</th>
%endif
%if pick.print_packing:
            <th style="text-align:center;">${_("Pack")}</th>
            <th style="text-align:center;">${_("Packaging")}</th>
%endif
            <th style="text-align:center;">${_("Source Location")}</th>
            <th style="text-align:center;">${_("Destination Location")}</th>
         </tr>
        </thead>
        %for line in pick.move_lines_sorted :
        <tbody>
        <tr>
%if pick.print_code:
           <td>${line.product_id.default_code or ''|entity}</td>
           <td>${line.product_id.name|entity}
        %if line.note :
        <br>
        ${line.note |carriage_returns}
        %endif
        </td>
%else:
           <td>${line.name|entity}
        %if line.note :
        <br>
        ${line.note |carriage_returns}
        %endif
        </td>
%endif
%if pick.print_uom:
           <td style="white-space:nowrap;text-align:right;">${str(line.product_qty).replace(',000','') or '0'}</td>
           <td style="white-space:nowrap;text-align:left;">${line.product_uom.name or ''}</td>
%endif
%if pick.print_uos:
           <td style="white-space:nowrap;text-align:right;">${str(line.product_uos_qty).replace(',000','') or '0'}</td>
           <td style="white-space:nowrap;text-align:left;">${line.product_uos.name or ''}</td>
%endif
%if pick.print_ean:
           <td style="white-space:nowrap;text-align:left;">${line.product_packaging.ean or line.product_id.ean13 or ''}</td>
%endif
%if pick.print_lot:
           <td style="white-space:normal;text-align:left;">${line.prodlot_id.prefix or ''}${line.prodlot_id.prefix and '-' or ''}${line.prodlot_id.name or '' }</td>
%endif
%if pick.print_packing:
           <td style="white-space:normal;text-align:left;">${line.product_packaging.qty and line.product_qty/line.product_packaging.qty or ''}</td>
           <td style="white-space:normal;text-align:left;">${line.product_packaging and line.product_packaging.ul.name or ''} ${line.product_packaging and _(" / " or '')} ${line.product_packaging and line.product_packaging.qty or ''} ${line.product_packaging and line.product_id.uom_id.name or ''}</td>
%endif
           <td style="white-space:nowrap;text-align:left;">${line.location_id.name or ''}</td>
           <td style="white-space:nowrap;text-align:left;">${line.location_dest_id.name or ''}</td>
        </tr>
        %endfor
        </tbody>
    </table>
<br/>
<table style="text-align:left; border-style:hidden; width:100%">
<tr style="border-style:hidden;">
<td style="border-style:hidden;;width:40%">
    <table style="text-align:right;border:1px solid lightgrey">
%if 'sample' in pick._columns and pick.sample:
<tr><td style="text-align:left;"> ${_("Sample")}</td><td>  ${pick.sample}</td></tr>
%endif
%if 'seal' in pick._columns and pick.seal:
<tr><td style="text-align:left;"> ${_("Seal")}</td><td>  ${pick.seal}</td></tr>
%endif
%if 'number_weighing' in pick._columns and pick.number_weighing:
<tr><td style="text-align:left;"> ${_("Number Weighing")}</td><td>  ${pick.number_weighing}</td></tr>
%endif
<!-- empty char string is 5 char long-->
%if 'date_weighing' in pick._columns and len(pick.date_weighing)>5  :  
    <tr><td style="text-align:left;">${_("Date Weighing")}</td><td>  ${pick.date_weighing} </td></tr>
%endif
    </table>

%if 'tractor_gross' in pick._columns and (pick.tractor_gross or pick.tractor_number or date_weighing or total_net):
<br>
    <table style="text-align:right;border:1px solid lightgrey">
        <tr style="text-align:right;border:1px solid lightgrey;">
            <th/> 
            <th>${_("Tractor")}</th>  
            <th>${_("Trailer")}</th> 
            <th>${_("Total")}</th> 
        </tr>
        <tr>
            <td style="text-align:left;">${_("License Plate")}</td>
            <td>${ pick.tractor_number or ''}</td>
            <td>${ pick.trailer_number or ''}</td>
            <td/>
        </tr>
        <tr>
            <td style="text-align:left;">${_("Net")}</td>
            <td>${ formatLang(pick.tractor_net or '')}</td>
            <td>${ formatLang(pick.trailer_net or '')}</td>
            <td>${ formatLang(pick.total_net or '')}</td>
        </tr>
%if 'print_net_only' in pick._columns and not pick.print_net_only:
        <tr>
            <td style="text-align:left;">${_("Tare")}</td>
            <td >${ formatLang(pick.tractor_tare or '')}</td>
            <td i>${ formatLang(pick.trailer_tare or '') }</td>
            <td/>
        </tr>
        <tr>
            <td style="text-align:left;">${_("Gross")}</td>
            <td >${ formatLang(pick.tractor_gross or '')}</td>
            <td >${ formatLang(pick.trailer_gross or '') }</td>
            <td>${ formatLang(pick.total_gross or '')}</td>
        </tr>
%endif
    </table>
%endif       
</td>
<td stype="border-style:hidden;">
%if pick.note and 'note_print' not in pick._columns:
    <br>
    ${pick.note|carriage_returns}
    <br>
    %endif
    %if 'note_print' in pick._columns and pick.note_print:
        <br>
        ${pick.note_print|carriage_returns}
        <br>
        %endif
        <br>
        </td>
        
</tr>
</table>

    <p style="page-break-after:always"></p>
    %endfor 
</body>
</html>
