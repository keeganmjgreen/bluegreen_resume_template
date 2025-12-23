uv run yml_to_resume.py --output=resume.html

uv run yml_to_resume.py --page-number=1 --output=resume_page_1.html
google-chrome resume_page_1.html --headless --print-to-pdf=resume_page_1.pdf --no-pdf-header-footer
rm resume_page_1.html

uv run yml_to_resume.py --page-number=2 --output=resume_page_2.html
google-chrome resume_page_2.html --headless --print-to-pdf=resume_page_2.pdf --no-pdf-header-footer
rm resume_page_2.html

pdfunite resume_page_1.pdf resume_page_2.pdf green_resume.pdf

rm resume_page_1.pdf
rm resume_page_2.pdf
