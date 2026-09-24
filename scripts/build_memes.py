#!/usr/bin/env python3
import hashlib
import io
import json
import os
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources.json"
OUT = ROOT / "memes"
PREV = ROOT / "previews"
INDEX = ROOT / "source_index.json"
SIZE = 256

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
    if w % 4 or h % 4:
        raise ValueError(f"sheet must be divisible by 4x4, got {w}x{h}")
    cw, ch = w // 4, h // 4
    frames = []
    for row in range(4):
        for col in range(4):
            cell = sheet.crop((col*cw, row*ch, (col+1)*cw, (row+1)*ch))
            cell.thumbnail((SIZE, SIZE), Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", (SIZE, SIZE), (0,0,0,0))
            x = (SIZE-cell.width)//2
            y = (SIZE-cell.height)//2
            canvas.alpha_composite(cell.convert("RGBA"), (x,y))
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

def main():
    config = json.loads(SOURCES.read_text(encoding="utf-8"))
    PREV.mkdir(parents=True, exist_ok=True)
    entries = []
    first_frames = []
    cover = None

    for item in config["sources"]:
        raw = download(item["source_url"])
        sha256 = hashlib.sha256(raw).hexdigest()
        sheet = Image.open(io.BytesIO(raw)).convert("RGBA")
        original_size = list(sheet.size)
        frames = split_sheet(sheet)
        target = OUT / item["category"] / item["output"]
        save_gif(frames, target, int(item.get("duration_ms", 100)))
        first_frames.append((item["label"], frames[0].copy()))
        if item["id"] == "wave":
            cover = frames[0].copy()
        entries.append({
            "id": item["id"],
            "label": item["label"],
            "category": item["category"],
            "output": target.relative_to(ROOT).as_posix(),
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

    if cover:
        cover.save(PREV / "cover.png")

    cols = 4
    tile = 192
    rows = (len(first_frames) + cols - 1) // cols
    overview = Image.new("RGBA", (cols*tile, rows*tile), (255,255,255,255))
    for i, (_, frame) in enumerate(first_frames):
        f = frame.copy()
        f.thumbnail((tile-12, tile-12), Image.Resampling.LANCZOS)
        x = (i % cols)*tile + (tile-f.width)//2
        y = (i // cols)*tile + (tile-f.height)//2
        overview.alpha_composite(f, (x,y))
    overview.convert("RGB").save(PREV / "overview.png", optimize=True)

    index = {
        "schema_version": 1,
        "generated": True,
        "generator": "scripts/build_memes.py",
        "upstream_attribution": {
            "author": "YunYueSama",
            "repo": "https://github.com/YunYueSama/codex-deepseek-pet",
            "license": "LICENSES/YunYueSama-Big-Fat-Fish-Attribution-1.0.txt"
        },
        "entries": entries
    }
    INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"built {len(entries)} animated memes")

if __name__ == "__main__":
    main()
