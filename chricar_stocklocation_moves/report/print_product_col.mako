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
      
      cumul_categ_qty_begin = 0.0
      cumul_categ_qty_plus = 0.0
      cumul_categ_qty_minus = 0.0
      cumul_categ_qty_inventory = 0.0
      cumul_categ_qty_end = 0.0
      cumul_categ_value_begin = 0.0
      cumul_categ_value_plus = 0.0
      cumul_categ_value_minus = 0.0
      cumul_categ_value_inventory = 0.0
      cumul_categ_value_end = 0.0
      cumul_categ_lines = 0.0
      
      cumul_tot_qty_begin = 0.0
      cumul_tot_qty_plus = 0.0
      cumul_tot_qty_minus = 0.0
      cumul_tot_qty_inventory = 0.0
      cumul_tot_qty_end = 0.0
      cumul_tot_value_begin = 0.0
      cumul_tot_value_plus = 0.0
      cumul_tot_value_minus = 0.0
      cumul_tot_value_inventory = 0.0
      cumul_tot_value_end = 0.0
      
      products = context['products']

 
 %>


<head>
    <style type="text/css">
        ${css}
        pre {font-family:helvetica; font-size:12;}
    </style>
<h1>${_("Product Columns")}</h1>
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
            <th style="text-align:left;white-space:nowrap">${_("UoM")}</th>
            <th style="text-align:right">${_("Qty Begin")}</th>
            <th style="text-align:right">${_("Qty Plus")}</th>
            <th style="text-align:right">${_("Qty Minus")}</th>
            <th style="text-align:right">${_("Qty Inventory")}</th>
            <th style="text-align:right">${_("Qty End")}</th>
            <th style="text-align:right">${_("Value Begin")}</th>
            <th style="text-align:right">${_("Value Plus")}</th>
            <th style="text-align:right">${_("Value Minus")}</th>
            <th style="text-align:right">${_("Value Inventory")}</th>
            <th style="text-align:right">${_("Vlaue End")}</th>
         </tr>
        </thead>
<%
sorted_objects = sorted(objects, key=lambda o : o.categ_id.name + o.name) 
%>
%for prod in sorted_objects :
        <tbody>

%if categ and categ != prod.categ_id.name and cumul_categ_lines > 0:
          <tr>
            <th style="text-align:left;white-space:nowrap">${categ} ${_("TOTAL")}</th>
            <th style="text-align:left;white-space:nowrap"></th>
            <th style="text-align:right;white-space:nowrap">${  formatLang(cumul_categ_qty_begin)}</th>
            <th style="text-align:right;white-space:nowrap">${  formatLang(cumul_categ_qty_plus)}</th>
            <th style="text-align:right;white-space:nowrap">${  formatLang(cumul_categ_qty_minus)}</th>
            <th style="text-align:right;white-space:nowrap;">${  formatLang(cumul_categ_qty_inventory)}</th>
            <th style="text-align:right;white-space:nowrap;">${  formatLang(cumul_categ_qty_end)}</th>
            <th style="text-align:right;white-space:nowrap">${  formatLang(cumul_categ_value_begin)}</th>
            <th style="text-align:right;white-space:nowrap">${  formatLang(cumul_categ_value_plus)}</th>
            <th style="text-align:right;white-space:nowrap">${  formatLang(cumul_categ_value_minus)}</th>
            <th style="text-align:right;white-space:nowrap;">${  formatLang(cumul_categ_value_inventory)}</th>
            <th style="text-align:right;white-space:nowrap;">${  formatLang(cumul_categ_value_end)}</th>
         </tr>
         <tr>
            <th style="text-align:right;white-space:nowrap"></th>
            <th style="text-align:right;white-space:nowrap"></th>
            <th style="text-align:right;white-space:nowrap"></th>
            <th style="text-align:right;white-space:nowrap"></th>
            <th style="text-align:right;white-space:nowrap"></th>
         </tr>
<%
      cumul_categ_qty_begin = 0.0
      cumul_categ_qty_plus = 0.0
      cumul_categ_qty_minus = 0.0
      cumul_categ_qty_inventory = 0.0
      cumul_categ_qty_end = 0.0
      cumul_categ_value_begin = 0.0
      cumul_categ_value_plus = 0.0
      cumul_categ_value_minus = 0.0
      cumul_categ_value_inventory = 0.0
      cumul_categ_value_end = 0.0
      cumul_categ_lines = 0
%>    
%endif

<% 
    if products.get(str(prod.id),False):
        qty_begin = products[str(prod.id)]['qty_begin'] 
        qty_plus = products[str(prod.id)]['qty_plus'] 
        qty_minus = products[str(prod.id)]['qty_minus'] 
        qty_inventory = products[str(prod.id)]['qty_inventory'] 
        qty_end = products[str(prod.id)]['qty_end'] 
        value_begin = products[str(prod.id)]['value_begin'] 
        value_plus = products[str(prod.id)]['value_plus'] 
        value_minus = products[str(prod.id)]['value_minus'] 
        value_inventory = products[str(prod.id)]['value_inventory'] 
        value_end = products[str(prod.id)]['value_end'] 
    else:
        qty_begin = 0
        qty_plus = 0
        qty_minus = 0
        qty_inventory = 0
        qty_end = 0
        value_begin = 0
        value_plus = 0
        value_minus = 0
        value_inventory = 0
        value_end = 0
%>

%if (all_zero or qty_begin !=0 or qty_plus !=0 or qty_minus !=0 or qty_inventory !=0 or qty_end !=0 or value_begin !=0 or value_plus !=0 or value_minus !=0 or value_inventory !=0 or value_end !=0 ):
      <tr>
          
            <td>${prod.name}</td>
            <td>${prod.uom_id.name or ''}</td>
            <td style="text-align:right;white-space:nowrap;">${formatLang(qty_begin)}</td>
            <td style="text-align:right;white-space:nowrap;">${formatLang(qty_plus)}</td>
            <td style="text-align:right;white-space:nowrap;">${formatLang(qty_minus)}</td>
            <td style="text-align:right;white-space:nowrap;">${formatLang(qty_inventory)}</td>
            <td style="text-align:right;white-space:nowrap;">${formatLang(qty_end)}</td>
            <td style="text-align:right;white-space:nowrap;">${formatLang(value_begin)}</td>
            <td style="text-align:right;white-space:nowrap;">${formatLang(value_plus)}</td>
            <td style="text-align:right;white-space:nowrap;">${formatLang(value_minus)}</td>
            <td style="text-align:right;white-space:nowrap;">${formatLang(value_inventory)}</td>
            <td style="text-align:right;white-space:nowrap;">${formatLang(value_end)}</td>
            
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
    
    cumul_categ_qty_begin += qty_begin 
    cumul_categ_qty_plus += qty_plus
    cumul_categ_qty_minus += qty_minus
    cumul_categ_qty_inventory += qty_inventory
    cumul_categ_qty_end += qty_end

    cumul_categ_value_begin += value_begin
    cumul_categ_value_plus  += value_plus
    cumul_categ_value_minus += value_minus
    cumul_categ_value_inventory += value_inventory
    cumul_categ_value_end += value_end
    cumul_categ_lines += 1
    
    cumul_tot_qty_begin += qty_begin 
    cumul_tot_qty_plus += qty_plus
    cumul_tot_qty_minus += qty_minus
    cumul_tot_qty_inventory += qty_inventory
    cumul_tot_qty_end += qty_end

    cumul_tot_value_begin += value_begin
    cumul_tot_value_plus  += value_plus
    cumul_tot_value_minus += value_minus
    cumul_tot_value_inventory += value_inventory
    cumul_tot_value_end += value_end
 %>
    </tr>
%endif
        </tbody>
%endfor
        <tfoot>
%if cumul_categ_lines >0:
            <tr>
            <th style="text-align:left;white-space:nowrap">${categ} ${_("TOTAL")}</th>
            <th style="text-align:right;white-space:nowrap"></th>
            <th style="text-align:right;white-space:nowrap">${  formatLang(cumul_categ_qty_begin)}</th>
            <th style="text-align:right;white-space:nowrap">${  formatLang(cumul_categ_qty_plus)}</th>
            <th style="text-align:right;white-space:nowrap">${  formatLang(cumul_categ_qty_minus)}</th>
            <th style="text-align:right;white-space:nowrap;">${  formatLang(cumul_categ_qty_inventory)}</th>
            <th style="text-align:right;white-space:nowrap;">${  formatLang(cumul_categ_qty_end)}</th>
            <th style="text-align:right;white-space:nowrap">${  formatLang(cumul_categ_value_begin)}</th>
            <th style="text-align:right;white-space:nowrap">${  formatLang(cumul_categ_value_plus)}</th>
            <th style="text-align:right;white-space:nowrap">${  formatLang(cumul_categ_value_minus)}</th>
            <th style="text-align:right;white-space:nowrap;">${  formatLang(cumul_categ_value_inventory)}</th>
            <th style="text-align:right;white-space:nowrap;">${  formatLang(cumul_categ_value_end)}</th>

         </tr>
%endif
         <tr>
            <th style="text-align:right;white-space:nowrap"></th>
            <th style="text-align:right;white-space:nowrap"></th>
            <th style="text-align:right;white-space:nowrap"></th>
            <th style="text-align:right;white-space:nowrap"></th>
            <th style="text-align:right;white-space:nowrap"></th>
         </tr>

          <tr>
            <th style="text-align:left;white-space:nowrap">${_("GRAND TOTAL")}</th>
            <th style="text-align:right;white-space:nowrap"></th>
            <th style="text-align:right;white-space:nowrap">${  formatLang(cumul_tot_qty_begin)}</th>
            <th style="text-align:right;white-space:nowrap">${  formatLang(cumul_tot_qty_plus)}</th>
            <th style="text-align:right;white-space:nowrap">${  formatLang(cumul_tot_qty_minus)}</th>
            <th style="text-align:right;white-space:nowrap;">${  formatLang(cumul_tot_qty_inventory)}</th>
            <th style="text-align:right;white-space:nowrap;">${  formatLang(cumul_tot_qty_end)}</th>
            <th style="text-align:right;white-space:nowrap">${  formatLang(cumul_tot_value_begin)}</th>
            <th style="text-align:right;white-space:nowrap">${  formatLang(cumul_tot_value_plus)}</th>
            <th style="text-align:right;white-space:nowrap">${  formatLang(cumul_tot_value_minus)}</th>
            <th style="text-align:right;white-space:nowrap;">${  formatLang(cumul_tot_value_inventory)}</th>
            <th style="text-align:right;white-space:nowrap;">${  formatLang(cumul_tot_value_end)}</th>

         </tr>
        </tfoot>
</table>

</body>

</html>
