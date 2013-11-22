## -*- coding: utf-8 -*-
<html>
 
<head>
</head>
<body>
    <style  type="text/css">
     table {
       page-break-after:auto;
       border-collapse: collapse;
       cellspacing="0";
       font-size:12px;
           }
     th {margin: 0px; padding: 3px; border: 1px solid Grey;  vertical-align: loc; }
     td {margin: 0px; padding: 3px; border: 1px solid lightgrey;  vertical-align: loc; }
     pre {font-family:helvetica; font-size:12;}
    </style>


%for loc in objects:

<%
owner = []
for top in loc.top_ids:
    if top.partner_id.name not in owner:
         owner.append(top.partner_id.name)    
owners = ','.join([id for id in owner])

%>
<h1>${_("Info Real Estate")}</h1>

<table>
    <tbody>
        <tr>
        <td>${_("Object")}</td>
        <td>${loc.name or ''|entity}</td>
        </tr> 

        %if owners:
        <tr>
        <td>${_("Owner")}</td>
        <td>${owners|entity}</td>
        </tr>
        %endif

        %if 'surface' in loc._columns and loc.surface:         
        <tr>
        <td>${_("Surface")}</td>
        <td>${loc.surface or ''|entity}m²</td>
        </tr>    
        %endif

        %if 'lease_target' in loc._columns and  'surface' in loc._columns and loc.lease_target and loc.surface and loc.surface  > 0:
        <tr>
        <td>${_("Monthly Rent Net")}</td>
        <td>${formatLang(round((loc.lease_target ),0))} €
            (${formatLang(loc.lease_target / loc.surface )}€/m²) 
        </td>
        </tr>
        %endif

        %if 'operating_cost' in loc._columns and 'surface' in loc._columns  and loc.operating_cost:
        <tr>
        <td>${_("Monthly Operating Cost Net")}</td>
        <td>${formatLang(round(loc.operating_cost ,0)) or '' | entity} €  
          %if loc.surface and loc.surface  > 0:
            (${formatLang((loc.operating_cost or 0 ) / loc.surface )}€/m²)
          %endif
        </td>
        </tr>
        %endif

        %if ('assessed_value' in loc._columns or 'assessed_date' in loc._columns)  and  (loc.assessed_value or loc.assessed_date):
        <tr>
        <td>${_("Asessed Value")}</td>
        <td>${formatLang(round(loc.assessed_value,0)) or '' | entity}</td>
        </tr>
        <tr>
        <td>${_("Asessed Value Increased")}</td>
        <td>${formatLang(round(loc.assessed_value_increased,0)) or '' | entity}</td>
        </tr>
        <tr>
        <td>${_("Asessed Date")}</td>
        <td>${loc.assessed_date or '' | entity}</td>
        </tr>
        %endif
        %if ('assessed_value_increased' in loc._columns and loc.assessed_value_increased):
        <tr>
        <td>${_("Property Tax")}</td>
        <td>${loc.assessed_value_increased * 0.01 or '' | entity}</td>
        </tr>
        %endif
 

      %if ('rent_actual' in loc._columns and loc.rent_actual) or ('rent_plan' in loc._columns and loc.rent_plan):
      <table>
        <thead>
      <br/>
        <tr>
        <td/>
        <td/>
        <td style="text-align:right;">${_("Actual")}</td>
        <td style="text-align:right;">${_("Plan")}</td>
        </tr>    
         </thead>
         <tbody>
        <tr>
        <td>${_("Lease")}</td>
        <td/>
        <td style="text-align:right;">${loc.rent_actual or ''|entity}</td>
        <td style="text-align:right;">${loc.rent_plan or ''|entity}</td>
        </tr>    
        <tr>
        <td>${_("Lease/m²")}</td>
        <td/>
        <td style="text-align:right;">${formatLang(loc.rent_actual_surface,2) or ''|entity}</td>
        <td style="text-align:right;">${formatLang(loc.rent_plan_surface,2) or ''|entity}</td>
        </tr>    
        %if ('discount' in loc._columns and loc.discount) or ( 'discount_value_actual' in loc._columns and loc.discount_value_actual) or ( 'discount_value_plan' in loc._columns and loc.discount_value_plan):         
        <tr>
        <td>${_("Rate / Valuation")}</td>
        <td>${loc.discount or ''|entity}%</td>
        <td style="text-align:right;">${loc.discount_value_actual or ''|entity}</td>
        <td style="text-align:right;">${loc.discount_value_plan or ''|entity}</td>
        </tr>
        %if loc.surface > 0:
        <tr>
        <td>${_("Price / m²")}</td>
        <td/>
        <td style="text-align:right;">${formatLang(loc.discount_value_actual/loc.surface) or ''|entity}</td>
        <td style="text-align:right;">${formatLang(loc.discount_value_plan/loc.surface) or ''|entity}</td>
        </tr>
        %endif
        %endif
         <tbody>
       </table>
        %endif

      </tbody>
    </table>
<br/>

${_("Tax Results")}
<%
val = loc.tax_res[2]

pl = ''
sums = {}
sums['Result'] = {}
for fy1 in loc.tax_res[1] :
    sums['Result'][fy1[0]] = 0
%> 
     
     <table>
        
       <thead>
         <tr>
         <th>${_("Code")[:4]}</th>
         <th>${_("Account")}</th>
         %for fy in loc.tax_res[1] :
         <th> ${fy[0]} </th>
         %endfor
         </tr>
         %for ac in loc.tax_res[0]:
          %if pl and pl != ac[3]:
              <tr>
                <td/><td> ${pl} </td> 
                 %for fy1 in loc.tax_res[1] :
                    <td style="text-align:right;"> ${formatLang(sums[pl][fy1[0]],0)} </td>
                 %endfor
              </tr>
          %endif
           <%
              pl = ac[3]
              if not sums.get(pl) :
                  sums[pl] = {}
                  for fy1 in loc.tax_res[1]:
                      sums[pl][fy1[0]] = 0
            %>
         <tr>
          <td> ${ac[0]} </td> 
          <td> ${ac[1]} </td> 
          %for fy1 in loc.tax_res[1] :
            <td style="text-align:right;"> ${formatLang(val[ac[0]][fy1[0]] or 0, 0)} </td>
            <%
            sums[pl][fy1[0]] += val[ac[0]][fy1[0]] or 0
            sums['Result'][fy1[0]] += val[ac[0]][fy1[0]] or 0
            %>
          %endfor
             
         </tr>
         %endfor
              <tr>
                <td/><td> ${pl} </td>  
                 %for fy1 in loc.tax_res[1] :
                    <td style="text-align:right;"> ${formatLang(sums[pl][fy1[0]],0)} </td>
                 %endfor
              </tr>
              <tr style="font-weight:bold">
                <td/><td> ${_("Result")} </td>  
                 %for fy1 in loc.tax_res[1] :
                    <td style="text-align:right;"> ${formatLang(sums['Result'][fy1[0]],0)} </td>
                 %endfor

              </tr>
          
       </thead>

     </table>
 
<p style="page-break-after:always"></p>
%endfor
</body>

</html>
