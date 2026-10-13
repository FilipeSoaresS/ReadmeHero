from pathlib import Path
import shutil


SUPPORTED_IMAGE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"
}


def is_image_file(path: str) -> bool:
    return Path(path).suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS


def copy_image_to_assets(source: str, project_dir: str) -> str:
    source_path = Path(source)
    assets_dir = Path(project_dir) / "assets" / "images"
    assets_dir.mkdir(parents=True, exist_ok=True)

    destination = assets_dir / source_path.name

    counter = 1
    while destination.exists():
        destination = assets_dir / f"{source_path.stem}_{counter}{source_path.suffix}"
        counter += 1

    shutil.copy2(source_path, destination)

    return str(Path("assets") / "images" / destination.name).replace("\\", "/")
