<html>                
<b>Sales Folder</b>
                
  <body>
    <style  type="text/css">
     table {
       border-collapse: collapse;
       cellspacing="0";
       font-size:10px;
           }
     td {margin: 0px; padding: 3px; border: 1px solid lightgrey;  vertical-align: top; }
    </style> 

</head>

  <body>
    <style  type="text/css">
     table {
       border-collapse: collapse;
       cellspacing="0";
       font-size:12px;
           }
    </style>
<table>

 %for top in objects :
     <tbody>
        <tr>
        <td>Object</td>
        <td>${top.location_id.name or ''|entity}</td>
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
        <td>Surface m²</td>
        <td>${top.surface or ''|entity}</td>
        </tr>    
        %endif
        
        <tr>
        <td>Monthly Rent Net €</td>
        <td>${round((top.surface or '0' ) * (top.lease_target or ''),0) or ''|entity}</td>
        </tr>
        <tr>
        <td>Monthly Operating Cost Net €</td>
        <td>${round(top.operating_cost ,0) or ''|entity}</td>
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
        <td>${top.constructed or ''|entity}</td>
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
        <tr>
        <td COLSPAN=2>
          <img src=${top.blueprint} alt="Blueprint" width="400" height="400" />
        </dt>
        </tr>

        %endif
      </tbody>
 %endfor
 <table>
  </body>
</html>
