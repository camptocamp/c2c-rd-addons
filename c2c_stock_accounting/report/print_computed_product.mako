<html>
%if context['data'] and context['data'].get('form'):
  <%form = True%>
%else:
  <%form = False%>
%endif

%if form  and context['data']['form']['display_with_zero_qty'] ==1:
  <%all_zero = True%>
%else:
  <%all_zero = False%>
%endif



<head>
    <style type="text/css">
        ${css}
        pre {font-family:helvetica; font-size:12;}
    </style>
<h1>${_("Product List")}</h1>
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
     pre {font-family:helvetica; font-size:15;}
    </style>
    
<table>

        <thead>
          <tr>
            <th style="text-align:left;white-space:nowrap">${_("Category")}</th>
            <th style="text-align:left;white-space:nowrap">${_("Produkt")}</th>
            <th style="text-align:right;white-space:nowrap">${_("Qty")}</th>
            <th style="text-align:left;white-space:nowrap">${_("UoM")}</th>
            <th style="text-align:right">${_("Valuation")}</th>
            <th style="text-align:right">${_("Valuation Comp")}</th>
            <th style="text-align:right">${_("Valuation Diff")}</th>
            <th style="text-align:left;white-space:nowrap">${_("Code")}</th>
            <th style="text-align:left;white-space:nowrap">${_("Account")}</th>
            <th style="text-align:left;white-space:nowrap">${_("Code")}</th>
            <th style="text-align:left;">${_("Account Expense")}</th>
         </tr>
        </thead>
%for prod in objects :
        <tbody>
%if (all_zero or prod.qty_available !=0  or prod.valuation !=0 or prod.valuation2 !=0 ):
          <tr>
            <td style="text-align:left;white-space:nowrap">${prod.categ_id.name or ''}</td>
            <td>${prod.name}</td>
            <td style="text-align:right">${prod.qty_available}</td>
            <td>${prod.uom_id.name or ''}</td>
            <td style="text-align:right">${prod.valuation}</td>
            <td style="text-align:right">${prod.valuation2}</td>
            <td style="text-align:right">${prod.valuation_diff}</td>
            <td style="text-align:right">${prod.stock_account_id.code}</td>
            <td>${prod.stock_account_id.name}</td>
            <td style="text-align:right">${prod.expense_account_id.code}</td>
            <td>${prod.expense_account_id.name}</td>
         </tr>
%endif
        </tbody>
%endfor
</table>

</body>

</html>
