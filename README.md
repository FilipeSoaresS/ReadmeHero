## Current version

`0.2.4` — rounded window shell, complete window controls, and theme-aware README preview colors.

# ReadMe Hero

A visual README builder for creating professional Markdown documents without having to learn Markdown first.

## V0.2

- Custom frameless application shell inspired by the ReadMe Hero / Steam Swapper window structure
- Dark and light themes
- English, Brazilian Portuguese, Spanish, Chinese and Japanese UI
- Visual block editor
- Live preview
- Image drag-and-drop
- Markdown export
- BEM-inspired component naming

## Run

```powershell
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install -r requirements.txt
python run.py
```

## Mermaid charts and diagrams

Use the Mermaid block to create charts and diagrams that export as native `mermaid` fenced blocks for GitHub rendering.

## GitHub Preview

Click **GitHub Preview** in the application header to open a separate live preview window styled after GitHub's README presentation.

The preview updates automatically as the document changes and follows the selected light/dark theme.

> Mermaid blocks are shown as Mermaid source inside the desktop preview. GitHub renders Mermaid diagrams on the published README itself.


## v0.2.15

- Remote HTTP/HTTPS images now render in the live preview and GitHub Preview.
- SVG icons such as Devicon are supported.
- External images are cached locally to avoid repeated downloads.
- Local project images continue to work normally.


## v0.2.16

Performance improvements:
- Remote images are downloaded asynchronously instead of blocking the UI thread.
- Remote image resources use a shared memory/disk cache.
- The editor coalesces rapid text changes before rebuilding the preview.
- Remote images render immediately from cache when available.
