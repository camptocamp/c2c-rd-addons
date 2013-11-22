## -*- coding: utf-8 -*-
<html>
%if context['data'] and context['data'].get('form'):
  <%form = True%>
%else:
  <%form = False%>
%endif


<head>
<b>Partner participation</b> requested by ${user.name}
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

<%setLang(user.context_lang)%>

% for partner in objects:
<p>
 Partner:   ${partner.name}
 Participations:
</p>
    <table  >

     <thead >
        <tr>
          <td>Share</td>
          <td>Paid In</td>
          <td>Agio</td>
          <td>Percentage</td>
          <td>Participation</td>
          <td>Consolidation</td>
          <td>Date from</td>
          <td>Date to</td>
          <td>Date Fiscal from</td>
          <td>Date Fiscal to</td>
          <td>Note</td>
          <td>State</td>
        </tr>
      </thead>

 %for share in partner.participation_current_ids:
     <tbody >
        <tr>
          <td style="text-align:right;white-space:nowrap;">${formatLang(share.name)}</td>
          <td style="text-align:right;white-space:nowrap;">${formatLang(share.paid_in or '')}</td>
          <td style="text-align:right;white-space:nowrap;">${formatLang(share.agio or '')}</td>
          <td style="text-align:right;white-space:nowrap;">${formatLang(share.percentage or'' )}</td>
          <td>${share.partner_id.name}</td>
          <td>${share.consolidation or ''}</td>
          <td>${share.valid_from or ''|entity}</td>
          <td>${share.valid_until or ''|entity}</td>
          <td>${share.valid_fiscal_from or ''|entity}</td>
          <td>${share.valid_fiscal_until or ''|entity}</td>
          <td>${share.comment or ''|entity}</td>
          <td>${share.state or ''|entity}</td>
        </tr>

     </tbody>
 %endfor
    </table>

%endfor

  </body>
</html>
