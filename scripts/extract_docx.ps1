$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("H:\Source\repos\mvp-research-sheerssoft\docs\The Hospitality Revenue & Operational Blueprint - ver. Consultant_responses.docx")
$doc.Content.Text | Out-File "H:\Source\repos\mvp-research-sheerssoft\blueprint_text.txt" -Encoding UTF8
$doc.Close()
$word.Quit()
