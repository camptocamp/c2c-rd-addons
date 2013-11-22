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
     td {margin: 0px; padding: 3px; border: 1px solid lightgrey;  vertical-align: top; }
     pre {font-family:helvetica; font-size:12;}
    </style>
%for top in objects:
<%setLang(top.partner_id.lang)%>
<h1>${_("Info Folders")}</h1>

<table>
    <tbody>
        <tr>
        <td>${_("Object")}</td>
        <td>${top.location_id.name or ''|entity}</td>
        <td rowspan=20>${helper.embed_image('png',top.location_id.image, width=250)}<br>${helper.embed_image('png',top.location_id.blueprint, width=250)}</td>
        </tr> 

        <tr>
        <td>${_("Top")}</td>
        <td>${top.name or ''|entity}</td>
        </tr>

        <tr>
        <td>${_("Owner")}</td>
        <td>${top.partner_id.name or ''|entity}</td>
        </tr>

        %if top.staircase or top.flor:
        <tr>
        <td>${_("Staircase / Floor")}</td>
        <td>${top.staircase or '-'|entity} / ${top.floor or '-'|entity}</td>
        </tr>
        %endif

        %if top.surface:
        <tr>
        <td>${_("Surface")}</td>
        <td>${top.surface or ''|entity}m²</td>
        </tr>    
        %endif

        %if top.lease_target and top.surface:
        <tr>
        <td>${_("Monthly Rent Net")}</td>
        <td>${formatLang(round((top.surface * top.lease_target ),0))} €
            (${formatLang(top.lease_target or 0)}€/m²) 
        </td>
        </tr>
        %endif

        %if top.operating_cost:
        <tr>
        <td>${_("Monthly Operating Cost Net")}</td>
        <td>${formatLang(round(top.operating_cost ,0)) or '' | entity} €  
          %if top.surface and top.surface <> 0:
            (${formatLang((top.operating_cost or 0 ) / top.surface )}€/m²)
          %endif
        </td>
        </tr>
        %endif

        %if top.usage:
        <tr>
        <td>${_("Usage")}</td>
        <td>${top.usage or ''|entity}</td>
        </tr>
        %endif

        %if top.category:
        <tr>
        <td>${_("Category")}</td>
        <td>${top.category or ''|entity}</td>
        </tr>
        %endif

        %if top.rooms:
        <tr>
        <td>${_("Rooms")}</td>
        <td>${top.rooms or ''|entity}</td>
        </tr>
        %endif

        %if top.constructed:
        <tr>
        <td>${_("Construction Year")}</td>
        <td>${str(top.constructed).replace(',','') or ''|entity}</td>
        </tr>
        %endif

        %if top.old_building:
        <tr>
        <td>${_("Old Building")}</td>
        <td>${top.old_building or ''|entity}</td>
        </tr>
        %endif

        %if top.lift:
        <tr>
        <td>${_("Elevator")}</td>
        <td>${top.lift or ''|entity}</td>
        </tr>
        %endif

        %if top.handicap:
        <tr>
        <td>${_("Handicap Accessible")}</td>
        <td>${top.handicap or ''|entity}</td>
        </tr>
        %endif

        %if top.heating:
        <tr>
        <td>${_("Heating")}</td>
        <td>${top.heating or ''|entity}</td>
        </tr>
        %endif

        %if top.heating_source:
        <tr>
        <td>${_("Heating Source")}</td>
        <td>${top.heating_source or ''|entity}</td>
        </tr>
        %endif

        %if top.telephon:
        <tr>
        <td>${_("Telephon")}</td>
        <td>${top.telephon or ''|entity}</td>
        </tr>
        %endif

        %if top.internet:
        <tr>
        <td>${_("Internet")}</td>
        <td>${top.internet or ''|entity}</td>
        </tr>
        %endif

        %if top.tv_cable:
        <tr>
        <td>${_("Kabel TV")}</td>
        <td>${top.tv_cable or ''|entity}</td>
        </tr>
        %endif

        %if top.tv_sat:
        <tr>
        <td>${_("Sat TV")}</td>
        <td>${top.tv_sat or ''|entity}</td>
        </tr>
        %endif

        %if top.alarm:
        <tr>
        <td>${_("Alarm")}</td>
        <td>${top.alarm or ''|entity}</td>
        </tr>
        %endif

        %if top.note_sales:
        <tr>
        <td COLSPAN=2><pre><b>${_("Remarks:")}</b>
${top.note_sales or ''|entity}</pre></td>
        </tr>
        %endif

        %if top.blueprint:
        <tr>
        <td COLSPAN=2>
          ${helper.embed_image('png',top.blueprint, width=400)}
        </dt>
        </tr>
        %endif

      </tbody>
    </table>
<p style="page-break-after:always"></p>
%endfor
</body>

</html>
