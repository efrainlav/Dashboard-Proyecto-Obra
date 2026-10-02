# Visor Proyecto Windpeshi vr 1.0

Visor geográfico interactivo para la visualización de la infraestructura, torres de transmisión, ocupaciones de cauce, comunidades y programación semanal de obra del Proyecto Windpeshi.

## 🚀 Características

- **Mapa interactivo:** Basado en Leaflet con capa de callejero OpenStreetMap y satélite híbrido Esri.
- **Capas geográficas:**
  - Torres de transmisión (`kml/Torres.kml`)
  - Aerogeneradores (`kml/Aeros_Parque.kml`)
  - Área del parque (`kml/Area_Parque.kml`)
  - Ocupaciones de cauce en línea y parque (`kml/Ocupacion_Cauce_Linea.kml`, `kml/Ocupaciones_Cauce_Parque.kml`)
  - Comunidades del área de influencia (`kml/Comunidades_2026.kmz`)
- **Programación semanal y reprogramación:**
  - Selector de semana (`programacion-semanal.json`) con actualización reactiva de fechas.
  - Navegación diaria (Lunes a Viernes y Resumen semanal).
  - Resaltado visual en el mapa de las torres y cauces programados para cada jornada.
  - Clasificación de actividades: Social y predial, Gestión ambiental, Obra civil, Logística y suministros.
- **Interactividad panel ↔ mapa:** Clic en torres u ocupaciones de la lista para enfocar y abrir su ventana emergente con datos técnicos.

## 📦 Estructura del proyecto

```text
├── index.html                  # Aplicación web / Visor
├── programacion-semanal.json   # Catálogo de programación semanal
├── kml/                        # Capas espaciales (KML y KMZ)
├── png/                        # Logotipo e imágenes institucionales
├── svg/                        # Íconos vectoriales del visor
└── README.md                   # Documentación
```

## 🌐 Despliegue en GitHub Pages

Este proyecto es una aplicación estática y funciona directamente en **GitHub Pages**.
