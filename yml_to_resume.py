from __future__ import annotations

import abc
import argparse
from pathlib import Path
from typing import ClassVar, Literal
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
    name: ClassVar[str]

    title: str

    @abc.abstractmethod
    def to_html(self) -> str:
        raise NotImplementedError


class SkillsResumeSection(ResumeSection):
    name = "skills_section"

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


class HighlightsSection(ResumeSection):
    name = "highlights_section"

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
    outer_list_css_class: ClassVar[Literal["padded-list", "unpadded-list"]]

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
    name = "experiences_section"
    outer_list_css_class = "padded-list"

    title: str = "Experience"


class QualificationsSection(ResumeSectionWithEntries):
    name = "qualifications_section"
    outer_list_css_class = "unpadded-list"

    title: str = "Education"


class ProjectsSection(ResumeSectionWithEntries):
    name = "projects_section"
    outer_list_css_class = "unpadded-list"

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
sections_yml = {}
for page in pages:
    sections_yml |= yml[f"page_{page}"]
template = template.replace(
    "<!-- sidebar -->",
    SkillsResumeSection(**sections_yml["skills_section"]).to_html()
    if sections_yml.get("skills_section") is not None
    else "",
)
MAIN_SECTIONS: list[ResumeSection] = [
    HighlightsSection,
    ExperiencesSection,
    QualificationsSection,
    ProjectsSection,
]
template = template.replace(
    "<!-- main -->",
    "".join(
        [
            section_class(**sections_yml[section_class.name]).to_html()
            for section_class in MAIN_SECTIONS
            if sections_yml.get(section_class.name) is not None
        ]
    ),
)
Path(args.output).write_text(template)
