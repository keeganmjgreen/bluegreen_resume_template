# <span style="background: linear-gradient(to right, #155799, #159957); -webkit-background-clip: text; background-clip: text; color: transparent; ">Bluegreen</span> resume template

Get your next <text style="font-weight: bold; background: linear-gradient(to right, #159957, #155799); -webkit-background-clip: text; background-clip: text; color: transparent; ">cleantech</text> role.

<div style="display: grid; grid-template-columns: repeat(2, 50%); align-items: center;">
    <div style="padding: 10px;"><text style="font-size: large; font-weight: bold; background: linear-gradient(to right, #155799, #159957); -webkit-background-clip: text; background-clip: text; color: transparent; ">One command</text> generates portable HTML and PDF files, for ease of sharing with others or hosting as a website.</div>
    <div style="padding: 10px;"><img src="readme_assets/resume-1.png" width="100%" style="filter: drop-shadow(0 5px 5px gray)"></div> <!-- pdftoppm -png -r 300 resume.pdf resume.png -->
    <div style="padding: 10px;"><img src="readme_assets/mobile_1.png" width="45%" style="border: 1px solid black; border-radius: 10px;"> <img src="readme_assets/mobile_2.png" width="45%" style="border: 1px solid black; border-radius: 10px;"></div>
    <div style="padding: 10px;"><text style="font-size: large; font-weight: bold; background: linear-gradient(to right, #155799, #159957); -webkit-background-clip: text; background-clip: text; color: transparent; ">Responsive layout</text> that looks great both on the web and on mobile.</div>
    <div style="padding: 10px;"><text style="font-size: large; font-weight: bold; background: linear-gradient(to right, #155799, #159957); -webkit-background-clip: text; background-clip: text; color: transparent; ">Automatic dark mode</text> to match that of whatever device the HTML page is being viewed on.</div>
    <div style="padding: 10px;"><img src="readme_assets/dark_mode.png" width="100%" style="border-radius: 5px;"></div>
    <div style="padding: 10px;"><img src="readme_assets/css_variables_screenshot.png" width="100%"></div>
    <div style="padding: 10px;"><text style="font-size: large; font-weight: bold; background: linear-gradient(to right, #155799, #159957); -webkit-background-clip: text; background-clip: text; color: transparent; ">Extremely customizable</text> (fonts, colors, spacing, etc.) thanks to CSS variables.</div>
    <div style="padding: 10px;"><text style="font-size: large; font-weight: bold; background: linear-gradient(to right, #155799, #159957); -webkit-background-clip: text; background-clip: text; color: transparent; ">Easy to fill in</text> your resume details, thanks to one YAML config file.</div>
    <div style="padding: 10px;"><img src="readme_assets/yml_screenshot.png" width="100%"></div>
</div>

## Getting started

1. Fill in the `bluegreen_resume.yml` template with your resume details.
2. Customize the CSS variables in `bluegreen_resume_template.html` to your liking.
3. Run `build_resume.sh` to generate a portable HTML resume (`resume.html`) and a two-page resume PDF (`resume.pdf`) of equal quality. This requires:
   - python>=3.10
   - pydantic>=2
   - pyyaml
   - Google Chrome (to print the resume to PDF in the background)
