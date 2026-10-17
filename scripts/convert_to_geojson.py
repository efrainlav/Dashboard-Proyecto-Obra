#!/usr/bin/env python3
import os
import zipfile
import xml.etree.ElementTree as ET
import re
import html
import json

def parse_html_table(desc):
    if not desc:
        return {}
    props = {}
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', desc, re.DOTALL | re.IGNORECASE)
    for r in rows:
        tds = re.findall(r'<td[^>]*>(.*?)</td>', r, re.DOTALL | re.IGNORECASE)
        tds = [re.sub(r'<[^>]+>', '', t).strip() for t in tds]
        if len(tds) >= 2 and tds[0]:
            k = html.unescape(tds[0]).strip()
            v = html.unescape(' '.join(tds[1:])).strip()
            props[k] = v
    return props

def parse_extended_data(elem):
    props = {}
    for data in elem.findall('.//{http://www.opengis.net/kml/2.2}SimpleData'):
        name = data.get('name')
        val = data.text or ''
        if name:
            props[name] = val.strip()
    for data in elem.findall('.//{http://www.opengis.net/kml/2.2}Data'):
        name = data.get('name')
        val_elem = data.find('{http://www.opengis.net/kml/2.2}value')
        val = val_elem.text if val_elem is not None else ''
        if name:
            props[name] = (val or '').strip()
    return props

def parse_coords_string(coords_str):
    coords = []
    for token in coords_str.strip().split():
        parts = token.split(',')
        if len(parts) >= 2:
            try:
                lon = round(float(parts[0]), 6)
                lat = round(float(parts[1]), 6)
                coords.append([lon, lat])
            except ValueError:
                continue
    return coords

def kml_to_geojson(kml_path, output_name):
    print(f"Processing {kml_path} -> {output_name}...")
    if kml_path.endswith('.kmz'):
        with zipfile.ZipFile(kml_path, 'r') as z:
            kml_entry = next(n for n in z.namelist() if n.lower().endswith('.kml'))
            xml_content = z.read(kml_entry)
            root = ET.fromstring(xml_content)
    else:
        with open(kml_path, 'rb') as f:
            root = ET.fromstring(f.read())

    placemarks = [el for el in root.iter() if el.tag.endswith('Placemark')]
    features = []

    for idx, pm in enumerate(placemarks):
        name_elem = next((el for el in pm.iter() if el.tag.endswith('name')), None)
        name = name_elem.text.strip() if (name_elem is not None and name_elem.text) else f"Feature_{idx+1}"
        
        desc_elem = next((el for el in pm.iter() if el.tag.endswith('description')), None)
        desc = desc_elem.text if desc_elem is not None else ''
        
        props = {"name": name}
        props.update(parse_html_table(desc))
        props.update(parse_extended_data(pm))
        
        # Geometría
        point_elem = next((el for el in pm.iter() if el.tag.endswith('Point')), None)
        poly_elem = next((el for el in pm.iter() if el.tag.endswith('Polygon')), None)
        multi_poly = next((el for el in pm.iter() if el.tag.endswith('MultiGeometry')), None)

        geometry = None

        if point_elem is not None:
            c_elem = next((el for el in point_elem.iter() if el.tag.endswith('coordinates')), None)
            if c_elem is not None and c_elem.text:
                pts = parse_coords_string(c_elem.text)
                if pts:
                    geometry = {
                        "type": "Point",
                        "coordinates": pts[0]
                    }
        elif poly_elem is not None:
            rings = []
            outer = next((el for el in poly_elem.iter() if el.tag.endswith('outerBoundaryIs')), None)
            if outer is not None:
                c_elem = next((el for el in outer.iter() if el.tag.endswith('coordinates')), None)
                if c_elem is not None and c_elem.text:
                    rings.append(parse_coords_string(c_elem.text))
            for inner in (el for el in poly_elem.iter() if el.tag.endswith('innerBoundaryIs')):
                c_elem = next((el for el in inner.iter() if el.tag.endswith('coordinates')), None)
                if c_elem is not None and c_elem.text:
                    rings.append(parse_coords_string(c_elem.text))
            if rings and rings[0]:
                geometry = {
                    "type": "Polygon",
                    "coordinates": rings
                }
        elif multi_poly is not None:
            # MultiPolygon
            multi_coords = []
            for poly in (el for el in multi_poly.iter() if el.tag.endswith('Polygon')):
                rings = []
                outer = next((el for el in poly.iter() if el.tag.endswith('outerBoundaryIs')), None)
                if outer is not None:
                    c_elem = next((el for el in outer.iter() if el.tag.endswith('coordinates')), None)
                    if c_elem is not None and c_elem.text:
                        rings.append(parse_coords_string(c_elem.text))
                for inner in (el for el in poly.iter() if el.tag.endswith('innerBoundaryIs')):
                    c_elem = next((el for el in inner.iter() if el.tag.endswith('coordinates')), None)
                    if c_elem is not None and c_elem.text:
                        rings.append(parse_coords_string(c_elem.text))
                if rings and rings[0]:
                    multi_coords.append(rings)
            if multi_coords:
                geometry = {
                    "type": "MultiPolygon",
                    "coordinates": multi_coords
                }

        if geometry:
            feat_id = pm.get('id') or f"{output_name.split('.')[0]}_{idx+1}"
            features.append({
                "type": "Feature",
                "id": feat_id,
                "properties": props,
                "geometry": geometry
            })

    geojson = {
        "type": "FeatureCollection",
        "name": output_name.replace('.geojson', ''),
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
            }
        },
        "features": features
    }

    os.makedirs('geojson', exist_ok=True)
    out_path = os.path.join('geojson', output_name)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    print(f" -> Guardado {out_path} con {len(features)} entidades.")

if __name__ == '__main__':
    layers = [
        ('kml/Torres.kml', 'Torres.geojson'),
        ('kml/Aeros_Parque.kml', 'Aerogeneradores.geojson'),
        ('kml/Area_Parque.kml', 'Area_Parque.geojson'),
        ('kml/Ocupacion_Cauce_Linea.kml', 'Ocupacion_Cauce_Linea.geojson'),
        ('kml/Ocupaciones_Cauce_Parque.kml', 'Ocupaciones_Cauce_Parque.geojson'),
        ('kml/Comunidades_2026.kmz', 'Comunidades.geojson'),
        ('kml/Municipios.kml.kmz', 'Municipios.geojson')
    ]
    for src, dst in layers:
        kml_to_geojson(src, dst)
    print("¡Todas las capas fueron convertidas exitosamente a GeoJSON!")
