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
    font-size:12px;
    }
    tr { page-break-inside : avoid; vertical-align: top;}
    td { margin: 0px; padding: 3px; border: 1px solid lightgrey; vertical-align: top; }
    pre {font-family:helvetica; font-size:15;}
    </style>
    
    %for voucher in objects :
        
        <h1>
        ${voucher.name} ${voucher.date}   ${_(voucher.state)}
        </h1>
        
        
        <table>
        <thead>
        <tr>
            <th colspan="4"> </th>
            <th style="text-align:right">${_("Starting Balance")}</th>
        </tr>
        <tr>
        <th style="text-align:left;white-space:nowrap">${_("Text")}</th>
        <th style="text-align:left;white-space:nowrap">${_("Date")}</th>
        
        <th style="text-align:left;white-space:nowrap">${_("Partner Account")}</th>
        <th style="text-align:left;white-space:nowrap">${_("Tax")}</th>
        <th style="text-align:right;white-space:normal">${formatLang(voucher.balance_start)}</th>
        </tr>
        </thead>
        <%
        running_tot = 0
         %>
        %for line in voucher.line_ids_sorted:
            <tbody>
            <tr>
            <td style="text-align:left;white-space:nowrap">${line.name or ''}</td>
            <td style="white-space:nowrap">${line.date}</td>
            <td>${line.partner_id.name or (line.account_id.code +' '+ line.account_id.name )}</td>

            %if 'tax_id' in line._columns: 
               <td>${line.tax_id.name or ''}</td>
            %else:
               <td/>
            %endif
            <td style="text-align:right;white-space:nowrap">${line.amount}</td>
            <%
             running_tot += line.amount
             %>
            </tr>
            </tbody>
            %endfor
            <tfoot>
            <tr>
            <th colspan="3"> </th>
            <th style="text-align:right">${_("Ending Balance")}</th>
            <th style="text-align:right;white-space:nowrap">${formatLang(voucher.balance_end_real)}</th>
            </tr>
            %if running_tot != balance_end_real:
            <th colspan="3"> </th>
            <th style="text-align:right">${_("Computed Balance")}</th>
            <th style="text-align:right;white-space:nowrap">${formatLang(running_tot)}</th>
            %endif
            </tfoot>
            </table>
            
            %endfor
            
            
            </body>
            
            </html>

