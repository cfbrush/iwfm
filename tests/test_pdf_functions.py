# test_pdf_functions.py
# unit tests for PDF functions: pdf_addpages, pdf_cell, pdf_combine,
#                               pdf_create, pdf_save, pdf_setfont
# Copyright (C) 2026 University of California
# -----------------------------------------------------------------------------
# This information is free; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This work is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# For a copy of the GNU General Public License, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# -----------------------------------------------------------------------------

import pytest

# Check if fpdf is available
fpdf = pytest.importorskip("fpdf", reason="fpdf library not installed")

import iwfm


# =============================================================================
# Tests for pdf_create
# =============================================================================
class TestPdfCreate:
    """Tests for the pdf_create function."""

    def test_create_default_pdf(self):
        """Test creating PDF with default parameters."""
        pdf = iwfm.pdf_create()
        assert pdf is not None
        assert isinstance(pdf, fpdf.FPDF)

    def test_create_portrait_pdf(self):
        """Test creating portrait-oriented PDF."""
        pdf = iwfm.pdf_create(layout='P')
        assert pdf is not None

    def test_create_landscape_pdf(self):
        """Test creating landscape-oriented PDF."""
        pdf = iwfm.pdf_create(layout='L')
        assert pdf is not None

    def test_create_pdf_with_inches(self):
        """Test creating PDF with inch units."""
        pdf = iwfm.pdf_create(units='in')
        assert pdf is not None

    def test_create_pdf_with_millimeters(self):
        """Test creating PDF with millimeter units."""
        pdf = iwfm.pdf_create(units='mm')
        assert pdf is not None

    def test_create_pdf_with_centimeters(self):
        """Test creating PDF with centimeter units."""
        pdf = iwfm.pdf_create(units='cm')
        assert pdf is not None

    def test_create_pdf_with_points(self):
        """Test creating PDF with point units."""
        pdf = iwfm.pdf_create(units='pt')
        assert pdf is not None

    def test_create_letter_size_pdf(self):
        """Test creating Letter size PDF."""
        pdf = iwfm.pdf_create(pagesize='Letter')
        assert pdf is not None

    def test_create_a4_size_pdf(self):
        """Test creating A4 size PDF."""
        pdf = iwfm.pdf_create(pagesize='A4')
        assert pdf is not None

    def test_create_legal_size_pdf(self):
        """Test creating Legal size PDF."""
        pdf = iwfm.pdf_create(pagesize='Legal')
        assert pdf is not None

    def test_create_pdf_all_custom_params(self):
        """Test creating PDF with all custom parameters."""
        pdf = iwfm.pdf_create(layout='L', units='mm', pagesize='A4')
        assert pdf is not None

    def test_created_pdf_can_add_page(self):
        """Test that created PDF can have pages added."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        # Should not raise an exception


# =============================================================================
# Tests for pdf_addpages
# =============================================================================
class TestPdfAddpages:
    """Tests for the pdf_addpages function."""

    def test_add_single_page(self):
        """Test adding a single page."""
        pdf = iwfm.pdf_create()
        result = iwfm.pdf_addpages(pdf, pages=1)
        assert result is not None
        assert result is pdf

    def test_add_default_pages(self):
        """Test adding default number of pages (1)."""
        pdf = iwfm.pdf_create()
        result = iwfm.pdf_addpages(pdf)
        assert result is not None

    def test_add_multiple_pages(self):
        """Test adding multiple pages."""
        pdf = iwfm.pdf_create()
        result = iwfm.pdf_addpages(pdf, pages=5)
        assert result is not None

    def test_add_zero_pages(self):
        """Test adding zero pages."""
        pdf = iwfm.pdf_create()
        result = iwfm.pdf_addpages(pdf, pages=0)
        assert result is not None

    def test_add_many_pages(self):
        """Test adding many pages."""
        pdf = iwfm.pdf_create()
        result = iwfm.pdf_addpages(pdf, pages=100)
        assert result is not None

    def test_returns_same_pdf_object(self):
        """Test that function returns the same PDF object."""
        pdf = iwfm.pdf_create()
        original_id = id(pdf)
        result = iwfm.pdf_addpages(pdf, pages=3)
        assert id(result) == original_id

    def test_added_pages_can_be_saved(self, tmp_path):
        """Test that PDF with added pages can be saved."""
        pdf = iwfm.pdf_create()
        pdf = iwfm.pdf_addpages(pdf, pages=3)

        output_path = tmp_path / "output.pdf"
        pdf.output(str(output_path))
        assert output_path.exists()
        assert output_path.stat().st_size > 0


# =============================================================================
# Tests for pdf_setfont
# =============================================================================
class TestPdfSetfont:
    """Tests for the pdf_setfont function."""

    def test_set_default_font(self):
        """Test setting default font."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        result = iwfm.pdf_setfont(pdf)
        assert result is not None
        assert result is pdf

    def test_set_arial_font(self):
        """Test setting Arial font."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        result = iwfm.pdf_setfont(pdf, font='Arial')
        assert result is not None

    def test_set_helvetica_font(self):
        """Test setting Helvetica font."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        result = iwfm.pdf_setfont(pdf, font='Helvetica')
        assert result is not None

    def test_set_times_font(self):
        """Test setting Times font."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        result = iwfm.pdf_setfont(pdf, font='Times')
        assert result is not None

    def test_set_courier_font(self):
        """Test setting Courier font."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        result = iwfm.pdf_setfont(pdf, font='Courier')
        assert result is not None

    def test_set_bold_style(self):
        """Test setting bold style."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        result = iwfm.pdf_setfont(pdf, style='B')
        assert result is not None

    def test_set_italic_style(self):
        """Test setting italic style."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        result = iwfm.pdf_setfont(pdf, style='I')
        assert result is not None

    def test_set_underline_style(self):
        """Test setting underline style."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        result = iwfm.pdf_setfont(pdf, style='U')
        assert result is not None

    def test_set_bold_italic_style(self):
        """Test setting bold italic style."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        result = iwfm.pdf_setfont(pdf, style='BI')
        assert result is not None

    def test_set_regular_style(self):
        """Test setting regular (no style) font."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        result = iwfm.pdf_setfont(pdf, style='')
        assert result is not None

    def test_set_small_font_size(self):
        """Test setting small font size."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        result = iwfm.pdf_setfont(pdf, size=8)
        assert result is not None

    def test_set_large_font_size(self):
        """Test setting large font size."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        result = iwfm.pdf_setfont(pdf, size=72)
        assert result is not None

    def test_set_all_custom_font_params(self):
        """Test setting all custom font parameters."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        result = iwfm.pdf_setfont(pdf, font='Courier', style='BI', size=14)
        assert result is not None

    def test_returns_same_pdf_object(self):
        """Test that function returns the same PDF object."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        original_id = id(pdf)
        result = iwfm.pdf_setfont(pdf)
        assert id(result) == original_id


# =============================================================================
# Tests for pdf_cell
# =============================================================================
class TestPdfCell:
    """Tests for the pdf_cell function."""

    def test_create_default_cell(self):
        """Test creating cell with default parameters."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        result = iwfm.pdf_cell(pdf)
        assert result is not None
        assert result is pdf

    def test_create_cell_with_text(self):
        """Test creating cell with text content."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        result = iwfm.pdf_cell(pdf, t='Hello World')
        assert result is not None

    def test_create_cell_with_custom_dimensions(self):
        """Test creating cell with custom height and width."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        result = iwfm.pdf_cell(pdf, h=10, w=5)
        assert result is not None

    def test_create_cell_with_border(self):
        """Test creating cell with border."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        result = iwfm.pdf_cell(pdf, b=1)
        assert result is not None

    def test_create_cell_left_aligned(self):
        """Test creating left-aligned cell."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        result = iwfm.pdf_cell(pdf, a='L')
        assert result is not None

    def test_create_cell_right_aligned(self):
        """Test creating right-aligned cell."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        result = iwfm.pdf_cell(pdf, a='R')
        assert result is not None

    def test_create_cell_center_aligned(self):
        """Test creating center-aligned cell."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        result = iwfm.pdf_cell(pdf, a='C')
        assert result is not None

    def test_create_cell_all_custom_params(self):
        """Test creating cell with all custom parameters."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        result = iwfm.pdf_cell(pdf, h=8, w=3, t='Test', b=1, a='L')
        assert result is not None

    def test_create_multiple_cells(self):
        """Test creating multiple cells."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        pdf = iwfm.pdf_cell(pdf, t='Cell 1')
        pdf = iwfm.pdf_cell(pdf, t='Cell 2')
        pdf = iwfm.pdf_cell(pdf, t='Cell 3')
        assert pdf is not None

    def test_returns_same_pdf_object(self):
        """Test that function returns the same PDF object."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        original_id = id(pdf)
        result = iwfm.pdf_cell(pdf, t='Test')
        assert id(result) == original_id


# =============================================================================
# Tests for pdf_save
# =============================================================================
class TestPdfSave:
    """Tests for the pdf_save function."""

    def test_save_empty_pdf(self, tmp_path):
        """Test saving an empty PDF (with one page)."""
        pdf = iwfm.pdf_create()
        pdf.add_page()

        output_path = tmp_path / "output.pdf"
        iwfm.pdf_save(pdf, str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_save_pdf_with_content(self, tmp_path):
        """Test saving PDF with text content."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, 'Hello World')

        output_path = tmp_path / "output.pdf"
        iwfm.pdf_save(pdf, str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_save_pdf_with_multiple_pages(self, tmp_path):
        """Test saving PDF with multiple pages."""
        pdf = iwfm.pdf_create()
        for i in range(5):
            pdf.add_page()
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, f'Page {i + 1}')

        output_path = tmp_path / "output.pdf"
        iwfm.pdf_save(pdf, str(output_path))

        assert output_path.exists()

    def test_save_pdf_with_pdf_extension(self, tmp_path):
        """Test saving PDF with .pdf extension."""
        pdf = iwfm.pdf_create()
        pdf.add_page()

        output_path = tmp_path / "document.pdf"
        iwfm.pdf_save(pdf, str(output_path))

        assert output_path.exists()

    def test_save_pdf_to_subdirectory(self, tmp_path):
        """Test saving PDF to subdirectory."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        pdf = iwfm.pdf_create()
        pdf.add_page()

        output_path = subdir / "output.pdf"
        iwfm.pdf_save(pdf, str(output_path))

        assert output_path.exists()

    def test_save_returns_none(self, tmp_path):
        """Test that pdf_save returns None."""
        pdf = iwfm.pdf_create()
        pdf.add_page()

        output_path = tmp_path / "output.pdf"
        result = iwfm.pdf_save(pdf, str(output_path))

        assert result is None

    def test_save_overwrites_existing_file(self, tmp_path):
        """Test that saving overwrites existing file."""
        pdf1 = iwfm.pdf_create()
        pdf1.add_page()

        output_path = tmp_path / "output.pdf"
        iwfm.pdf_save(pdf1, str(output_path))
        size1 = output_path.stat().st_size

        # Create larger PDF and save to same path
        pdf2 = iwfm.pdf_create()
        for _ in range(10):
            pdf2.add_page()
            pdf2.set_font('Arial', '', 12)
            pdf2.cell(0, 10, 'More content to make file larger')

        iwfm.pdf_save(pdf2, str(output_path))
        size2 = output_path.stat().st_size

        assert size2 > size1


# =============================================================================
# Tests for pdf_combine
# =============================================================================
class TestPdfCombine:
    """Tests for the pdf_combine function."""

    @pytest.fixture
    def pypdf_available(self):
        """Check if pypdf is available."""
        try:
            import pypdf  # noqa: F401
            assert pypdf is not None
            return True
        except ImportError:
            pytest.skip("pypdf library not installed")

    def create_test_pdf(self, filepath, content="Test"):
        """Helper to create a simple test PDF."""
        pdf = iwfm.pdf_create()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, content)
        pdf.output(str(filepath))

    def test_combine_single_pdf(self, tmp_path, pypdf_available):
        """Test combining a single PDF."""
        # Create source directory with one PDF
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        self.create_test_pdf(source_dir / "doc1.pdf", "Document 1")

        # Combine
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        count = iwfm.pdf_combine(str(output_dir), str(source_dir), "combined.pdf")

        assert count == 1
        assert (output_dir / "combined.pdf").exists()

    def test_combine_multiple_pdfs(self, tmp_path, pypdf_available):
        """Test combining multiple PDFs."""
        # Create source directory with multiple PDFs
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        for i in range(3):
            self.create_test_pdf(source_dir / f"doc{i}.pdf", f"Document {i}")

        # Combine
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        count = iwfm.pdf_combine(str(output_dir), str(source_dir), "combined.pdf")

        assert count == 3
        assert (output_dir / "combined.pdf").exists()

    def test_combine_returns_correct_count(self, tmp_path, pypdf_available):
        """Test that combine returns correct file count."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        for i in range(5):
            self.create_test_pdf(source_dir / f"doc{i}.pdf", f"Document {i}")

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        count = iwfm.pdf_combine(str(output_dir), str(source_dir), "combined.pdf")

        assert count == 5

    def test_combine_empty_directory(self, tmp_path, pypdf_available):
        """Test combining from empty directory."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        count = iwfm.pdf_combine(str(output_dir), str(source_dir), "combined.pdf")

        assert count == 0

    def test_combine_ignores_non_pdf_files(self, tmp_path, pypdf_available):
        """Test that combine ignores non-PDF files."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # Create PDF and non-PDF files
        self.create_test_pdf(source_dir / "doc1.pdf", "Document 1")
        (source_dir / "readme.txt").write_text("Not a PDF")
        (source_dir / "data.csv").write_text("a,b,c")

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        count = iwfm.pdf_combine(str(output_dir), str(source_dir), "combined.pdf")

        assert count == 1

    def test_combine_creates_valid_pdf(self, tmp_path, pypdf_available):
        """Test that combined PDF is valid and readable."""
        import pypdf

        source_dir = tmp_path / "source"
        source_dir.mkdir()
        for i in range(2):
            self.create_test_pdf(source_dir / f"doc{i}.pdf", f"Document {i}")

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        count = iwfm.pdf_combine(str(output_dir), str(source_dir), "combined.pdf")

        # Verify combined PDF is readable
        combined_path = output_dir / "combined.pdf"
        with open(combined_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            # Combined PDF should have pages and be readable
            assert len(reader.pages) > 0
            # Should have at least as many pages as files combined
            assert len(reader.pages) >= count


# =============================================================================
# Integration tests for PDF workflow
# =============================================================================
class TestPdfWorkflow:
    """Integration tests for complete PDF workflows."""

    def test_complete_pdf_creation_workflow(self, tmp_path):
        """Test complete workflow: create, add pages, set font, add cells, save."""
        # Create PDF
        pdf = iwfm.pdf_create(layout='P', units='in', pagesize='Letter')

        # Add pages
        pdf = iwfm.pdf_addpages(pdf, pages=2)

        # Set font on first page (already on first page after addpages)
        # Need to go back to first page
        pdf.page = 1
        pdf = iwfm.pdf_setfont(pdf, font='Arial', style='B', size=16)

        # Add cell
        pdf = iwfm.pdf_cell(pdf, h=1, w=0, t='Title', b=0, a='C')

        # Save
        output_path = tmp_path / "complete_workflow.pdf"
        iwfm.pdf_save(pdf, str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_multi_page_document_with_content(self, tmp_path):
        """Test creating multi-page document with content on each page."""
        pdf = iwfm.pdf_create()

        for i in range(3):
            pdf.add_page()
            pdf = iwfm.pdf_setfont(pdf, font='Arial', style='B', size=20)
            pdf = iwfm.pdf_cell(pdf, h=1, w=0, t=f'Page {i + 1}', b=0, a='C')

        output_path = tmp_path / "multipage.pdf"
        iwfm.pdf_save(pdf, str(output_path))

        assert output_path.exists()

    def test_different_fonts_on_same_page(self, tmp_path):
        """Test using different fonts on the same page."""
        pdf = iwfm.pdf_create()
        pdf.add_page()

        # Title in bold Arial
        pdf = iwfm.pdf_setfont(pdf, font='Arial', style='B', size=24)
        pdf = iwfm.pdf_cell(pdf, t='Title')

        # Body in regular Times
        pdf = iwfm.pdf_setfont(pdf, font='Times', style='', size=12)
        pdf = iwfm.pdf_cell(pdf, t='Body text')

        # Footer in italic Courier
        pdf = iwfm.pdf_setfont(pdf, font='Courier', style='I', size=10)
        pdf = iwfm.pdf_cell(pdf, t='Footer')

        output_path = tmp_path / "fonts.pdf"
        iwfm.pdf_save(pdf, str(output_path))

        assert output_path.exists()
