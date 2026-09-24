#!/usr/bin/env python3
import hashlib
import io
import json
import shutil
import urllib.request
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources.json"
OUT = ROOT / "memes"
PREV = ROOT / "previews"
INDEX = ROOT / "source_index.json"
SIZE = 256
STATIC_FRAME_INDICES = [0, 5, 10, 15]

def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "blue-fat-fish-meme-pack-builder/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()

def remove_magenta(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    px = list(im.getdata())
    out = []
    for r, g, b, a in px:
        if r >= 238 and b >= 238 and g <= 35:
            out.append((255, 0, 255, 0))
        else:
            out.append((r, g, b, a))
    im.putdata(out)
    return im

def rgba_to_gif_frame(im: Image.Image) -> Image.Image:
    rgba = im.convert("RGBA")
    alpha = rgba.getchannel("A")
    rgb = Image.new("RGB", rgba.size, (255, 0, 255))
    rgb.paste(rgba, mask=alpha)
    pal = rgb.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    palette = pal.getpalette()
    palette += [0] * (768 - len(palette))
    palette[255*3:255*3+3] = [255, 0, 255]
    pal.putpalette(palette)
    mask = alpha.point(lambda a: 255 if a < 32 else 0)
    pal.paste(255, mask=mask)
    pal.info["transparency"] = 255
    pal.info["disposal"] = 2
    return pal

def split_sheet(sheet: Image.Image):
    w, h = sheet.size
    frames = []
    for row in range(4):
        for col in range(4):
            left = round(col * w / 4)
            top = round(row * h / 4)
            right = round((col + 1) * w / 4)
            bottom = round((row + 1) * h / 4)
            cell = sheet.crop((left, top, right, bottom))
            cell.thumbnail((SIZE, SIZE), Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
            x = (SIZE - cell.width) // 2
            y = (SIZE - cell.height) // 2
            canvas.alpha_composite(cell.convert("RGBA"), (x, y))
            frames.append(remove_magenta(canvas))
    return frames

def save_gif(frames, path: Path, duration: int):
    path.parent.mkdir(parents=True, exist_ok=True)
    gif_frames = [rgba_to_gif_frame(f) for f in frames]
    gif_frames[0].save(
        path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=duration,
        loop=0,
        disposal=2,
        transparency=255,
        optimize=False,
    )

def save_static_frames(item, frames):
    static_dir = OUT / item["category"] / "static"
    static_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(item["output"]).stem
    outputs = []
    for idx in STATIC_FRAME_INDICES:
        frame_no = idx + 1
        target = static_dir / f"{stem}-f{frame_no:02d}.png"
        frames[idx].save(target, format="PNG", optimize=True)
        outputs.append((idx, target))
    return outputs

def make_overview(frames, path: Path, cols: int, tile: int):
    if not frames:
        return
    rows = (len(frames) + cols - 1) // cols
    overview = Image.new("RGBA", (cols * tile, rows * tile), (255, 255, 255, 255))
    for i, frame in enumerate(frames):
        f = frame.copy()
        f.thumbnail((tile - 12, tile - 12), Image.Resampling.LANCZOS)
        x = (i % cols) * tile + (tile - f.width) // 2
        y = (i // cols) * tile + (tile - f.height) // 2
        overview.alpha_composite(f, (x, y))
    overview.convert("RGB").save(path, optimize=True)

def main():
    config = json.loads(SOURCES.read_text(encoding="utf-8"))
    PREV.mkdir(parents=True, exist_ok=True)

    # Remove only generated static subdirectories so stale PNGs do not survive source changes.
    if OUT.exists():
        for static_dir in OUT.glob("*/static"):
            if static_dir.is_dir():
                shutil.rmtree(static_dir)

    animated_entries = []
    static_entries = []
    animated_preview_frames = []
    static_preview_frames = []
    cover = None

    for item in config["sources"]:
        raw = download(item["source_url"])
        sha256 = hashlib.sha256(raw).hexdigest()
        sheet = Image.open(io.BytesIO(raw)).convert("RGBA")
        original_size = list(sheet.size)
        frames = split_sheet(sheet)

        animated_target = OUT / item["category"] / item["output"]
        save_gif(frames, animated_target, int(item.get("duration_ms", 100)))
        animated_preview_frames.append(frames[0].copy())

        if item["id"] == "wave":
            cover = frames[0].copy()

        animated_entries.append({
            "id": item["id"],
            "label": item["label"],
            "media_type": "animated",
            "category": item["category"],
            "output": animated_target.relative_to(ROOT).as_posix(),
            "source_url": item["source_url"],
            "source_path": item["source_path"],
            "author": item["author"],
            "upstream_repo": item["upstream_repo"],
            "license": item["license"],
            "modified": True,
            "source_sha256": sha256,
            "source_dimensions": original_size,
            "frames": len(frames),
            "output_size": [SIZE, SIZE],
            "duration_ms": int(item.get("duration_ms", 100)),
        })

        for idx, target in save_static_frames(item, frames):
            static_preview_frames.append(frames[idx].copy())
            static_entries.append({
                "id": f"{item['id']}-f{idx+1:02d}",
                "label": f"{item['label']} · 静态帧 {idx+1}",
                "media_type": "static",
                "category": item["category"],
                "output": target.relative_to(ROOT).as_posix(),
                "frame_index": idx + 1,
                "source_animation_id": item["id"],
                "source_url": item["source_url"],
                "source_path": item["source_path"],
                "author": item["author"],
                "upstream_repo": item["upstream_repo"],
                "license": item["license"],
                "modified": True,
                "source_sha256": sha256,
                "source_dimensions": original_size,
                "output_size": [SIZE, SIZE],
                "format": "png",
            })

    if cover:
        cover.save(PREV / "cover.png", optimize=True)

    make_overview(animated_preview_frames, PREV / "overview.png", cols=4, tile=192)
    make_overview(static_preview_frames, PREV / "static-overview.png", cols=6, tile=128)

    index = {
        "schema_version": 1,
        "generated": True,
        "generator": "scripts/build_memes.py",
        "summary": {
            "animated_count": len(animated_entries),
            "static_count": len(static_entries),
            "static_frames_per_source": len(STATIC_FRAME_INDICES),
            "static_frame_indices_1_based": [i + 1 for i in STATIC_FRAME_INDICES],
        },
        "upstream_attribution": {
            "author": "YunYueSama",
            "repo": "https://github.com/YunYueSama/codex-deepseek-pet",
            "license": "LICENSES/YunYueSama-Big-Fat-Fish-Attribution-1.0.txt",
        },
        "entries": animated_entries + static_entries,
    }
    INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"built {len(animated_entries)} animated memes and {len(static_entries)} static PNG memes")

if __name__ == "__main__":
    main()
