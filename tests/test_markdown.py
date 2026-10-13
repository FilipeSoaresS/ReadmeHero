from app.core.blocks import HeadingBlock, ParagraphBlock, ImageBlock


def test_heading_markdown():
    block = HeadingBlock("ReadMe Hero", 1)
    assert block.to_markdown() == "# ReadMe Hero"


def test_paragraph_markdown():
    block = ParagraphBlock("Hello world")
    assert block.to_markdown() == "Hello world"


def test_image_markdown():
    block = ImageBlock("assets/images/demo.png", "Demo image")
    assert block.to_markdown() == "![Demo image](assets/images/demo.png)"
