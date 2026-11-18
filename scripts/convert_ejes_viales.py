#!/usr/bin/env python3
"""
Convierte el shapefile Eje_Via.zip (MAGNA-SIRGAS_2018_Origen-Nacional / EPSG:9377)
a GeoJSON WGS84 en geojson/Ejes_Viales.geojson.
"""

import json
import math
import struct
import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ZIP_PATH = Path("/tmp/Eje_Via.zip")
OUT_PATH = BASE_DIR / "geojson" / "Ejes_Viales.geojson"


def epsg9377_to_wgs84(x: float, y: float) -> list[float]:
    """Transforma coordenadas planas EPSG:9377 (MAGNA-SIRGAS Origen Nacional) a [lon, lat] WGS84."""
    a = 6378137.0
    f = 1.0 / 298.257222101
    e2 = 2.0 * f - f * f
    ep2 = e2 / (1.0 - e2)
    k0 = 0.9992
    lat0 = math.radians(4.0)
    lon0 = math.radians(-73.0)
    fe = 5000000.0
    fn = 2000000.0

    def meridian_arc(lat: float) -> float:
        e4 = e2 * e2
        e6 = e4 * e2
        return a * (
            (1.0 - e2 / 4.0 - 3.0 * e4 / 64.0 - 5.0 * e6 / 256.0) * lat
            - (3.0 * e2 / 8.0 + 3.0 * e4 / 32.0 + 45.0 * e6 / 1024.0) * math.sin(2.0 * lat)
            + (15.0 * e4 / 256.0 + 45.0 * e6 / 1024.0) * math.sin(4.0 * lat)
            - (35.0 * e6 / 3072.0) * math.sin(6.0 * lat)
        )

    m0 = meridian_arc(lat0)
    m = m0 + (y - fn) / k0
    mu = m / (a * (1.0 - e2 / 4.0 - 3.0 * e2 * e2 / 64.0 - 5.0 * e2 * e2 * e2 / 256.0))
    e1 = (1.0 - math.sqrt(1.0 - e2)) / (1.0 + math.sqrt(1.0 - e2))
    phi1 = (
        mu
        + (3.0 * e1 / 2.0 - 27.0 * e1**3 / 32.0) * math.sin(2.0 * mu)
        + (21.0 * e1**2 / 16.0 - 55.0 * e1**4 / 32.0) * math.sin(4.0 * mu)
        + (151.0 * e1**3 / 96.0) * math.sin(6.0 * mu)
        + (1097.0 * e1**4 / 512.0) * math.sin(8.0 * mu)
    )
    sin_p = math.sin(phi1)
    cos_p = math.cos(phi1)
    tan_p = math.tan(phi1)
    n1 = a / math.sqrt(1.0 - e2 * sin_p * sin_p)
    t1 = tan_p * tan_p
    c1 = ep2 * cos_p * cos_p
    r1 = a * (1.0 - e2) / ((1.0 - e2 * sin_p * sin_p) ** 1.5)
    d = (x - fe) / (n1 * k0)

    lat = phi1 - (n1 * tan_p / r1) * (
        d**2 / 2.0
        - (5.0 + 3.0 * t1 + 10.0 * c1 - 4.0 * c1**2 - 9.0 * ep2) * d**4 / 24.0
        + (61.0 + 90.0 * t1 + 298.0 * c1 + 45.0 * t1**2 - 252.0 * ep2 - 3.0 * c1**2)
        * d**6
        / 720.0
    )
    lon = lon0 + (
        d
        - (1.0 + 2.0 * t1 + c1) * d**3 / 6.0
        + (5.0 - 2.0 * c1 + 28.0 * t1 - 3.0 * c1**2 + 8.0 * ep2 + 24.0 * t1**2) * d**5 / 120.0
    ) / cos_p
    return [round(math.degrees(lon), 6), round(math.degrees(lat), 6)]


def read_dbf_records(dbf_bytes: bytes) -> list[dict[str, str]]:
    num_rec, len_hdr, len_rec = struct.unpack("<4xIHH20x", dbf_bytes[:32])
    fields = []
    off = 32
    while off < len_hdr - 1 and dbf_bytes[off] != 0x0D:
        fn = dbf_bytes[off : off + 11].split(b"\x00")[0].decode("latin1")
        fl = dbf_bytes[off + 16]
        fields.append((fn, fl))
        off += 32

    records = []
    for i in range(num_rec):
        rec = dbf_bytes[len_hdr + i * len_rec + 1 : len_hdr + (i + 1) * len_rec]
        foff = 0
        props = {}
        for fn, fl in fields:
            props[fn] = (
                rec[foff : foff + fl].replace(b"\x00", b"").decode("utf-8", errors="replace").strip()
            )
            foff += fl
        records.append(props)
    return records


def build_feature_metadata(idx: int, raw_eje: str, doc_name: str, length_m: float) -> dict:
    clean_eje = (raw_eje or "").strip().upper()

    if not clean_eje and "11-12-13-WP43" in doc_name:
        return {
            "name": "Acceso WP43 (tramo inicial)",
            "shortName": "WP43",
            "ejeId": "WP43",
            "ejeAliases": ["WP43"],
        }

    if clean_eje.startswith("WP"):
        return {
            "name": f"Acceso {clean_eje}",
            "shortName": clean_eje,
            "ejeId": clean_eje,
            "ejeAliases": [clean_eje],
        }

    # En XREF-088-CIV-EJE VÍA-4-6-7.dwg el tramo principal (REC 12, 1682.8 m)
    # viene etiquetado como EJE='7' y representa también el corredor del Eje 4.
    if clean_eje == "7" and "4-6-7" in doc_name:
        if length_m > 500:
            return {
                "name": "Eje Vial 4 / 7",
                "shortName": "Eje 4 / 7",
                "ejeId": "EJE7",
                "ejeAliases": ["EJE4", "EJE7"],
            }
        return {
            "name": "Eje Vial 7 (ramal)",
            "shortName": "Eje 7",
            "ejeId": "EJE7",
            "ejeAliases": ["EJE7"],
        }

    if clean_eje.isdigit():
        num = int(clean_eje)
        eje_id = f"EJE{num}"
        return {
            "name": f"Eje Vial {num}",
            "shortName": f"Eje {num}",
            "ejeId": eje_id,
            "ejeAliases": [eje_id],
        }

    return {
        "name": f"Eje Vial {idx + 1}",
        "shortName": f"Eje {idx + 1}",
        "ejeId": f"EJE_{idx + 1}",
        "ejeAliases": [],
    }


def main() -> None:
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo {ZIP_PATH}")

    with zipfile.ZipFile(ZIP_PATH) as z:
        dbf_bytes = z.read("Eje_Via.dbf")
        shp_bytes = z.read("Eje_Via.shp")
        shx_bytes = z.read("Eje_Via.shx")

    records = read_dbf_records(dbf_bytes)
    features = []

    for i, rec_props in enumerate(records):
        shx_off = 100 + i * 8
        rec_off_words = struct.unpack(">i", shx_bytes[shx_off : shx_off + 4])[0]
        byte_off = rec_off_words * 2 + 8
        shp_type = struct.unpack("<i", shp_bytes[byte_off : byte_off + 4])[0]
        if shp_type not in (3, 13, 23):
            continue

        num_parts, num_pts = struct.unpack("<ii", shp_bytes[byte_off + 36 : byte_off + 44])
        parts = list(
            struct.unpack(f"<{num_parts}i", shp_bytes[byte_off + 44 : byte_off + 44 + 4 * num_parts])
        )
        pts_off = byte_off + 44 + 4 * num_parts
        raw_pts = [
            struct.unpack("<dd", shp_bytes[pts_off + j * 16 : pts_off + (j + 1) * 16])
            for j in range(num_pts)
        ]

        part_bounds = parts + [num_pts]
        part_lines_raw = [raw_pts[part_bounds[p] : part_bounds[p + 1]] for p in range(num_parts)]
        total_len_m = 0.0
        for line in part_lines_raw:
            for j in range(len(line) - 1):
                total_len_m += math.hypot(line[j + 1][0] - line[j][0], line[j + 1][1] - line[j][1])

        meta = build_feature_metadata(
            i, rec_props.get("EJE", ""), rec_props.get("DocName", ""), total_len_m
        )

        wgs_lines = [[epsg9377_to_wgs84(x, y) for x, y in line] for line in part_lines_raw if len(line) >= 2]
        if not wgs_lines:
            continue

        geometry = (
            {"type": "LineString", "coordinates": wgs_lines[0]}
            if len(wgs_lines) == 1
            else {"type": "MultiLineString", "coordinates": wgs_lines}
        )

        features.append(
            {
                "type": "Feature",
                "id": f"eje_via_{i + 1}",
                "properties": {
                    "name": meta["name"],
                    "shortName": meta["shortName"],
                    "ejeId": meta["ejeId"],
                    "ejeAliases": meta["ejeAliases"],
                    "rawEje": rec_props.get("EJE", ""),
                    "layer": rec_props.get("Layer", ""),
                    "docName": rec_props.get("DocName", ""),
                    "length_m": round(total_len_m, 1),
                    "length_km": round(total_len_m / 1000.0, 2),
                },
                "geometry": geometry,
            }
        )

    geojson = {
        "type": "FeatureCollection",
        "name": "Ejes_Viales",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": features,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(geojson, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generado {OUT_PATH} con {len(features)} ejes viales.")


if __name__ == "__main__":
    main()
