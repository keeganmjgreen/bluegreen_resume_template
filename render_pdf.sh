sed -i -e 's/printPage = 0/printPage = 1/g' resume.html
google-chrome resume.html --headless --print-to-pdf=resume_page_1.pdf --no-pdf-header-footer

sed -i -e 's/printPage = 1/printPage = 2/g' resume.html
google-chrome resume.html --headless --print-to-pdf=resume_page_2.pdf --no-pdf-header-footer

sed -i -e 's/printPage = 2/printPage = 0/g' resume.html

pdfunite resume_page_1.pdf resume_page_2.pdf resume.pdf

rm resume_page_1.pdf
rm resume_page_2.pdf
