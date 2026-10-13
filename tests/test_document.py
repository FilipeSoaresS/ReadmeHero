from app.core.document import Document
from app.core.blocks import HeadingBlock, ParagraphBlock


def test_document_generates_markdown():
    document = Document()
    document.add_block(HeadingBlock("Project", 1))
    document.add_block(ParagraphBlock("A description."))

    assert document.to_markdown() == "# Project\n\nA description."
