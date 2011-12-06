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

 %for partner in partner.participation_ids :
     <tbody >
        <tr>
          <td style="text-align:right;white-space:nowrap;">${formatLang(partner.name)}</td>
          <td style="text-align:right;white-space:nowrap;">${formatLang(partner.paid_in)}</td>
          <td style="text-align:right;white-space:nowrap;">${formatLang(partner.agio)}</td>
          <td style="text-align:right;white-space:nowrap;">${formatLang(partner.percentage or'' )}</td>
          <td>${partner.partner_id.name}</td>
          <td>${partner.consolidation or ''}</td>
          <td>${partner.valid_from or ''|entity}</td>
          <td>${partner.valid_until or ''|entity}</td>
          <td>${partner.valid_fiscal_from or ''|entity}</td>
          <td>${partner.valid_fiscal_until or ''|entity}</td>
          <td>${partner.comment or ''|entity}</td>
          <td>${partner.state or ''|entity}</td>
        </tr>

     </tbody>
 %endfor
    </table>

%endfor

  </body>
</html>
