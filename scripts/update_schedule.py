#!/usr/bin/env python3
"""
Genera y actualiza programacion-semanal.json combinando:
- Semanas históricas (octubre 2026) con etiqueta source="TORRES" (y ODS02 en 05-10 a 11-10)
- Programación trisemanal de noviembre 2026 desde los 3 archivos Excel:
  * Torres (Consorcio Windpeshi) -> source="TORRES"
  * ODS001 (Consorcio IIWA KAI) -> source="ODS01"
  * ODS002 (Consorcio IIWA KAI) -> source="ODS02"
"""

import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / "programacion-semanal.json"
TORRES_GEOJSON = BASE_DIR / "geojson" / "Torres.geojson"
AEROS_GEOJSON = BASE_DIR / "geojson" / "Aerogeneradores.geojson"

UPLOADED_DIR = Path(
    "/Users/efrainlav/.gemini/antigravity/brain/6a739d63-2b9b-4351-a029-bd1f21e524f7/.user_uploaded"
)
FILE_TORRES = UPLOADED_DIR / "media_1794582282735_d24acb66.xlsx"
FILE_ODS01 = UPLOADED_DIR / "media_1794582283159_706d7416.xlsx"
FILE_ODS02 = UPLOADED_DIR / "media_1794582283173_be4f9579.xlsx"

DAY_META = [
    ("monday", "Lunes", ["lunes"]),
    ("tuesday", "Martes", ["martes"]),
    ("wednesday", "Miércoles", ["miércoles", "miercoles"]),
    ("thursday", "Jueves", ["jueves"]),
    ("friday", "Viernes", ["viernes"]),
    ("saturday", "Sábado", ["sábado", "sabado"]),
]


def col_to_idx(col_str: str) -> int:
    res = 0
    for ch in col_str:
        res = res * 26 + (ord(ch) - ord("A") + 1)
    return res


def parse_ref(ref: str) -> tuple[int, int]:
    m = re.match(r"([A-Z]+)(\d+)", ref)
    return col_to_idx(m.group(1)), int(m.group(2))


def clean_text(text: str) -> str:
    if not text:
        return ""
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return " · ".join(lines)


def load_xlsx_sheets(path: Path) -> dict[str, dict[tuple[int, int], str]]:
    ns = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    sheets: dict[str, dict[tuple[int, int], str]] = {}
    with zipfile.ZipFile(path) as z:
        strings: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            sst = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in sst.findall("main:si", ns):
                texts = [
                    t.text or ""
                    for t in si.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")
                ]
                strings.append("".join(texts))

        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rel_map = {r.attrib["Id"]: r.attrib["Target"] for r in rels}

        for sh in wb.find("main:sheets", ns):
            name = sh.attrib["name"]
            rid = sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            target = "xl/" + rel_map[rid].lstrip("/")
            ws = ET.fromstring(z.read(target))
            grid: dict[tuple[int, int], str] = {}
            for c in ws.findall(".//main:c", ns):
                ref = c.attrib.get("r")
                if not ref:
                    continue
                t = c.attrib.get("t")
                v = c.find("main:v", ns)
                is_el = c.find("main:is", ns)
                val = ""
                if v is not None and v.text is not None:
                    val = strings[int(v.text)] if t == "s" else v.text
                elif is_el is not None:
                    val = "".join(
                        x.text or ""
                        for x in is_el.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")
                    )
                if val != "":
                    col, row = parse_ref(ref)
                    grid[(row, col)] = val.strip()

            for m in ws.findall(".//main:mergeCell", ns):
                s, e = m.attrib["ref"].split(":")
                c1, r1 = parse_ref(s)
                c2, r2 = parse_ref(e)
                base_val = grid.get((r1, c1), "")
                if base_val:
                    for r in range(r1, r2 + 1):
                        for c in range(c1, c2 + 1):
                            grid[(r, c)] = base_val
            sheets[name] = grid
    return sheets


def parse_sheet_blocks(grid: dict[tuple[int, int], str], source: str) -> dict[str, dict]:
    """
    Extrae actividades, torres, ocupaciones y aerogeneradores por día (monday..saturday)
    para una hoja de programación semanal.
    """
    header_row = None
    label_col = None
    day_cols: dict[str, int] = {}

    for r in range(1, 15):
        row_days: dict[str, int] = {}
        found_desc = None
        for c in range(1, 45):
            val = grid.get((r, c), "").strip().lower()
            if val in ("descripción", "descripcion") and found_desc is None:
                found_desc = c
            for key, _, aliases in DAY_META:
                if val in aliases and key not in row_days:
                    row_days[key] = c
        if len(row_days) >= 5:
            header_row = r
            label_col = found_desc or 4
            day_cols = row_days
            break

    if header_row is None:
        raise ValueError(f"No se encontró fila de días en hoja ({source})")

    # Identificar bloques por cada "Frente trabajo ..." / "Area de entorno"
    blocks = []
    current = None
    max_row = max((r for r, _ in grid.keys()), default=header_row)

    for r in range(header_row + 1, max_row + 1):
        # Buscar texto de etiqueta en columnas 1..label_col
        lbl = ""
        for col_try in [label_col, 2, 1, 3, 4, 5]:
            candidate = grid.get((r, col_try), "").strip()
            if candidate:
                lbl = candidate
                break

        upper_lbl = lbl.upper()
        if "RECURSOS HUMANOS" in upper_lbl or "EQUIPOS Y MAQUINARIA" in upper_lbl:
            break

        is_front_header = (
            upper_lbl.startswith("FRENTE")
            or upper_lbl.startswith("AREA DE ENTORNO")
            or upper_lbl.startswith("ÁREA DE ENTORNO")
        )
        if is_front_header:
            if current is not None:
                blocks.append(current)
            current = {"front": clean_text(lbl), "comunidad_row": None, "coord_row": None, "act_row": None}
            continue

        if current is None:
            continue

        norm_lbl = lbl.lower()
        if norm_lbl.startswith("comunidad"):
            current["comunidad_row"] = r
        elif norm_lbl.startswith("coordenadas"):
            current["coord_row"] = r
        elif norm_lbl.startswith("actividad"):
            # En hojas de Torres (Frente No 8), la fila que normalmente es Comunidad viene etiquetada como "Actividad"
            if current["comunidad_row"] is None and current["act_row"] is None and current["coord_row"] is None:
                current["comunidad_row"] = r
            else:
                current["act_row"] = r

    if current is not None:
        blocks.append(current)

    per_day = {}
    for day_key, _, _ in DAY_META:
        col = day_cols.get(day_key)
        if col is None:
            continue
        activities = []
        towers = []
        occupations = []
        aeros = []
        ejes = []

        for blk in blocks:
            comunidad = clean_text(grid.get((blk["comunidad_row"], col), "")) if blk["comunidad_row"] else ""
            coords = clean_text(grid.get((blk["coord_row"], col), "")) if blk["coord_row"] else ""
            act = clean_text(grid.get((blk["act_row"], col), "")) if blk["act_row"] else ""

            if not act and not comunidad and not coords:
                continue
            if not act:
                continue

            # Construir ubicación combinando comunidad y coordenadas sin duplicar
            loc_parts = []
            if comunidad:
                loc_parts.append(comunidad)
            if coords and coords.lower() != comunidad.lower():
                loc_parts.append(coords)
            location = " · ".join(loc_parts) if loc_parts else "Sin ubicación"

            activities.append({
                "source": source,
                "front": blk["front"],
                "title": act,
                "location": location,
            })

            combined_text = f"{comunidad} {coords} {act}"
            for eje_id in extract_ejes_from_text(combined_text):
                if eje_id not in ejes:
                    ejes.append(eje_id)

            if source == "TORRES":
                # Extraer torres T###[N|V] y casos como "Santa rosa (128)"
                for m in re.finditer(r"\bT\s*(\d{1,3}[NV]?)\b", combined_text, re.IGNORECASE):
                    tid = f"T{m.group(1).upper()}"
                    if tid not in towers:
                        towers.append(tid)
                for m in re.finditer(r"Santa\s*rosa\s*\((\d{2,3})\)", combined_text, re.IGNORECASE):
                    tid = f"T{m.group(1)}"
                    if tid not in towers:
                        towers.append(tid)
                for m in re.finditer(r"\bOC\s*0*(\d+)\b", combined_text, re.IGNORECASE):
                    oid = f"OC{int(m.group(1))}"
                    if oid not in occupations:
                        occupations.append(oid)
            else:
                # Extraer aerogeneradores WP##
                for m in re.finditer(r"\bWP[:\s]*0*(\d{1,2})\b", combined_text, re.IGNORECASE):
                    wid = f"WP{int(m.group(1))}"
                    if wid not in aeros:
                        aeros.append(wid)

        per_day[day_key] = {
            "activities": activities,
            "towers": towers,
            "occupations": occupations,
            "aeros": aeros,
            "ejes": ejes,
        }
    return per_day


def extract_ejes_from_text(text: str) -> list[str]:
    """Extrae identificadores normalizados de ejes viales (EJE2, EJE14, WP43, etc.)."""
    found: list[str] = []
    if not text:
        return found
    for m in re.finditer(
        r"\bejes?\b\s*:?\s*(\d{1,2}(?:\s*(?:,|y|\.|/|-)\s*\d{1,2})*)",
        text,
        re.IGNORECASE,
    ):
        for num in re.findall(r"\d{1,2}", m.group(1)):
            eid = f"EJE{int(num)}"
            if eid not in found:
                found.append(eid)
    if re.search(r"\bWP[:\s]*0*43\b", text, re.IGNORECASE) and "WP43" not in found:
        found.append("WP43")
    return found


def build_day_entry(day_key: str, day_name: str, date_str: str, month_num: str, parsed_sources: list[dict]) -> dict:
    towers = []
    occupations = []
    aeros = []
    ejes = []
    activities = []

    for pdata in parsed_sources:
        d = pdata.get(day_key)
        if not d:
            continue
        for t in d["towers"]:
            if t not in towers:
                towers.append(t)
        for o in d["occupations"]:
            if o not in occupations:
                occupations.append(o)
        for a in d["aeros"]:
            if a not in aeros:
                aeros.append(a)
        for e in d.get("ejes", []):
            if e not in ejes:
                ejes.append(e)
        activities.extend(d["activities"])

    return {
        "key": day_key,
        "name": day_name,
        "date": date_str,
        "label": f"{day_name} {date_str}-{month_num}",
        "towers": towers,
        "occupations": occupations,
        "aeros": aeros,
        "ejes": ejes,
        "activities": activities,
    }


def main():
    existing = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    torres_sheets = load_xlsx_sheets(FILE_TORRES)
    ods01_sheets = load_xlsx_sheets(FILE_ODS01)
    ods02_sheets = load_xlsx_sheets(FILE_ODS02)

    # 1. Conservar semanas históricas de octubre con source="TORRES"
    historical_weeks = []
    ods02_oct = parse_sheet_blocks(ods02_sheets["05.10 AL 10.10"], "ODS02")

    for w in existing["weeks"]:
        if w["id"] not in ("2026-09-28", "2026-10-05", "2026-10-12"):
            continue
        new_days = []
        for d in w["days"]:
            d_copy = dict(d)
            d_copy.setdefault("aeros", [])
            d_copy.setdefault("ejes", [])
            d_copy["activities"] = [
                {**act, "source": act.get("source") or "TORRES"} for act in d_copy.get("activities", [])
            ]
            if w["id"] == "2026-10-05" and d_copy["key"] in ods02_oct:
                extra = ods02_oct[d_copy["key"]]
                for a in extra["aeros"]:
                    if a not in d_copy["aeros"]:
                        d_copy["aeros"].append(a)
                for e in extra.get("ejes", []):
                    if e not in d_copy["ejes"]:
                        d_copy["ejes"].append(e)
                d_copy["activities"].extend(extra["activities"])
            for act in d_copy["activities"]:
                for e in extract_ejes_from_text(f"{act.get('location', '')} {act.get('title', '')}"):
                    if e not in d_copy["ejes"]:
                        d_copy["ejes"].append(e)
            new_days.append(d_copy)

        if w["id"] == "2026-10-05" and "saturday" in ods02_oct:
            sat = ods02_oct["saturday"]
            if sat["activities"]:
                new_days.append({
                    "key": "saturday",
                    "name": "Sábado",
                    "date": "10",
                    "label": "Sábado 10-10",
                    "towers": [],
                    "occupations": [],
                    "aeros": sat["aeros"],
                    "ejes": sat.get("ejes", []),
                    "activities": sat["activities"],
                })

        historical_weeks.append({**w, "days": new_days})

    # 2. Construir las 3 semanas del trisemanal de noviembre
    nov_weeks_spec = [
        {
            "id": "2026-11-09",
            "sheet": "09-11 a 15-11",
            "label": "09 al 15 de noviembre 2026",
            "torres_sheet": "09-11 al 14-11",
            "ods01_sheet": "09.11 AL 15.11",
            "ods02_sheet": "09.11  AL 15.11",
            "dates": [("monday", "Lunes", "09"), ("tuesday", "Martes", "10"), ("wednesday", "Miércoles", "11"), ("thursday", "Jueves", "12"), ("friday", "Viernes", "13"), ("saturday", "Sábado", "14")],
        },
        {
            "id": "2026-11-16",
            "sheet": "16-11 a 22-11",
            "label": "16 al 22 de noviembre 2026",
            "torres_sheet": "15-11 a 22-11",
            "ods01_sheet": "16.11 AL 22.11",
            "ods02_sheet": "16.11  AL 22.11",
            "dates": [("monday", "Lunes", "16"), ("tuesday", "Martes", "17"), ("wednesday", "Miércoles", "18"), ("thursday", "Jueves", "19"), ("friday", "Viernes", "20"), ("saturday", "Sábado", "21")],
        },
        {
            "id": "2026-11-23",
            "sheet": "23-11 a 29-11",
            "label": "23 al 29 de noviembre 2026",
            "torres_sheet": "23-11 a 29-11",
            "ods01_sheet": "23.11 AL 29.11",
            "ods02_sheet": "23.11  AL 29.11",
            "dates": [("monday", "Lunes", "23"), ("tuesday", "Martes", "24"), ("wednesday", "Miércoles", "25"), ("thursday", "Jueves", "26"), ("friday", "Viernes", "27"), ("saturday", "Sábado", "28")],
        },
    ]

    nov_weeks = []
    for spec in nov_weeks_spec:
        p_torres = parse_sheet_blocks(torres_sheets[spec["torres_sheet"]], "TORRES")
        p_ods01 = parse_sheet_blocks(ods01_sheets[spec["ods01_sheet"]], "ODS01")
        p_ods02 = parse_sheet_blocks(ods02_sheets[spec["ods02_sheet"]], "ODS02")

        days = [
            build_day_entry(d_key, d_name, d_date, "11", [p_torres, p_ods01, p_ods02])
            for d_key, d_name, d_date in spec["dates"]
        ]
        nov_weeks.append({
            "id": spec["id"],
            "sheet": spec["sheet"],
            "label": spec["label"],
            "days": days,
        })

    output = {
        "defaultWeekId": "2026-11-09",
        "weeks": historical_weeks + nov_weeks,
    }
    JSON_PATH.write_text(json.dumps(output, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    # Verificación cruzada contra GeoJSON
    torres_geo = {
        (f["properties"].get("name") or "").upper()
        for f in json.loads(TORRES_GEOJSON.read_text(encoding="utf-8"))["features"]
    }
    aeros_geo = {
        (f["properties"].get("name") or "").upper()
        for f in json.loads(AEROS_GEOJSON.read_text(encoding="utf-8"))["features"]
    }

    def tower_matches(tid: str) -> bool:
        return tid in torres_geo or f"{tid}N" in torres_geo or f"{tid}V" in torres_geo

    print("Generado programacion-semanal.json con", len(output["weeks"]), "semanas.")
    for w in nov_weeks:
        all_t = sorted({t for d in w["days"] for t in d["towers"]})
        all_a = sorted({a for d in w["days"] for a in d["aeros"]})
        all_o = sorted({o for d in w["days"] for o in d["occupations"]})
        all_e = sorted({e for d in w["days"] for e in d.get("ejes", [])})
        missing_t = [t for t in all_t if not tower_matches(t)]
        missing_a = [a for a in all_a if a not in aeros_geo]
        counts = {}
        for d in w["days"]:
            for act in d["activities"]:
                counts[act["source"]] = counts.get(act["source"], 0) + 1
        print(
            f"  {w['id']} ({w['label']}): acts={counts} | torres={all_t} | aeros={all_a} | occ={all_o} | ejes={all_e} | missing_t={missing_t} | missing_a={missing_a}"
        )


if __name__ == "__main__":
    main()

