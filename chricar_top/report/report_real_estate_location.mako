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

<h1>${_("Info Real Estate")}</h1>

<table>
    <tbody>
        <tr>
        <td>${_("Object")}</td>
        <td>${loc.name or ''|entity}</td>
        </tr> 

        <tr>
        <td>${_("Owner")}</td>
        <td>${loc.company_id.name or ''|entity}</td>
        </tr>

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

      </tbody>
    </table>
<br/>
${_("Tax Resuts")}
<%
val = loc.tax_res[2]
%> 
     
     <table>
        
       <thead>
         <tr>
         <th>${_("Code")}</th>
         <th>${_("Account")}</th>
         <th>${_("Company")}</th>
         %for fy in loc.tax_res[1] :
         <th> ${fy[0]} </th>
         %endfor
         </tr>
         %for ac in loc.tax_res[0]:
         <tr>
          <td> ${ac[0]} </td> 
          <td> ${ac[1]} </td> 
          <td> ${ac[2]} </td> 
          %for fy1 in loc.tax_res[1] :
            <td style="text-align:right;"> ${formatLang(val[ac[0]][fy1[0]] or 0, 0)} </td>
          %endfor
         </tr>
         %endfor
          
       </thead>

     </table>
 
<p style="page-break-after:always"></p>
%endfor
</body>

</html>
