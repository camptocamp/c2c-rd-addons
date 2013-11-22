## -*- coding: utf-8 -*-
<html>
<head>
                <b>Label Test</b> requested by ${user.name}
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

<p>
Selection:
%if context['data'] :
<%doc>
    FIXME - print default or actual paramaters
            waiting for Nicalas to fix bug and pass form params
</%doc>
  <table>
	    <tr>
	    <td></td>
            <td></td>
	    </tr>
  </table>
%endif
<p>
<%
chapter.__init__()
%>

    <table  >

     <thead >
        <tr>
          <td>Name</td>
          <td>Address</td>
        </tr>
      </thead>


 %for address in objects :
     <tbody >
        <tr>
          <td>${address.partner_id.name or ''|entity}  </td>

          <td><pre>${address.address_label or ''|entity}</pre>  </td>
        </tr>
      </tbody>
 %endfor
    </table>


  </body>
</html>
