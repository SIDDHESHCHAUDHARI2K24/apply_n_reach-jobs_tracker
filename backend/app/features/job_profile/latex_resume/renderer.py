"""PDF rendering via pdflatex subprocess."""
import shutil
import subprocess
import tempfile
from pathlib import Path


class LatexCompileError(Exception):
    """Raised when pdflatex compilation fails."""

    def __init__(self, message: str, log_tail: str = ""):
        super().__init__(message)
        self.log_tail = log_tail


def render_pdf(latex_source: str, filename_stem: str = "resume") -> bytes:
    """Compile latex_source to PDF bytes via pdflatex.

    Args:
        latex_source: Complete LaTeX document source string.
        filename_stem: Base filename for the temp .tex file (no extension, no spaces).

    Returns:
        Raw PDF bytes.

    Raises:
        LatexCompileError: If pdflatex is not found or compilation fails.
        FileNotFoundError: If pdflatex binary is not installed.
    """
    pdflatex = shutil.which("pdflatex")
    if pdflatex is None:
        raise LatexCompileError(
            "pdflatex not found on PATH. Install TeX Live or MiKTeX.",
            log_tail=""
        )

    # Sanitize filename_stem: replace spaces and special chars
    safe_stem = "".join(c if c.isalnum() or c in "-_" else "_" for c in filename_stem)
    if not safe_stem:
        safe_stem = "resume"

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = Path(tmpdir) / f"{safe_stem}.tex"
        pdf_path = Path(tmpdir) / f"{safe_stem}.pdf"
        log_path = Path(tmpdir) / f"{safe_stem}.log"

        tex_path.write_text(latex_source, encoding="utf-8")

        # Run pdflatex (twice for cross-references)
        cmd = [pdflatex, "-interaction=nonstopmode", "-output-directory", tmpdir, str(tex_path)]
        for _ in range(2):
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )

        if not pdf_path.exists() or result.returncode != 0:
            # Extract log tail for error reporting
            log_tail = ""
            if log_path.exists():
                log_text = log_path.read_text(encoding="utf-8", errors="replace")
                # Find first error line
                lines = log_text.splitlines()
                error_lines = [l for l in lines if l.startswith("!")]
                if error_lines:
                    log_tail = "\n".join(error_lines[:10])
                else:
                    log_tail = "\n".join(lines[-30:])
            raise LatexCompileError(
                f"pdflatex compilation failed (exit code {result.returncode})",
                log_tail=log_tail,
            )

        return pdf_path.read_bytes()
