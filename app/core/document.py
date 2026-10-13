from app.core.blocks import MarkdownBlock


class Document:
    """Document model independent from the graphical interface."""

    def __init__(self):
        self.blocks: list[MarkdownBlock] = []

    def add_block(self, block: MarkdownBlock, index: int | None = None):
        if index is None:
            self.blocks.append(block)
        else:
            self.blocks.insert(index, block)

    def remove_block(self, index: int):
        if 0 <= index < len(self.blocks):
            self.blocks.pop(index)

    def move_block(self, old_index: int, new_index: int):
        if not (0 <= old_index < len(self.blocks)):
            return
        new_index = max(0, min(new_index, len(self.blocks) - 1))
        block = self.blocks.pop(old_index)
        self.blocks.insert(new_index, block)

    def to_markdown(self) -> str:
        return "\n\n".join(
            block.to_markdown()
            for block in self.blocks
            if block.to_markdown().strip()
        )

    def to_html_blocks(self) -> str:
        return "\n".join(
            block.to_html()
            for block in self.blocks
            if block.to_markdown().strip()
        )
