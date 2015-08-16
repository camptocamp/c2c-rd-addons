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
    td { margin: 0px; padding: 3px; border: 1px solid lightgrey;  vertical-align: top; }
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
            <th style="text-align:right;white-space:normal">${voucher.balance_start}</th>
        </tr>
        <tr>
        <th style="text-align:left;white-space:nowrap">${_("Text")}</th>
        <th style="text-align:left;white-space:nowrap">${_("Date")}</th>
        
        <th style="text-align:left;white-space:nowrap">${_("Partner Account")}</th>
        <th style="text-align:left;white-space:nowrap">${_("Tax")}</th>
        <th style="text-align:left;white-space:nowrap">${_("Tax Amount")}</th>

        </tr>
        </thead>
        %for line in voucher.line_ids_sorted:
            <tbody>
            <tr>
            <td style="text-align:left;white-space:nowrap">${line.name or ''}</td>
            <td style="white-space:nowrap">${line.date}</td>
            <td>${line.partner_id.name or line.account_id.name}</td>
            <td style="white-space:nowrap">${'tax_id' in line._columns and line.tax_id.name or ''}</td>
            <td style="text-align:right;white-space:nowrap">${line.amount_tax or ''}</td>
            <td style="text-align:right;white-space:nowrap">${line.amount}</td>
            </tr>
            </tbody>
            %endfor
            <tfoot>
            <tr>
            <th colspan="4"> </th>
            <th style="text-align:right">${_("Ending Balance")}</th>
            <th style="text-align:right;white-space:nowrap">${voucher.balance_end_real}</th>
            </tr>
            </tfoot>
            </table>
            
            %endfor
            
            
            </body>
            
            </html>
            
