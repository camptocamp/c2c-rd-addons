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
    </style>
%for top in objects:

<table>
<h1>Info Folder</h1>
    <tbody>
        <tr>
        <td>Object</td>
        <td>${top.location_id.name or ''|entity}</td>
        <td rowspan=20>${helper.embed_image('png',top.location_id.image, width=250)}<br>${helper.embed_image('png',top.location_id.blueprint, width=250)}</td>
        </tr> 

        <tr>
        <td>Top</td>
        <td>${top.name or ''|entity}</td>
        </tr>

        <tr>
        <td>Owner</td>
        <td>${top.partner_id.name or ''|entity}</td>
        </tr>

        %if top.staircase or top.flor:
        <tr>
        <td>Staircase / Floor</td>
        <td>${top.staircase or ''|entity} / ${top.floor or ''|entity}</td>
        </tr>
        %endif

        %if top.surface:
        <tr>
        <td>Surface</td>
        <td>${top.surface or ''|entity}m²</td>
        </tr>    
        %endif

        <tr>
        <td>Monthly Rent Net</td>
        <td>${round((top.surface or 0 ) * (top.lease_target or 0),0) or ''|entity} €</td>
        </tr>
        <tr>

        <td>Monthly Operating Cost Net</td>
        <td>${round(top.operating_cost ,0) or ''|entity} €</td>
        </tr>

        %if top.usage:
        <tr>
        <td>Usage</td>
        <td>${top.usage or ''|entity}</td>
        </tr>
        %endif

        %if top.category:
        <tr>
        <td>Category</td>
        <td>${top.category or ''|entity}</td>
        </tr>t
        %endif

        %if top.rooms:
        <tr>
        <td>Rooms</td>
        <td>${top.rooms or ''|entity}</td>
        </tr>
        %endif

        %if top.constructed:
        <tr>
        <td>Construction Year</td>
        <td>${str(top.constructed).replace(',','') or ''|entity}</td>
        </tr>
        %endif

        %if top.old_building:
        <tr>
        <td>Old Building</td>
        <td>${top.old_building or ''|entity}</td>
        </tr>
        %endif

        %if top.lift:
        <tr>
        <td>Elevator</td>
        <td>${top.lift or ''|entity}</td>
        </tr>
        %endif

        %if top.handicap:
        <tr>
        <td>Handicap Accessible</td>
        <td>${top.handicap or ''|entity}</td>
        </tr>
        %endif

        %if top.heating:
        <tr>
        <td>Heating</td>
        <td>${top.heating or ''|entity}</td>
        </tr>
        %endif

        %if top.heating_source:
        <tr>
        <td>Heating Source</td>
        <td>${top.heating_source or ''|entity}</td>
        </tr>
        %endif

        %if top.telephon:
        <tr>
        <td>Telefon</td>
        <td>${top.telephon or ''|entity}</td>
        </tr>
        %endif

        %if top.internet:
        <tr>
        <td>Internet</td>
        <td>${top.internet or ''|entity}</td>
        </tr>
        %endif

        %if top.tv_cable:
        <tr>
        <td>Kabel TV</td>
        <td>${top.tv_cable or ''|entity}</td>
        </tr>
        %endif

        %if top.tv_sat:
        <tr>
        <td>Sat TV</td>
        <td>${top.tv_sat or ''|entity}</td>
        </tr>
        %endif

        %if top.alarm:
        <tr>
        <td>Alarm</td>
        <td>${top.alarm or ''|entity}</td>
        </tr>
        %endif

        %if top.note_sales:
        <tr>
        <td COLSPAN=2>${top.note_sales or ''|entity}</td>
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
    <table>
</body>
%endfor
</html>