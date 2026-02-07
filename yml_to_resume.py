from __future__ import annotations

import abc
import argparse
from pathlib import Path
from typing import Any, ClassVar, Literal

import pydantic
import yaml


class ResumeSection(pydantic.BaseModel, abc.ABC):
    name: ClassVar[str]

    @abc.abstractmethod
    def to_html(self) -> str:
        raise NotImplementedError


class SkillsSection(ResumeSection):
    name = "skills_section"

    title: str
    content: list[str] | dict[str, list[str]]

    def to_html(self) -> str:
        content = (
            self.content if isinstance(self.content, dict) else {None: self.content}
        )
        return f'<div class="heading left-heading">{self.title}</div>' + "".join(
            [
                (
                    f'<div class="entry-heading"><div class="left">{skill_group_name}</div></div>'
                    if skill_group_name
                    else ""
                )
                + '<ul class="padded-list">'
                + "".join([f"<li>{skill}</li>" for skill in skills])
                + "</ul>"
                for skill_group_name, skills in content.items()
            ]
        )


class HighlightsSection(ResumeSection):
    name = "highlights_section"

    title: str
    content: list[str]

    def to_html(self) -> str:
        return (
            f'<div class="heading right-heading">{self.title}</div>'
            + "<ul>"
            + "".join([f"<li>{highlight}</li>" for highlight in self.content])
            + "</ul>"
        )


class ResumeSectionWithEntries(ResumeSection):
    title: str
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


class ParagraphSection(ResumeSection):
    name = "paragraph_section"

    content: list[str]

    def to_html(self) -> str:
        return "".join([f"<p>{paragraph}</p>" for paragraph in self.content])


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
        ParagraphSection,
    ],
}


def parse_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", default="bluegreen_resume_template.html")
    parser.add_argument("--subtemplate", default="bluegreen_resume_subtemplate.html")
    parser.add_argument("--styles", default="styles.css")
    parser.add_argument("--resume-yml", default="resume.yml")
    parser.add_argument("--page-number", type=int, default=None)
    parser.add_argument("--populated-subtemplate", default="populated_subtemplate.html")
    parser.add_argument("--output", default="resume.html")
    return parser.parse_args()


def populate_subtemplate(
    subtemplate: str, resume_yml: dict[str, Any], page_number: int | None = None
) -> str:
    page_numbers = [1, 2] if page_number is None else [page_number]
    for field in ["name", "tagline", "phone", "email", "location"]:
        subtemplate = subtemplate.replace(f"<!-- {field} -->", resume_yml[field])
    sections_yml = {}
    for i in page_numbers:
        sections_yml |= resume_yml.get(f"page_{i}", {})
    for region, section_classes in SECTION_CLASSES_BY_REGION.items():
        subtemplate = subtemplate.replace(
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
        subtemplate = subtemplate.replace("<!-- footer -->", f"Page {page_number} of 2")

    return subtemplate


def populate_template(template: str, styles: str, populated_subtemplate: str) -> str:
    template = template.replace("/* style */", "\n        ".join(styles.split("\n")))
    template = template.replace(
        "<!-- subtemplate -->", "\n    ".join(populated_subtemplate.split("\n"))
    )

    return template


if __name__ == "__main__":
    args = parse_cli_args()
    populated_subtemplate = populate_subtemplate(
        subtemplate=Path(args.subtemplate).read_text(),
        resume_yml=yaml.safe_load(Path(args.resume_yml).read_text()),
        page_number=args.page_number,
    )
    populated_template = populate_template(
        template=Path(args.template).read_text(),
        styles=Path(args.styles).read_text(),
        populated_subtemplate=populated_subtemplate,
    )
    Path(args.populated_subtemplate).write_text(populated_subtemplate)
    Path(args.output).write_text(populated_template)
