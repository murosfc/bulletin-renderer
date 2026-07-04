import json
import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "boletim.pdf"
OUTPUT_PATH = ROOT / "data" / "boletim.json"
IMAGES_DIR = ROOT / "assets" / "boletim-images"


def normalize(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = re.sub(r"\r", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def first_match(pattern: str, text: str, flags: int = 0) -> str:
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else ""


def split_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def image_type_from_bytes(data: bytes) -> str:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return "gif"
    if data.startswith(b"BM"):
        return "bmp"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "webp"
    if data.startswith((b"II*\x00", b"MM\x00*")):
        return "tif"
    return ""


def image_size_from_bytes(data: bytes, image_type: str) -> tuple[int, int]:
    try:
        if image_type == "png" and len(data) >= 24:
            width = int.from_bytes(data[16:20], "big")
            height = int.from_bytes(data[20:24], "big")
            return width, height

        if image_type == "gif" and len(data) >= 10:
            width = int.from_bytes(data[6:8], "little")
            height = int.from_bytes(data[8:10], "little")
            return width, height

        if image_type == "bmp" and len(data) >= 26:
            width = int.from_bytes(data[18:22], "little")
            height = int.from_bytes(data[22:26], "little")
            return abs(width), abs(height)

        if image_type == "jpg":
            i = 2
            size = len(data)
            while i < size - 9:
                if data[i] != 0xFF:
                    i += 1
                    continue
                marker = data[i + 1]
                i += 2
                if marker in (0xD8, 0xD9):
                    continue
                if i + 1 >= size:
                    break
                segment_length = int.from_bytes(data[i : i + 2], "big")
                if segment_length < 2 or i + segment_length > size:
                    break
                if marker in {
                    0xC0,
                    0xC1,
                    0xC2,
                    0xC3,
                    0xC5,
                    0xC6,
                    0xC7,
                    0xC9,
                    0xCA,
                    0xCB,
                    0xCD,
                    0xCE,
                    0xCF,
                }:
                    if i + 7 < size:
                        height = int.from_bytes(data[i + 3 : i + 5], "big")
                        width = int.from_bytes(data[i + 5 : i + 7], "big")
                        return width, height
                    break
                i += segment_length
    except Exception:
        return 0, 0

    return 0, 0


def is_logo_image(width: int, height: int, extension: str) -> bool:
    if width <= 0 or height <= 0:
        return False

    area = width * height
    ratio = max(width / height, height / width)

    if width <= 220 and height <= 220:
        return True
    if area <= 70000:
        return True
    if (height < 120 and width > 420) or (width < 120 and height > 420):
        return True
    if ratio >= 8 and area < 220000:
        return True

    # Logotipos vetoriais do rodape/cabecalho costumam vir como faixas PNG muito largas.
    if extension in {"png", "gif", "webp", "bmp"} and ratio >= 2.8 and width >= 1800 and height <= 1200:
        return True

    return False


def extract_article(page1: str) -> dict:
    lines = split_lines(page1)

    reference = ""
    ref_idx = -1
    for idx, line in enumerate(lines):
        if re.match(r"^[1-3]?[A-Za-zÀ-ÿ]+\s+\d+:\d+(?:-\d+)?$", line):
            reference = line
            ref_idx = idx
            break

    title = ""
    if ref_idx > 0:
        for idx in range(ref_idx - 1, max(-1, ref_idx - 8), -1):
            candidate = lines[idx]
            if len(candidate) >= 6 and candidate.upper() == candidate:
                title = candidate
                break

    if not title:
        title = first_match(r"\n([A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9 ?!]{8,})\n", page1)

    author = first_match(r"\n(Rev\.[^\n]+)$", page1, flags=re.MULTILINE)
    verse = first_match(r'"([^\"]*Con[^\"]+)"\s*\(([^\)]+)\)', page1)
    verse_ref = first_match(r'"[^\"]*Con[^\"]+"\s*\(([^\)]+)\)', page1)

    if not verse:
        verse = first_match(r'"([^\"]+)"\s*\((Provérbios[^\)]+)\)', page1)
        verse_ref = first_match(r'"[^\"]+"\s*\((Provérbios[^\)]+)\)', page1)

    body = ""
    if reference:
        ref_char_idx = page1.find(reference)
        if ref_char_idx != -1:
            body_candidate = page1[ref_char_idx + len(reference) :]
            if verse:
                verse_anchor = body_candidate.find('"' + verse + '"')
                if verse_anchor != -1:
                    body_candidate = body_candidate[:verse_anchor]
            if author:
                body_candidate = body_candidate.replace(author, "")
            body = normalize(body_candidate)

    return {
        "title": title,
        "reference": reference,
        "author": author,
        "body": body,
        "verse": verse,
        "verseReference": verse_ref,
    }


def extract_agenda_and_birthdays(page3: str) -> tuple[list[dict], list[str]]:
    lines = split_lines(page3)

    agenda = []
    birthdays = []

    day_pattern = re.compile(r"^(Domingo|Segunda|Terça|Quarta|Quinta|Sexta|Sábado).*", re.IGNORECASE)
    birthday_pattern = re.compile(r"^\d{2}/\d{2}\s*-\s*")

    current_day = None
    for line in lines:
        if day_pattern.match(line):
            current_day = {"day": line, "items": []}
            agenda.append(current_day)
            continue

        if birthday_pattern.match(line):
            birthdays.append(line)
            current_day = None
            continue

        if current_day and (line.startswith("08h") or line.startswith("9h") or line.startswith("10") or line.startswith("18h") or line.startswith("19h") or line.startswith("20h") or line.startswith("06h") or line.startswith("07h") or line.startswith("11h") or line.startswith("12h") or line.startswith("13h") or line.startswith("14h") or line.startswith("15h") or line.startswith("16h") or line.startswith("17h") or line.startswith("21h") or line.startswith("22h") or line.startswith("23h") or line.startswith("00h") or line.startswith("01h") or line.startswith("02h") or line.startswith("03h") or line.startswith("04h") or line.startswith("05h")):
            current_day["items"].append(line)

    if not birthdays:
        birthday_block = first_match(r"ANIVERSARIANTES(.*?)(?=CONSELHO|NOSSA CONTA|$)", page3, flags=re.DOTALL)
        if birthday_block:
            birthdays = split_lines(birthday_block)

    return agenda, birthdays


def extract_images(reader: PdfReader) -> list[dict]:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    for old_file in IMAGES_DIR.iterdir():
        if old_file.is_file():
            old_file.unlink()

    gallery = []
    valid_extensions = {"jpg", "jpeg", "png", "gif", "webp", "bmp", "tif", "tiff"}

    for page_idx, page in enumerate(reader.pages, start=1):
        try:
            page_images = list(page.images)
        except Exception:
            page_images = []

        for img_idx, image_file in enumerate(page_images, start=1):
            image_name = image_file.name or f"page{page_idx}_image{img_idx}.bin"
            raw_extension = image_name.rsplit(".", 1)[-1].lower() if "." in image_name else ""
            image_bytes = image_file.data

            detected_extension = image_type_from_bytes(image_bytes)
            extension = raw_extension if raw_extension in valid_extensions else detected_extension
            if extension == "jpeg":
                extension = "jpg"
            if extension == "tiff":
                extension = "tif"
            if extension not in valid_extensions:
                continue

            width, height = image_size_from_bytes(image_bytes, extension)
            if is_logo_image(width, height, extension):
                continue

            output_name = f"page-{page_idx:02d}-img-{img_idx:02d}.{extension}"
            output_path = IMAGES_DIR / output_name
            output_path.write_bytes(image_bytes)

            gallery.append(
                {
                    "src": f"assets/boletim-images/{output_name}",
                    "page": page_idx,
                    "name": image_name,
                    "width": width,
                    "height": height,
                }
            )

    return gallery


def compact_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def clip_text(text: str, limit: int = 360) -> str:
    text = compact_spaces(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def extract_prayer_requests(page3: str) -> str:
    block = first_match(
        r"Ore por esses irmãos:\s*(.*?)(?=(Domingo|Segunda|Terça|Quarta|Quinta|Sexta|Sábado)\s+\d{2}/\d{2}|$)",
        page3,
        flags=re.DOTALL,
    )
    return compact_spaces(block)


def extract_finance_info(page3: str) -> str:
    pix = first_match(r"(PIX:\s*[^\n]+)", page3)
    return compact_spaces(pix)


def build_news_blocks(
    article: dict,
    community_summary: str,
    agenda: list[dict],
    birthdays: list[str],
    prayer_requests: str,
    finance_info: str,
    image_count: int,
) -> list[dict]:
    blocks: list[dict] = []

    if article.get("title"):
        blocks.append(
            {
                "type": "featured",
                "title": article["title"],
                "subtitle": article.get("reference", ""),
                "content": article.get("body", ""),
                "priority": 100,
            }
        )

    if community_summary:
        blocks.append(
            {
                "type": "community",
                "title": "Vida em Comunidade",
                "subtitle": "Comunhão",
                "content": community_summary,
                "priority": 85,
            }
        )

    if agenda:
        agenda_lines = []
        for day in agenda[:3]:
            items = ", ".join(day.get("items", [])[:2])
            if items:
                agenda_lines.append(f"{day.get('day', '').strip()}: {items}")
        agenda_text = " | ".join(agenda_lines)
        blocks.append(
            {
                "type": "agenda",
                "title": "Agenda da Semana",
                "subtitle": "Programação",
                "content": agenda_text,
                "priority": 80,
            }
        )

    if birthdays:
        blocks.append(
            {
                "type": "birthdays",
                "title": "Aniversariantes",
                "subtitle": "Celebração",
                "content": "; ".join(birthdays),
                "priority": 75,
            }
        )

    if prayer_requests:
        blocks.append(
            {
                "type": "prayer",
                "title": "Pedidos de Oração",
                "subtitle": "Intercessão",
                "content": prayer_requests,
                "priority": 70,
            }
        )

    if finance_info:
        blocks.append(
            {
                "type": "finance",
                "title": "Contribuição e Conta",
                "subtitle": "Serviço",
                "content": finance_info,
                "priority": 60,
            }
        )

    blocks.append(
        {
            "type": "visual",
            "title": "Recortes do Boletim",
            "subtitle": "Visual",
            "content": f"{image_count} imagens extraídas automaticamente do PDF.",
            "priority": 55,
        }
    )

    blocks.sort(key=lambda item: item.get("priority", 0), reverse=True)
    return blocks


def extract_identity(page1: str) -> dict:
    lines = split_lines(page1)

    values: list[str] = []
    current_value = ""
    in_values_block = False
    for raw_line in lines:
        line = raw_line.strip()
        if "AINDA NÃO TENDES FÉ?" in line:
            if current_value:
                values.append(current_value.strip())
            break

        if line.startswith("•"):
            in_values_block = True
            if current_value:
                values.append(current_value.strip())
            current_value = line.lstrip("•").strip()
            continue

        if in_values_block and current_value:
            if re.match(r"^[A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9 ]{6,}$", line):
                values.append(current_value.strip())
                current_value = ""
                in_values_block = False
            else:
                current_value = f"{current_value} {line}".strip()

    if current_value:
        values.append(current_value.strip())

    vision = ""
    mission = ""

    if "NOSSA VISÃO" in page1:
        vision = first_match(r"NOSSA VISÃO\s*(.*?)\s*NOSSA MISSÃO", page1, flags=re.DOTALL)
    if "NOSSA MISSÃO" in page1:
        mission = first_match(r"NOSSA MISSÃO\s*(.*?)\s*AINDA NÃO TENDES FÉ\?", page1, flags=re.DOTALL)

    return {
        "vision": compact_spaces(vision) if vision else "",
        "mission": compact_spaces(mission) if mission else "",
        "values": values,
    }


def build_editorial_sections(
    article: dict,
    community_summary: str,
    agenda: list[dict],
    birthdays: list[str],
    prayer_requests: str,
    finance_info: str,
    identity: dict,
    image_gallery: list[dict],
) -> list[dict]:
    sections: list[dict] = []

    sections.append(
        {
            "id": "manchete",
            "title": "Manchete da Semana",
            "kicker": article.get("reference", "Mensagem"),
            "news": [
                {
                    "title": article.get("title", "Mensagem Principal"),
                    "summary": article.get("body", ""),
                    "meta": article.get("author", ""),
                    "highlight": True,
                }
            ],
        }
    )

    comunidade_news = []
    if community_summary:
        comunidade_news.append(
            {
                "title": "Vida em Comunidade",
                    "summary": community_summary,
                "meta": "Comunhão",
            }
        )
    if identity.get("mission"):
        comunidade_news.append(
            {
                "title": "Nossa Missão",
                "summary": identity["mission"],
                "meta": "Identidade",
            }
        )
    if identity.get("vision"):
        comunidade_news.append(
            {
                "title": "Nossa Visão",
                "summary": identity["vision"],
                "meta": "Identidade",
            }
        )
    if identity.get("values"):
        comunidade_news.append(
            {
                "title": "Valores em Destaque",
                "summary": "",
                "meta": "Princípios",
                "bullets": identity["values"],
            }
        )

    if comunidade_news:
        sections.append(
            {
                "id": "comunidade",
                "title": "Comunidade e Propósito",
                "kicker": "Vida da Igreja",
                "news": comunidade_news,
            }
        )

    agenda_news = []
    for day in agenda:
        agenda_news.append(
            {
                "title": day.get("day", "Programação"),
                "summary": "",
                "meta": "Agenda",
                "bullets": day.get("items", []),
            }
        )

    if birthdays:
        agenda_news.append(
            {
                "title": "Aniversariantes",
                "summary": "",
                "meta": "Celebração",
                "bullets": birthdays,
            }
        )

    if agenda_news:
        sections.append(
            {
                "id": "agenda",
                "title": "Agenda e Celebrações",
                "kicker": "Semana",
                "news": agenda_news,
            }
        )

    cuidado_news = []
    if prayer_requests:
        cuidado_news.append(
            {
                "title": "Pedidos de Oração",
                    "summary": prayer_requests,
                "meta": "Intercessão",
            }
        )
    if finance_info:
        cuidado_news.append(
            {
                "title": "Contribuição",
                "summary": finance_info,
                "meta": "Conta da Igreja",
            }
        )

    if cuidado_news:
        sections.append(
            {
                "id": "cuidado",
                "title": "Cuidado e Serviço",
                "kicker": "Ação Pastoral",
                "news": cuidado_news,
            }
        )

    sections.append(
        {
            "id": "mural",
            "title": "Mural Visual",
            "kicker": "Imagens",
            "news": [
                {
                    "title": "Recortes do Boletim",
                    "summary": f"{len(image_gallery)} imagens incorporadas foram encontradas e exibidas no mural visual.",
                    "meta": "Galeria",
                }
            ],
        }
    )

    return sections


def main() -> None:
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {PDF_PATH}")

    reader = PdfReader(str(PDF_PATH))
    pages = [normalize(page.extract_text() or "") for page in reader.pages]

    page1 = pages[0] if pages else ""
    page2 = pages[1] if len(pages) > 1 else ""
    page3 = pages[2] if len(pages) > 2 else ""

    issue = first_match(r"N[oº]\s*(\d+)", page1)
    date_line = first_match(r"(Domingo,?\s*\d{2}\s*de\s*[A-Za-zçÇ]+\s*de\s*\d{4})", page1)

    opening_hours = []
    for marker in ["Escola Bíblica Dominical", "Cultos às", "Durante a semana", "Aos Domingos"]:
        m = re.search(rf"({re.escape(marker)}[^\n]*)", page1)
        if m:
            opening_hours.append(m.group(1).strip())

    article = extract_article(page1)
    agenda, birthdays = extract_agenda_and_birthdays(page3)
    image_gallery = extract_images(reader)
    prayer_requests = extract_prayer_requests(page3)
    finance_info = extract_finance_info(page3)
    news_blocks = build_news_blocks(
        article=article,
        community_summary=normalize(page2),
        agenda=agenda,
        birthdays=birthdays,
        prayer_requests=prayer_requests,
        finance_info=finance_info,
        image_count=len(image_gallery),
    )
    identity = extract_identity(page1)
    editorial_sections = build_editorial_sections(
        article=article,
        community_summary=normalize(page2),
        agenda=agenda,
        birthdays=birthdays,
        prayer_requests=prayer_requests,
        finance_info=finance_info,
        identity=identity,
        image_gallery=image_gallery,
    )

    data = {
        "meta": {
            "title": "Boletim Semanal",
            "issue": issue,
            "date": date_line,
            "pdfFile": "boletim.pdf",
            "generatedBy": "scripts/generate_boletim_json.py",
        },
        "hero": {
            "kicker": "Vida em comunidade",
            "headline": article["title"] or "Boletim Semanal",
            "subheadline": article["reference"] or "Mensagem da semana",
            "highlights": opening_hours,
        },
        "article": article,
        "community": {
            "summary": normalize(page2),
        },
        "identity": identity,
        "newsBlocks": news_blocks,
        "editorialSections": editorial_sections,
        "imageGallery": image_gallery,
        "agenda": agenda,
        "birthdays": birthdays,
        "contactsAndLeadership": split_lines(page3),
        "rawPages": pages,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"JSON gerado em: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
