#!/usr/bin/env python3
import hashlib
import io
import json
import shutil
import urllib.request
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ANIM_SOURCES = ROOT / "sources.json"
STATIC_SOURCES = ROOT / "static_sources.json"
OUT = ROOT / "memes"
PREV = ROOT / "previews"
INDEX = ROOT / "source_index.json"
SIZE = 256

def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent":"blue-fat-fish-meme-pack-builder/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()

def remove_magenta(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    px = list(im.getdata())
    out = []
    for r,g,b,a in px:
        if r >= 238 and b >= 238 and g <= 35:
            out.append((255,0,255,0))
        else:
            out.append((r,g,b,a))
    im.putdata(out)
    return im

def rgba_to_gif_frame(im: Image.Image) -> Image.Image:
    rgba = im.convert("RGBA")
    alpha = rgba.getchannel("A")
    rgb = Image.new("RGB", rgba.size, (255,0,255))
    rgb.paste(rgba, mask=alpha)
    pal = rgb.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    palette = pal.getpalette()
    palette += [0] * (768 - len(palette))
    palette[255*3:255*3+3] = [255,0,255]
    pal.putpalette(palette)
    mask = alpha.point(lambda a: 255 if a < 32 else 0)
    pal.paste(255, mask=mask)
    pal.info["transparency"] = 255
    pal.info["disposal"] = 2
    return pal

def split_sheet(sheet: Image.Image):
    w,h = sheet.size
    frames=[]
    for row in range(4):
        for col in range(4):
            left=round(col*w/4); top=round(row*h/4)
            right=round((col+1)*w/4); bottom=round((row+1)*h/4)
            cell=sheet.crop((left,top,right,bottom))
            cell.thumbnail((SIZE,SIZE), Image.Resampling.LANCZOS)
            canvas=Image.new("RGBA",(SIZE,SIZE),(0,0,0,0))
            canvas.alpha_composite(cell.convert("RGBA"),((SIZE-cell.width)//2,(SIZE-cell.height)//2))
            frames.append(remove_magenta(canvas))
    return frames

def save_gif(frames,path:Path,duration:int):
    path.parent.mkdir(parents=True,exist_ok=True)
    g=[rgba_to_gif_frame(f) for f in frames]
    g[0].save(path,save_all=True,append_images=g[1:],duration=duration,loop=0,disposal=2,transparency=255,optimize=False)

def make_overview(images,path:Path,cols:int,tile:int):
    if not images: return
    rows=(len(images)+cols-1)//cols
    canvas=Image.new("RGB",(cols*tile,rows*tile),(255,255,255))
    for i,img in enumerate(images):
        f=img.convert("RGBA")
        f.thumbnail((tile-12,tile-12),Image.Resampling.LANCZOS)
        bg=Image.new("RGBA",(tile,tile),(255,255,255,255))
        bg.alpha_composite(f,((tile-f.width)//2,(tile-f.height)//2))
        canvas.paste(bg.convert("RGB"),((i%cols)*tile,(i//cols)*tile))
    canvas.save(path,optimize=True)

def main():
    anim_cfg=json.loads(ANIM_SOURCES.read_text(encoding="utf-8"))
    static_cfg=json.loads(STATIC_SOURCES.read_text(encoding="utf-8"))
    PREV.mkdir(parents=True,exist_ok=True)

    # 清掉旧的“动画抽帧静态图”，再写入真正独立静态作品。
    if OUT.exists():
        for d in OUT.glob("*/static"):
            if d.is_dir():
                shutil.rmtree(d)

    animated_entries=[]
    static_entries=[]
    animated_preview=[]
    static_preview=[]
    cover=None

    for item in anim_cfg["sources"]:
        raw=download(item["source_url"])
        src_sha=hashlib.sha256(raw).hexdigest()
        sheet=Image.open(io.BytesIO(raw)).convert("RGBA")
        frames=split_sheet(sheet)
        target=OUT/item["category"]/item["output"]
        save_gif(frames,target,int(item.get("duration_ms",100)))
        animated_preview.append(frames[0].copy())
        if item["id"]=="wave": cover=frames[0].copy()
        animated_entries.append({
            "id":item["id"],"label":item["label"],"media_type":"animated",
            "category":item["category"],"output":target.relative_to(ROOT).as_posix(),
            "source_url":item["source_url"],"source_path":item["source_path"],
            "author":item["author"],"upstream_repo":item["upstream_repo"],
            "license":item["license"],"modified":True,
            "source_sha256":src_sha,"frames":len(frames),"output_size":[SIZE,SIZE]
        })

    for item in static_cfg["sources"]:
        raw=download(item["source_url"])
        src_sha=hashlib.sha256(raw).hexdigest()
        target=OUT/item["category"]/item["output"]
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(raw)
        img=Image.open(io.BytesIO(raw))
        static_preview.append(img.copy())
        static_entries.append({
            "id":item["id"],"label":item["label"],"media_type":"static-independent",
            "category":item["category"],"output":target.relative_to(ROOT).as_posix(),
            "source_url":item["source_url"],"original_url":item["original_url"],
            "metadata_url":item["metadata_url"],"author":item["author"],
            "submitter":item["submitter"],"origin":item["origin"],
            "license":item["license"],"license_note":item["license_note"],
            "tags":item.get("tags",[]),"source_sha256":src_sha,
            "source_dimensions":list(img.size),"format":img.format.lower() if img.format else "webp"
        })

    if cover: cover.save(PREV/"cover.png",optimize=True)
    make_overview(animated_preview,PREV/"overview.png",4,192)
    make_overview(static_preview,PREV/"static-overview.png",4,220)

    index={
        "schema_version":1,"generated":True,"generator":"scripts/build_memes.py",
        "summary":{"animated_count":len(animated_entries),"independent_static_count":len(static_entries)},
        "notes":[
            "静态区只收独立静态作品，不再使用动画抽帧。",
            "当前独立静态首批均为上游清单明确标记 CC0 的 DeepSeek/蓝色大肥鱼投稿。"
        ],
        "entries":animated_entries+static_entries
    }
    INDEX.write_text(json.dumps(index,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"built {len(animated_entries)} animated memes and {len(static_entries)} independent static memes")

if __name__=="__main__":
    main()
