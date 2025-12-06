python yml_to_resume.py --resume-yml=green_cover_letter.yml --output=green_cover_letter.html

google-chrome green_cover_letter.html --headless --print-to-pdf=green_cover_letter.pdf --no-pdf-header-footer
rm green_cover_letter.html
