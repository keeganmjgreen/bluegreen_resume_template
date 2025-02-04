import argparse
from pathlib import Path
import yaml

parser = argparse.ArgumentParser()
parser.add_argument("--pages", default="1,2")
parser.add_argument("--template", default="resume_template.html")
parser.add_argument("--resume-yml", default="bluegreen_resume.yml")
parser.add_argument("--output", default="resume.html")
args = parser.parse_args()
pages = [int(page) for page in args.pages.split(",")]


yml = yaml.safe_load(Path(args.resume_yml).read_text())
template = Path(args.template).read_text()
template = template.replace("<!-- name -->", yml["name"])
template = template.replace("<!-- tagline -->", yml["tagline"])
for x in ["phone", "email", "location"]:
    template = template.replace(f"<!-- {x} -->", yml[x])
sidebar_yml = {}
main_yml = {}
for page in pages:
    sidebar_yml |= yml[f"page_{page}"].get("sidebar", {})
    main_yml |= yml[f"page_{page}"].get("main", {})
sidebar_output = ""
if skillset_yml := sidebar_yml.get("skillset"):
    sidebar_output += (
        f'<div class="heading left-heading">{sidebar_yml["skillset_title"]}</div>'
        + "".join(
            [
                f'<div class="entry-heading"><div class="left">{skill_group}</div></div>'
                + '<ul class="padded-list">'
                + "".join([f"<li>{skill}</li>" for skill in skills])
                + "</ul>"
                for skill_group, skills in skillset_yml.items()
            ]
        )
    )
template = template.replace("<!-- sidebar -->", sidebar_output)
main_output = ""
if highlights := main_yml.get("highlights"):
    main_output += (
        f'<div class="heading right-heading">{main_yml["highlights_title"]}</div>'
        + "<ul>"
        + "".join([f"<li>{highlight}</li>" for highlight in main_yml["highlights"]])
        + "</ul>"
    )
for section_name in ["experiences", "qualifications", "projects"]:
    if section := main_yml.get(section_name):
        main_output += (
            f'<div class="heading right-heading">{main_yml[f"{section_name}_title"]}</div>'
            + "".join(
                [
                    f'<div class="entry-heading"><div class="left">{item["name"]}</div><div class="right">{item["period"]}</div></div>'
                    + (
                        f'<div class="entry-subheading"><div class="left">{item["institution"]}</div><div class="right">{item["location"]}</div></div>'
                        if item.get("institution") and item.get("location")
                        else ""
                    )
                    + f'<ul class="{"padded" if section_name == "experiences" else "unpadded"}-list">'
                    + "".join(
                        [
                            f"<li>{x if type(x) is str else list(x.keys())[0] + f'<ul class="unpadded-list">{"".join([f"<li>{v}</li>" for v in list(x.values())[0]])}</ul>'}</li>"
                            for x in item["content"]
                        ]
                    )
                    + "</ul>"
                    for item in section
                ]
            )
        )
template = template.replace("<!-- main -->", main_output)
Path(args.output).write_text(template)
