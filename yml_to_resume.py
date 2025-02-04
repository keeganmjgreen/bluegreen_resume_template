from __future__ import annotations

import argparse
from pathlib import Path
import pydantic
import yaml

parser = argparse.ArgumentParser()
parser.add_argument("--pages", default="1,2")
parser.add_argument("--template", default="resume_template.html")
parser.add_argument("--resume-yml", default="bluegreen_resume.yml")
parser.add_argument("--output", default="resume.html")
args = parser.parse_args()
pages = [int(page) for page in args.pages.split(",")]


class ResumeSection(pydantic.BaseModel):
    title: str


class SkillsResumeSection(ResumeSection):
    content: dict[str, list[str]]


class HighlightsResumeSection(ResumeSection):
    content: list[str]


SingleKeyDict = dict


class ResumeSectionWithEntries(ResumeSection):
    content: list[ResumeEntry]


class ResumeEntry(pydantic.BaseModel):
    name: str
    period: str
    institution: str = ""
    location: str = ""
    content: list[str | SingleKeyDict[str, list[str]]]


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
if sidebar_yml.get("skills_section") is not None:
    section = SkillsResumeSection(**sidebar_yml["skills_section"])
    sidebar_output += (
        f'<div class="heading left-heading">{section.title}</div>'
        + "".join(
            [
                f'<div class="entry-heading"><div class="left">{skill_group}</div></div>'
                + '<ul class="padded-list">'
                + "".join([f"<li>{skill}</li>" for skill in skills])
                + "</ul>"
                for skill_group, skills in section.content.items()
            ]
        )
    )
template = template.replace("<!-- sidebar -->", sidebar_output)
main_output = ""
if main_yml.get("highlights_section") is not None:
    section = HighlightsResumeSection(**main_yml["highlights_section"])
    main_output += (
        f'<div class="heading right-heading">{section.title}</div>'
        + "<ul>"
        + "".join([f"<li>{highlight}</li>" for highlight in section.content])
        + "</ul>"
    )
for section_name in [
    "experiences_section",
    "qualifications_section",
    "projects_section",
]:
    if main_yml.get(section_name) is not None:
        section = ResumeSectionWithEntries(**main_yml[section_name])
        main_output += (
            f'<div class="heading right-heading">{section.title}</div>'
            + "".join(
                [
                    f'<div class="entry-heading"><div class="left">{entry.name}</div><div class="right">{entry.period}</div></div>'
                    + (
                        f'<div class="entry-subheading"><div class="left">{entry.institution}</div><div class="right">{entry.location}</div></div>'
                        if entry.institution or entry.location
                        else ""
                    )
                    + f'<ul class="{"padded" if section_name == "experiences_section" else "unpadded"}-list">'
                    + "".join(
                        [
                            f"<li>{x if type(x) is str else list(x.keys())[0] + f'<ul class="unpadded-list">{"".join([f"<li>{v}</li>" for v in list(x.values())[0]])}</ul>'}</li>"
                            for x in entry.content
                        ]
                    )
                    + "</ul>"
                    for entry in section.content
                ]
            )
        )
template = template.replace("<!-- main -->", main_output)
Path(args.output).write_text(template)
