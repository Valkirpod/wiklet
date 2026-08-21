import re
from pathlib import Path

def slugify(name: str) -> str:
    slug = name.lower().replace(" ", "-")
    slug = re.sub(r'[<>:"/\\|?*]', '', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug or "unnamed"

def unique_slug(name: str, directory: Path, extension: str = "") -> str:
    base = slugify(name)
    candidate = base
    counter = 1
    
    while (directory / f"{candidate}{extension}").exists():
        candidate = f"{base}-{counter}"
        counter += 1

    return candidate