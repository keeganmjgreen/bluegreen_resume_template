python yml_to_resume.py --resume-yml=cover_letter.yml --output=cover_letter.html

google-chrome cover_letter.html --headless --print-to-pdf=green_cover_letter.pdf --no-pdf-header-footer
rm cover_letter.html
