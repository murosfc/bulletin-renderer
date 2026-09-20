import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"::error::{message}")
    raise SystemExit(1)


def main() -> None:
    pdf_path = ROOT / "boletim.pdf"
    json_path = ROOT / "data" / "boletim.json"
    html_path = ROOT / "index.html"

    if not pdf_path.is_file() or pdf_path.stat().st_size < 5:
        fail("boletim.pdf ausente ou vazio")
    if pdf_path.read_bytes()[:5] != b"%PDF-":
        fail("boletim.pdf nao possui assinatura PDF valida")

    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"data/boletim.json invalido: {exc}")

    for path in ("meta.issue", "meta.date", "hero.headline", "article.body"):
        value = data
        for key in path.split("."):
            value = value.get(key) if isinstance(value, dict) else None
        if not value:
            fail(f"campo obrigatorio ausente ou vazio: {path}")

    html = html_path.read_text(encoding="utf-8")
    references = set(re.findall(r"(?:src|data-src)=\"([^\"]+)\"", html))
    missing = [reference for reference in references if not reference.startswith(("http://", "https://", "data:")) and not (ROOT / reference).is_file()]
    if missing:
        fail("assets referenciados e ausentes: " + ", ".join(sorted(missing)))

    gallery = data.get("imageGallery", [])
    if not gallery:
        fail("imageGallery vazio: nenhuma imagem foi extraida")
    for image in gallery:
        source = image.get("src", "")
        if not source or not (ROOT / source).is_file():
            fail(f"imagem da galeria ausente: {source or '<sem src>'}")

    print(f"Validacao concluida: edicao {data['meta']['issue']}, {len(gallery)} imagens.")


if __name__ == "__main__":
    main()