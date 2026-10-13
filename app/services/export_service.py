from pathlib import Path


def export_document(markdown: str, output_dir: str):
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    readme_path = directory / "README.md"
    readme_path.write_text(markdown, encoding="utf-8")

    return readme_path
