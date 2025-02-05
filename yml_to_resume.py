from __future__ import annotations

import abc
import argparse
from copy import deepcopy
from pathlib import Path
from typing import ClassVar, Literal

import pydantic
import yaml


class ResumeSection(pydantic.BaseModel, abc.ABC):
    name: ClassVar[str]

    title: str

    @abc.abstractmethod
    def to_html(self) -> str:
        raise NotImplementedError


class SkillsSection(ResumeSection):
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

Region = Literal["sidebar", "main"]

SECTION_CLASSES_BY_REGION: dict[Region, list[ResumeSection]] = {
    "sidebar": [
        SkillsSection,
    ],
    "main": [
        HighlightsSection,
        ExperiencesSection,
        QualificationsSection,
        ProjectsSection,
    ],
}


def parse_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", default="bluegreen_resume_template.html")
    parser.add_argument("--resume-yml", default="bluegreen_resume.yml")
    parser.add_argument("--page-number", type=int, default=None)
    parser.add_argument("--output", default="resume.html")
    return parser.parse_args()


def convert_resume_yml_to_html(
    template: str, resume_yml: str, page_number: int | None = None
) -> str:
    page_numbers = [1, 2] if page_number is None else [page_number]
    template = deepcopy(template)
    for field in ["name", "tagline", "phone", "email", "location"]:
        template = template.replace(f"<!-- {field} -->", resume_yml[field])
    sections_yml = {}
    for i in page_numbers:
        sections_yml |= resume_yml[f"page_{i}"]
    for region, section_classes in SECTION_CLASSES_BY_REGION.items():
        template = template.replace(
            f"<!-- {region} -->",
            "".join(
                [
                    section_class(**sections_yml[section_class.name]).to_html()
                    for section_class in section_classes
                    if sections_yml.get(section_class.name) is not None
                ]
            ),
        )
    if page_number is not None:
        template = template.replace("<!-- footer -->", f"Page {page_number} of 2")
    return template


if __name__ == "__main__":
    args = parse_cli_args()
    html = convert_resume_yml_to_html(
        template=Path(args.template).read_text(),
        resume_yml=yaml.safe_load(Path(args.resume_yml).read_text()),
        page_number=args.page_number,
    )
    Path(args.output).write_text(html)
