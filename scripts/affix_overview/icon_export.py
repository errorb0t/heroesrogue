from __future__ import annotations

import subprocess
from pathlib import Path
from shutil import which

from .icon_names import icon_file_name

try:
    from PIL import Image
except ImportError:  # pragma: no cover - exercised only when Pillow is absent.
    Image = None  # type: ignore[assignment]


def needs_export(source_path: Path, target_path: Path) -> bool:
    if not target_path.exists():
        return True
    return source_path.stat().st_mtime_ns > target_path.stat().st_mtime_ns


def export_with_pillow(source_path: Path, target_path: Path) -> None:
    with Image.open(source_path) as image:
        image.save(target_path, format="PNG")


def export_with_magick(source_path: Path, target_path: Path) -> None:
    magick_binary = which("magick")
    if magick_binary is not None:
        command = [magick_binary, str(source_path), str(target_path)]
    else:
        convert_binary = which("convert")
        if convert_binary is None:
            raise RuntimeError(
                "DDS conversion requires Pillow or ImageMagick (`magick`/`convert`)."
            )
        command = [convert_binary, str(source_path), str(target_path)]

    subprocess.run(command, check=True)


def export_texture_icons(source_dir: Path, output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)

    exported = 0
    for source_path in sorted(source_dir.glob("*.dds")):
        target_path = output_dir / icon_file_name(source_path)
        if not needs_export(source_path, target_path):
            continue

        if Image is not None:
            export_with_pillow(source_path, target_path)
        else:
            export_with_magick(source_path, target_path)

        exported += 1

    return exported
