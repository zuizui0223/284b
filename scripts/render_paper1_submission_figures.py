#!/usr/bin/env python3
"""Render Paper 1 SVG figures at Ecology Letters full-page width for visual QA.

This is a production-only helper. It does not alter any scientific values.
It reports the equivalent physical text/stroke sizes at 173 mm and renders
PNG previews at 300 dpi plus a contact sheet for human inspection.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "manuscript" / "figures"
OUT = ROOT / "artifacts" / "paper1_figure_qa"

FIGURES = [
    (1, FIG_DIR / "figure1_relation_endpoint_contract_v0_2.svg"),
    (2, FIG_DIR / "figure2_level_a_empirical_anchor_v0_2.svg"),
    (3, FIG_DIR / "figure3_relation_layer_and_event_function_v0_2.svg"),
    (4, FIG_DIR / "figure4_parallel_openability_audits_v0_1.svg"),
    (5, FIG_DIR / "figure5_invalid_state_decomposition_v0_3.svg"),
]

PHYSICAL_WIDTH_MM = 173.0
DPI = 300
TARGET_PX = round(PHYSICAL_WIDTH_MM / 25.4 * DPI)
PHYSICAL_WIDTH_PT = PHYSICAL_WIDTH_MM / 25.4 * 72.0


def _num(value: str | None) -> float | None:
    if value is None:
        return None
    m = re.match(r"^-?\d+(?:\.\d+)?", value)
    return float(m.group(0)) if m else None


def inspect_svg(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    root = ET.fromstring(text)
    viewbox = root.attrib.get("viewBox")
    if not viewbox:
        raise ValueError(f"missing viewBox: {path}")
    _, _, vb_w, vb_h = [float(x) for x in viewbox.split()]

    font_sizes = [float(x) for x in re.findall(r"font-size:([0-9.]+)px", text)]
    stroke_widths = [float(x) for x in re.findall(r"stroke-width:([0-9.]+)", text)]
    if not font_sizes:
        raise ValueError(f"no CSS pixel font sizes found: {path}")

    unit_to_pt = PHYSICAL_WIDTH_PT / vb_w
    min_font = min(font_sizes)
    min_stroke = min(stroke_widths) if stroke_widths else None
    return {
        "file": path.name,
        "viewbox_width": vb_w,
        "viewbox_height": vb_h,
        "physical_width_mm": PHYSICAL_WIDTH_MM,
        "target_pixel_width_at_300dpi": TARGET_PX,
        "min_css_font_px": min_font,
        "min_font_pt_at_173mm": round(min_font * unit_to_pt, 3),
        "font_sizes_px": sorted(set(font_sizes)),
        "font_sizes_pt_at_173mm": [round(x * unit_to_pt, 3) for x in sorted(set(font_sizes))],
        "min_stroke_units": min_stroke,
        "min_stroke_pt_at_173mm": round(min_stroke * unit_to_pt, 3) if min_stroke is not None else None,
    }


def render_svg(path: Path, out_path: Path) -> None:
    cairosvg.svg2png(
        bytestring=path.read_bytes(),
        write_to=str(out_path),
        output_width=TARGET_PX,
    )


def make_contact_sheet(paths: list[Path], out_path: Path) -> None:
    images = [Image.open(p).convert("RGB") for p in paths]
    thumb_w = 1050
    margin = 50
    label_h = 55
    thumbs = []
    for i, image in enumerate(images, 1):
        ratio = thumb_w / image.width
        thumb = image.resize((thumb_w, round(image.height * ratio)))
        thumbs.append((i, thumb))
    total_h = margin + sum(label_h + im.height + margin for _, im in thumbs)
    sheet = Image.new("RGB", (thumb_w + margin * 2, total_h), "white")
    draw = ImageDraw.Draw(sheet)
    y = margin
    for i, im in thumbs:
        draw.text((margin, y), f"Figure {i} — 173 mm rendering preview", fill="black")
        y += label_h
        sheet.paste(im, (margin, y))
        y += im.height + margin
    sheet.save(out_path)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    metrics = []
    pngs = []
    for num, path in FIGURES:
        metrics.append(inspect_svg(path))
        out = OUT / f"figure{num}_173mm_300dpi.png"
        render_svg(path, out)
        pngs.append(out)
    (OUT / "physical_size_metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    make_contact_sheet(pngs, OUT / "contact_sheet_173mm.png")
    for row in metrics:
        print(
            f"{row['file']}: min font {row['min_css_font_px']} px -> "
            f"{row['min_font_pt_at_173mm']} pt at {PHYSICAL_WIDTH_MM:.0f} mm"
        )


if __name__ == "__main__":
    main()
