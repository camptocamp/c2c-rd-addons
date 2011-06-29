<html>
<head>
                <b>Sales Folder</b> requested by ${user.name}
</head>

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



 %for top in objects :
     <tbody>
        <tr>
        <td>Object</td>
        <td>top.location_id.name</td>
        </tr> 
        <tr>
        <td>Top</td>
        <td>top.name</td>
        </tr>
        <tr>
        <td>Owner</td>
        <td>top.partner_id.name</td>
        </tr>
        <tr>
        <td>Staircase / Floor</td>
        <td>top.staircase / top.floor</td>
        </tr>
        <tr>
        <td>Surface</td>
        <td>top.surface</td>
        </tr>    
        <tr>
        <td>Monthly Rent</td>
        <td>round((top.surface or '0' ) * (top.lease_target or ''),0)</td>
        </tr>
        <tr>
        <td>Monthly Operating Cost</td>
        <td>round(top.operating_cost ,0)</td>
        </tr>
        <tr>
        <td>Usage</td>
        <td>top.usage</td>
        </tr>
        <tr>
        <td>Category</td>
        <td>top.category</td>
        </tr>
        <tr>
        <td>Rooms</td>
        <td>top.rooms</td>
        </tr>
        <tr>
        <td>Construction Year</td>
        <td>top.constructed</td>
        </tr>
        <tr>
        <td>Old Building</td>
        <td>top.old_building</td>
        </tr>
        <tr>
        <td>Elevator</td>
        <td>top.lift</td>
        </tr>
        <tr>
        <td>Handicap Accessible</td>
        <td>top.handicap</td>
        </tr>
        <tr>
        <td>Heating</td>
        <td>top.heating</td>
        </tr>
        <tr>
        <td>Heating Source</td>
        <td>top.heating_source</td>
        </tr>
        <tr>
        <td>Telefon</td>
        <td>top.telephon</td>
        </tr>
        <tr>
        <td>Internet</td>
        <td>top.internet</td>
        </tr>
        <tr>
        <td>Kabel TV</td>
        <td>top.cable</td>
        </tr>
        <tr>
        <td>Sat TV</td>
        <td>top.sat_tv</td>
        </tr>
        <tr>
        <td>Alarm</td>
        <td>top.alarm</td>
        </tr>
        <tr>
        
        <td COLSPAN=2>top.note_sales</td>
        </tr>
      </tbody>
 %endfor
  </body>
</html>
