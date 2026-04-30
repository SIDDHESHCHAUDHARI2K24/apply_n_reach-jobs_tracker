"""Tests for job_profile latex_resume template_builder.

Covers rendering of technologies in projects and journal/year in research.
"""
from app.features.job_profile.latex_resume.template_builder import (
    _build_projects,
    _build_research,
)


class TestTemplateBuilderProjects:
    def test_technologies_appear_in_projects_section(self):
        """Projects with technologies render the technologies line in LaTeX."""
        projects = [
            {
                "project_name": "My Project",
                "description": "A cool project.",
                "start_month_year": "01/2023",
                "end_month_year": "06/2023",
                "reference_links": [],
                "technologies": ["Python", "FastAPI"],
            }
        ]
        latex = _build_projects(projects)
        assert "Technologies: Python, FastAPI" in latex

    def test_technologies_special_chars_escaped(self):
        """Technologies containing LaTeX special characters are escaped."""
        projects = [
            {
                "project_name": "My Project",
                "description": "Desc.",
                "reference_links": [],
                "technologies": ["C++", "AT&T SDK"],
            }
        ]
        latex = _build_projects(projects)
        assert r"C++" in latex
        assert r"\&" in latex

    def test_no_technologies_field_omits_line(self):
        """Projects without technologies do not produce a Technologies line."""
        projects = [
            {
                "project_name": "My Project",
                "description": "Desc.",
                "reference_links": [],
            }
        ]
        latex = _build_projects(projects)
        assert "Technologies:" not in latex

    def test_empty_technologies_list_omits_line(self):
        """Projects with an empty technologies list do not produce a Technologies line."""
        projects = [
            {
                "project_name": "My Project",
                "description": "Desc.",
                "reference_links": [],
                "technologies": [],
            }
        ]
        latex = _build_projects(projects)
        assert "Technologies:" not in latex

    def test_blank_technology_entries_are_filtered(self):
        """Blank strings in technologies list are ignored."""
        projects = [
            {
                "project_name": "My Project",
                "description": "Desc.",
                "reference_links": [],
                "technologies": ["Python", "  ", ""],
            }
        ]
        latex = _build_projects(projects)
        assert "Technologies: Python" in latex


class TestTemplateBuilderResearch:
    def test_journal_and_year_appear_in_heading(self):
        """Research with journal and year shows both in the project heading."""
        researches = [
            {
                "paper_name": "My Paper",
                "publication_link": "",
                "description": "",
                "journal": "Nature",
                "year": "2024",
            }
        ]
        latex = _build_research(researches)
        assert "Nature" in latex
        assert "2024" in latex
        assert r"\textit" in latex

    def test_journal_only_appears_in_heading(self):
        """Research with only journal (no year) still renders the journal."""
        researches = [
            {
                "paper_name": "My Paper",
                "publication_link": "",
                "description": "",
                "journal": "Science",
                "year": None,
            }
        ]
        latex = _build_research(researches)
        assert "Science" in latex
        assert r"\textit" in latex

    def test_year_only_appears_in_heading(self):
        """Research with only year (no journal) still renders the year."""
        researches = [
            {
                "paper_name": "My Paper",
                "publication_link": "",
                "description": "",
                "journal": None,
                "year": "2023",
            }
        ]
        latex = _build_research(researches)
        assert "2023" in latex
        assert r"\textit" in latex

    def test_no_journal_year_omits_textit(self):
        """Research without journal or year has no \\textit in the heading."""
        researches = [
            {
                "paper_name": "My Paper",
                "publication_link": "",
                "description": "",
            }
        ]
        latex = _build_research(researches)
        assert r"\textit" not in latex

    def test_journal_year_special_chars_escaped(self):
        """Journal name with LaTeX special chars is escaped."""
        researches = [
            {
                "paper_name": "My Paper",
                "publication_link": "",
                "description": "",
                "journal": "IEEE & ACM",
                "year": "2024",
            }
        ]
        latex = _build_research(researches)
        assert r"\&" in latex

    def test_technologies_and_journal_year_combined(self):
        """Combined test: project with technologies and research with journal/year."""
        projects = [
            {
                "project_name": "FastAPI App",
                "description": "A web API.",
                "reference_links": [],
                "technologies": ["Python", "FastAPI"],
            }
        ]
        researches = [
            {
                "paper_name": "My Study",
                "publication_link": "",
                "description": "",
                "journal": "Nature",
                "year": "2024",
            }
        ]
        project_latex = _build_projects(projects)
        research_latex = _build_research(researches)
        assert "Technologies: Python, FastAPI" in project_latex
        assert "Published in: Nature, 2024" not in research_latex  # uses heading format, not bullet
        assert "Nature" in research_latex
        assert "2024" in research_latex
