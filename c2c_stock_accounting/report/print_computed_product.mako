## -*- coding: utf-8 -*-
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


 <%
      categ = ''
      stock_account = ''
      expense_account = ''
      cumul_categ_qty = 0.0
      cumul_categ_valuation = 0.0
      cumul_categ_valuation2 = 0.0
      cumul_categ_valuation_diff = 0.0
      cumul_qty = 0.0
      cumul_valuation = 0.0
      cumul_valuation2 = 0.0
      cumul_valuation_diff = 0.0
 %>


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
     th { margin: 0px; padding: 3px; border: 0px solid lightgrey;  vertical-align: top; }
     pre {font-family:helvetica; font-size:15;}
    </style>
   
${_("Selection")}
<table>
<tr>
 <td>${_("Location")}</td>
 <td style="width:16%;">${_("From")}</td>
 <td style="width:16%;">${_("To")}</td>
 <td style="width:16%;">${_("From Compare")}</td>
 <td style="width:16%;">${_("To Compare")}</td>
</tr>
<tr>
 <td>${context['location_name'] or ''}</td>
 <td>${context['local_from_date1'] or ''}</td>
 <td>${context['local_to_date1'] or ''}</td>
 <td>${context['local_from_date2'] or ''}</td>
 <td>${context['local_to_date2'] or ''}</td>
<!--
 <td>${context['data']['form']['from_date'] or ''}</td>
 <td>${context['data']['form']['to_date'] or ''}</td>
 <td>${context['data']['form']['from_date2'] or ''}</td>
 <td>${context['data']['form']['to_date2'] or ''}</td>
-->
</tr>
</table>
<br>
<table>

        <thead>
          <tr>
            <th style="text-align:left;white-space:nowrap">${_("Product")}</th>
            <th style="text-align:right;white-space:nowrap">${_("Qty")}</th>
            <th style="text-align:left;white-space:nowrap">${_("UoM")}</th>
            <th style="text-align:right">${_("Avg Price")}</th>
            <th style="text-align:right">${_("Valuation")}</th>
            <th style="text-align:right">${_("Valuation Comp")}</th>
            <th style="text-align:right">${_("Valuation Diff")}</th>
         </tr>
        </thead>
<%
sorted_objects = sorted(objects, key=lambda o : o.categ_id.name + o.name) 
%>
%for prod in sorted_objects :
        <tbody>
%if (all_zero or prod.qty_available !=0  or prod.valuation1 !=0 or prod.valuation2 !=0 ):

%if categ and categ != prod.categ_id.name:
          <tr>
            <th style="text-align:left;white-space:nowrap">${categ} ${_("TOTAL")}</th>
            <th style="text-align:right;white-space:nowrap">${  formatLang(cumul_categ_qty)}</th>
            <th style="text-align:left;white-space:nowrap"></th>
            <th style="text-align:left;white-space:nowrap"></th>
            <th style="text-align:right;white-space:nowrap;">${  formatLang(cumul_categ_valuation)}</th>
            <th style="text-align:right;white-space:nowrap;">${  formatLang(cumul_categ_valuation2)}</th>
            <th style="text-align:left;white-space:nowrap"></th>
         </tr>
         <tr>
%if cumul_categ_valuation_diff > 0.0:
            <th style="text-align:right;white-space:nowrap">${stock_account} : ${expense_account}</th>
%else:
            <th style="text-align:right;white-space:nowrap">${expense_account} : ${stock_account}</th>
%endif
            <th style="text-align:right;white-space:nowrap"></th>
            <th style="text-align:right;white-space:nowrap"></th>
            <th style="text-align:left;white-space:nowrap"></th>
            <th style="text-align:left;white-space:nowrap"></th>
            <th style="text-align:left;white-space:nowrap"></th>
%if cumul_categ_valuation_diff < 0.0:
            <th style="text-align:right;white-space:nowrap;">${  formatLang( -cumul_categ_valuation_diff)}</th>
%else:
            <th style="text-align:right;white-space:nowrap;">${  formatLang(cumul_categ_valuation_diff)}</th>
%endif
         </tr>

 <%
      cumul_categ_qty = 0.0
      cumul_categ_valuation = 0.0
      cumul_categ_valuation2 = 0.0
      cumul_categ_valuation_diff = 0.0
 %>

%endif
          <tr>
            <td>${prod.name}</td>
            <td style="text-align:right">${prod.qty_available}</td>
            <td>${prod.uom_id.name or ''}</td>
%if prod.qty_available == 0:
            <td style="text-align:left;white-space:nowrap"></td>
%else:
            <td style="text-align:right">${  formatLang(prod.valuation1/prod.qty_available)}</td>
%endif
            <td style="text-align:right;white-space:nowrap;">${prod.valuation1}</td>
            <td style="text-align:right;white-space:nowrap;">${prod.valuation2}</td>
            <td style="text-align:right;white-space:nowrap;">${prod.valuation_diff}</td>

 <%
      categ = prod.categ_id.name
      if prod.stock_account_id and prod.stock_account_id.code and prod.stock_account_id.name:
          stock_account = prod.stock_account_id.code  + ' ' + prod.stock_account_id.name 
      else:
          stock_account = _('Undefined Stock Account')
      if prod.expense_account_id and prod.expense_account_id.code and prod.expense_account_id.name:
          expense_account = prod.expense_account_id.code + ' ' + prod.expense_account_id.name
      else:
          expense_account = _('Undefined Expense Account')
      cumul_categ_qty += prod.qty_available
      cumul_categ_valuation += prod.valuation1
      cumul_categ_valuation2 += prod.valuation2
      cumul_categ_valuation_diff += prod.valuation_diff
      cumul_qty += prod.qty_available
      cumul_valuation += prod.valuation1
      cumul_valuation2 += prod.valuation2
      cumul_valuation_diff += prod.valuation_diff
 %>
         </tr>
%endif
        </tbody>
%endfor
        <tfoot>
                  <tr>
            <th style="text-align:left;white-space:nowrap">${categ} ${_("TOTAL")}</th>
            <th style="text-align:right;white-space:nowrap">${  formatLang(cumul_categ_qty)}</th>
            <th style="text-align:left;white-space:nowrap"></th>
            <th style="text-align:left;white-space:nowrap"></th>
            <th style="text-align:right;white-space:nowrap;">${  formatLang(cumul_categ_valuation)}</th>
            <th style="text-align:right;white-space:nowrap;">${  formatLang(cumul_categ_valuation2)}</th>
            <th style="text-align:left;white-space:nowrap"></th>
         </tr>
         <tr>
%if cumul_categ_valuation_diff > 0.0:
            <th style="text-align:right;white-space:nowrap">${stock_account} : ${expense_account}</th>
%else:
            <th style="text-align:right;white-space:nowrap">${expense_account} : ${stock_account}</th>
%endif
            <th style="text-align:right;white-space:nowrap"></th>
            <th style="text-align:left;white-space:nowrap"></th>
            <th style="text-align:left;white-space:nowrap"></th>
            <th style="text-align:left;white-space:nowrap"></th>
            <th style="text-align:left;white-space:nowrap"></th>
%if cumul_categ_valuation_diff < 0.0:
            <th style="text-align:right";white-space:nowrap;>${  formatLang( -cumul_categ_valuation_diff)}</th>
%else:
            <th style="text-align:right">${  formatLang(cumul_categ_valuation_diff)}</th>
%endif
         </tr>

          <tr>
            <th style="text-align:left;white-space:nowrap">${_("GRAND TOTAL")}</th>
            <th style="text-align:right;white-space:nowrap">${ formatLang(cumul_qty)}</th>
            <th style="text-align:left;white-space:nowrap"></th>
            <th style="text-align:left;white-space:nowrap"></th>
            <th style="text-align:right;white-space:nowrap;">${ formatLang(cumul_valuation)}</th>
            <th style="text-align:right;white-space:nowrap;">${ formatLang(cumul_valuation2)}</th>
            <th style="text-align:right;white-space:nowrap;">${ formatLang(cumul_valuation_diff)}</th>
         </tr>
        </tfoot>
</table>

</body>

</html>
