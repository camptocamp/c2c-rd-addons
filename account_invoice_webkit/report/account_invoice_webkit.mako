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
    %for inv in objects :
    <% setLang(inv.partner_id.lang) %>
<br>
<br>
<br>
<br>
    <table >
        %if inv.company_id.address_label_position == 'left':
         <tr>
         <td>
           <pre>
${inv.address_invoice_id.address_label}
           <pre>
         </td>
         <td>
         %if inv.address_invoice_id.phone :
${_("Tel")}: ${inv.address_invoice_id.phone|entity} <br>
        %endif
        %if inv.address_invoice_id.fax :
${_("Fax")}: ${inv.address_invoice_id.fax|entity} <br>
        %endif
        %if inv.address_invoice_id.email :
${_("E-mail")}: ${inv.address_invoice_id.email|entity} <br>
        %endif
        %if inv.partner_id.vat :
${_("VAT")}: ${inv.partner_id.vat|entity} <br>
        %endif
         </td>

        </tr>
        %endif

        %if inv.company_id.address_label_position == 'right' or not inv.company_id.address_label_position:
         <tr>
         <td>
         %if inv.address_invoice_id.phone :
${_("Tel")}: ${inv.address_invoice_id.phone|entity} <br>
        %endif
        %if inv.address_invoice_id.fax :
${_("Fax")}: ${inv.address_invoice_id.fax|entity} <br>
        %endif
        %if inv.address_invoice_id.email :
${_("E-mail")}: ${inv.address_invoice_id.email|entity} <br>
        %endif
        %if inv.partner_id.vat :
${_("VAT")}: ${inv.partner_id.vat|entity} <br>
        %endif
         </td>
         <td>
           <pre>
${inv.address_invoice_id.address_label}
           <pre>
         </td>
        </tr>
        %endif

    </table>
    <br />
    %if inv.type == 'out_invoice' :
    <span class="title">${_("Invoice")} ${inv.number or ''|entity}</span>
    %elif inv.type == 'in_invoice' :
    <span class="title">${_("Supplier Invoice")} ${inv.number or ''|entity}</span>   
    %elif inv.type == 'out_refund' :
    <span class="title">${_("Refund")} ${inv.number or ''|entity}</span> 
    %elif inv.type == 'in_refund' :
    <span class="title">${_("Supplier Refund")} ${inv.number or ''|entity}</span> 
    %endif
    <br/>
    <br/>
    <table class="basic_table" width="90%">
        <tr><td>${_("Document")}</td><td>${_("Invoice Date")}</td>
          %if inv.reference:
           <td>${_("Partner Ref.")}</td>
          %endif
         <td>${_("Curr")}</td></tr>
        <tr><td>${inv.name}</td><td>${formatLang(inv.date_invoice, date=True)|entity}</td>
         %if inv.reference:
         <td>${inv.reference}
         </td>
         %endif
         <td>${inv.currency_id.name}</td></tr>
    </table>
    <h1><br /></h1>
    <table class="list_table"  width="90%">
        <thead><tr><th>${_("Description")}</th><th class>${_("Taxes")}</th><th class>${_("QTY")}</th><th>${_("Unit Price")}</th>
          %if inv.amount_discount != 0:
            <th >${_("Disc.(%)")}</th>
          %endif
        <th>${_("Price")}</th></tr></thead>
        %for line in inv.invoice_line :
        <tbody>
        <tr>
           <td>${line.name|entity}</td><td>${ ', '.join([ tax.name or '' for tax in line.invoice_line_tax_id ])|entity}</td>
           <td style="text-align:right;">${line.quantity}</td>
           <td style="text-align:right;">${formatLang(line.price_unit,digits=2)}</td>
          %if inv.amount_discount != 0:
           <td style="text-align:right;">${line.discount or 0.00}</td>
          %endif
           <td style="text-align:right;">${formatLang(line.price_subtotal)}
         </td></tr>
        %if line.note :
           %if inv.amount_discount != 0:
        <tr><td colspan="6" style="border-style:none"><pre style="font-family:Helvetica;padding-left:20px;font-size:10">${line.note |entity}</pre></td></tr>
           %else:
        <tr><td colspan="5" style="border-style:none"><pre style="font-family:Helvetica;padding-left:20px;font-size:10">${line.note |entity}</pre></td></tr>
           %endif
        %endif
        %endfor
        <tr>
           %if inv.amount_discount != 0:
             <td style="border-style:none"/>
           %endif
             <td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>Net Total:</b></td><td style="border-top:2px solid;text-align:right">${formatLang(inv.amount_untaxed)}</td></tr>
        <tr> 
           %if inv.amount_discount != 0:
              <td style="border-style:none"/>
           %endif
              <td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>Taxes:</b></td><td style="text-align:right">${formatLang(inv.amount_tax)}</td></tr>
        <tr> 
          %if inv.amount_discount != 0:
             <td style="border-style:none"/>
          %endif
             <td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>Total ${inv.currency_id.name}:</b></td><td style="border-top:2px solid;text-align:right">${formatLang(inv.amount_total)}</td></tr>
        </tbody>
    </table>
<br>
       %if inv.tax_line :
    <table class="list_table" style="width:40%;">
        <tr><th>${_("Tax")}</th><th>${_("Base")}</th><th>${_("Amount")}</th></tr>
        %for t in inv.tax_line :
        <tr>
            <td>${ t.name|entity } </td>
            <td style="text-align:right;">${ t.base|entity}</td>
            <td style="text-align:right;">${ formatLang(t.amount) }</td>
        </tr>
        %endfor
        <tr>
            <td style="border-style:none"/>
            <td style="border-top:2px solid;text-align:right;"><b>${_("Total")}</b></td>
            <td style="border-top:2px solid;text-align:right;">${ formatLang(inv.amount_tax) }</td>
        </tr>
        %endif
    </table>        
    %if inv.payment_term:
    <br><b>${_("Payment Term")}</b><br>
    ${inv.payment_term.name}<br>
    %endif:
    %if inv.comment:
    <pre>${inv.comment}</pre>
    %endif:
    <p style="page-break-after:always"></p>
    %endfor
</body>
</html>
