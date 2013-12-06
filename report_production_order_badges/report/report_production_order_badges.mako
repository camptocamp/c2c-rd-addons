## -*- coding: utf-8 -*-
<html>
  <head/>
  <body>

    <style  type="text/css">
     table {
       border-collapse: collapse;
       page-break-after:auto;
       cellspacing="5";
       font-size:20px;
           }
     td {margin: 0px; padding: 3px; border: 1px solid lightgrey;  vertical-align: top; }
    </style>

%for sale_order in objects:
%for line  in sale_order.order_line :
%for prod_line in line.stock_dispo_production_ids:
<br>
<br>
    <table>
      <tbody>
        <tr>
          <td>Dispo-Nr </td> <td>${sale_order.name} vom ${sale_order.date_order}  </td>
        </tr>
        <tr>
          <td>Auftraggeber</td> <td>${sale_order.partner_id.name or ''}  </td>
        </tr>
        <tr>
          <td>Kundenreferenz</td> <td>${sale_order.client_order_ref or ''}</td>
        </tr>
        <tr>
          <td>Empfänger</td> <td>${sale_order.partner_shipping_id.partner_id.name or ''}  </td>
        </tr>
        <tr>
          <td>BIO-Produkt / Sorte</td> <td>${line.product_id.name} ${line.product_id.variants or ''} ${line.product_packaging.name or ''}   </td>
        </tr>
        <tr>
          <td>Los</td> <td>${(line.prodlot_id.name or '')+'/'+(line.prodlot_id.ref or '')}  </td>
        </tr>
%if line.prodlot_id.global_gap_number:
        <tr>
          <td>Global-Gap-Nr</td> <td>${line.prodlot_id.global_gap_number }  </td>
        </tr>
%endif:
        <tr>
          <td>Feldname/-Nr.(AMA)</td> <td>${ line.location_product_id.name or ''}  </td>
        </tr>
        <tr>
          <td>Sortierung </td> <td>${prod_line.name  or ''}  </td>
        </tr>
        <tr>
          <td>Gewicht </td> <td>${str(prod_line.product_qty).replace(',000','')} ${line.product_uos.name or '' }  </td>
        </tr>
        <tr>
          <td>Datum der Aufbereitung </td> <td>${getattr(prod_line,"date","") or ''}  </td>
        </tr>
      </tbody>
    </table>
<br>
 %if line.trading_unit_owner_id:
    Das Gebinde steht im Eigentum der
    ${line.trading_unit_owner_id.name }
    , bitte retournieren!
 %endif:
<p style="page-break-after:always"></p>
%endfor
%endfor
%endfor
  </body>
</html>
