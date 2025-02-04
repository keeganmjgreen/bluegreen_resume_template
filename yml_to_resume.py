from __future__ import annotations

import abc
import argparse
from pathlib import Path
from typing import Literal
import pydantic
import yaml

parser = argparse.ArgumentParser()
parser.add_argument("--pages", default="1,2")
parser.add_argument("--template", default="resume_template.html")
parser.add_argument("--resume-yml", default="bluegreen_resume.yml")
parser.add_argument("--output", default="resume.html")
args = parser.parse_args()
pages = [int(page) for page in args.pages.split(",")]


class ResumeSection(pydantic.BaseModel, abc.ABC):
    title: str

    @abc.abstractmethod
    def to_html(self) -> str:
        raise NotImplementedError


class SkillsResumeSection(ResumeSection):
    content: dict[str, list[str]]

    def to_html(self) -> str:
        return f'<div class="heading left-heading">{self.title}</div>' + "".join(
            [
                f'<div class="entry-heading"><div class="left">{skill_group_name}</div></div>'
                + '<ul class="padded-list">'
                + "".join([f"<li>{skill}</li>" for skill in skills])
                + "</ul>"
                for skill_group_name, skills in self.content.items()
            ]
        )


class HighlightsResumeSection(ResumeSection):
    content: list[str]

    def to_html(self) -> str:
        return (
            f'<div class="heading right-heading">{self.title}</div>'
            + "<ul>"
            + "".join([f"<li>{highlight}</li>" for highlight in self.content])
            + "</ul>"
        )


class ResumeSectionWithEntries(ResumeSection):
    content: list[ResumeEntry]
    outer_list_css_class: Literal["padded-list", "unpadded-list"] = "unpadded-list"

    def to_html(self) -> str:
        return f'<div class="heading right-heading">{self.title}</div>' + "".join(
            [
                f'<div class="entry-heading"><div class="left">{entry.name}</div><div class="right">{entry.period}</div></div>'
                + (
                    f'<div class="entry-subheading"><div class="left">{entry.institution}</div><div class="right">{entry.location}</div></div>'
                    if entry.institution or entry.location
                    else ""
                )
                + f'<ul class="{self.outer_list_css_class}">'
                + "".join(
                    [
                        f"<li>{x if type(x) is str else list(x.keys())[0] + f'<ul class="unpadded-list">{"".join([f"<li>{v}</li>" for v in list(x.values())[0]])}</ul>'}</li>"
                        for x in entry.content
                    ]
                )
                + "</ul>"
                for entry in self.content
            ]
        )


class ExperiencesSection(ResumeSectionWithEntries):
    title: str = "Experience"
    outer_list_css_class: Literal["padded-list"] = "padded-list"


class QualificationsSection(ResumeSectionWithEntries):
    title: str = "Education"


class ProjectsSection(ResumeSectionWithEntries):
    title: str = "Projects"


class ResumeEntry(pydantic.BaseModel):
    name: str
    period: str
    institution: str = ""
    location: str = ""
    content: list[str | SingleKeyDict[str, list[str]]]


SingleKeyDict = dict


yml = yaml.safe_load(Path(args.resume_yml).read_text())
template = Path(args.template).read_text()
template = template.replace("<!-- name -->", yml["name"])
template = template.replace("<!-- tagline -->", yml["tagline"])
for x in ["phone", "email", "location"]:
    template = template.replace(f"<!-- {x} -->", yml[x])
sections = {}
for page in pages:
    sections |= yml[f"page_{page}"]
sidebar_output = ""
if sections.get("skills_section") is not None:
    sidebar_output += SkillsResumeSection(**sections["skills_section"]).to_html()
template = template.replace("<!-- sidebar -->", sidebar_output)
main_output = ""
if sections.get("highlights_section") is not None:
    main_output += HighlightsResumeSection(**sections["highlights_section"]).to_html()
for section_name in [
    "experiences_section",
    "qualifications_section",
    "projects_section",
]:
    if sections.get(section_name) is not None:
        main_output += {
            "experiences_section": ExperiencesSection,
            "qualifications_section": QualificationsSection,
            "projects_section": ProjectsSection,
        }[section_name](**sections[section_name]).to_html()
template = template.replace("<!-- main -->", main_output)
Path(args.output).write_text(template)
