# Visor Proyecto Windpeshi vr 1.0

Visor geográfico interactivo para la visualización de infraestructura eléctrica y eólica, torres de transmisión, ocupaciones de cauce, comunidades del área de influencia y programación semanal de obra.

---

## 🌐 Despliegue en Vivo (GitHub Pages)

El proyecto está publicado y en funcionamiento como una página web estática a través de **GitHub Pages**:

🔗 **[https://efrainlav.github.io/Dashboard-Proyecto-Obra/](https://efrainlav.github.io/Dashboard-Proyecto-Obra/)**

No requiere servidores backend, bases de datos externas ni configuraciones especiales; opera 100% en el navegador del cliente.

---

## ⚠️ Aviso sobre los Datos (Datos Demo / Ficticios)

> **IMPORTANTE:**
> 
> Todos los datos de programación, frentes de obra, fechas, actividades operativas y asignaciones contenidos en este repositorio (`programacion-semanal.json`) corresponden a **datos simulados / datos demo**.
> 
> - Su propósito es **estrictamente ilustrativo, didáctico y de demostración técnica** de capacidades en visualización geográfica e interfaces de control de obra.
> - **No contienen información confidencial**, reservada, comercial, contractual ni operativa real de ninguna entidad o empresa.
> - Este proyecto es un desarrollo independiente y no cuenta con afiliación, representación ni patrocinio oficial de ninguna compañía u operadora específica.

---

## 🚀 Características Principales

- **Mapa Cartográfico Interactivo:**
  - Desarrollado sobre Leaflet con soporte de control de capas base: callejero OpenStreetMap y satélite Esri World Imagery (híbrido con etiquetas).
  - Escala métrica integrada y controles de navegación intuitivos.

- **Capas Geográficas (KML y KMZ):**
  - **Torres de transmisión:** Trazado y ubicación de estructuras (`kml/Torres.kml`).
  - **Aerogeneradores:** Posición de turbinas eólicas (`kml/Aeros_Parque.kml`).
  - **Polígono del parque:** Delimitación perimetral del área del proyecto (`kml/Area_Parque.kml`).
  - **Ocupaciones de cauce:** Puntos de intervención hídrica en línea y parque (`kml/Ocupacion_Cauce_Linea.kml`, `kml/Ocupaciones_Cauce_Parque.kml`).
  - **Comunidades:** Localización de asentamientos y comunidades del entorno (`kml/Comunidades_2026.kmz`).

- **Control Dinámico de Programación Semanal:**
  - Selector de semana reactivo que sincroniza automáticamente las fechas y jornadas.
  - Navegación diaria por pestañas (Lunes a Viernes y Resumen semanal consolidado).
  - Resaltado visual en el mapa de las torres y ocupaciones de cauce programadas para la jornada activa.
  - Agrupación por tipos de actividad:
    - *Social y predial*
    - *Gestión ambiental*
    - *Obra civil*
    - *Logística y suministros*

- **Interactividad Panel Lateral ↔ Mapa:**
  - Clic en cualquier torre u ocupación del panel para hacer zoom automático, centrado y apertura del popup con metadatos técnicos.
  - Conteo reactivo de elementos programados por día.

---

## 📦 Estructura del Repositorio

```text
├── index.html                  # Aplicación web / Visor interactivo
├── programacion-semanal.json   # Datos demo de programación semanal
├── kml/                        # Capas espaciales vectoriales (KML y KMZ)
│   ├── Aeros_Parque.kml
│   ├── Area_Parque.kml
│   ├── Comunidades_2026.kmz
│   ├── Municipios.kml.kmz
│   ├── Ocupacion_Cauce_Linea.kml
│   ├── Ocupaciones_Cauce_Parque.kml
│   └── Torres.kml
├── png/                        # Recursos visuales y logotipo genérico
│   └── dummy_logo.jpg
├── svg/                        # Iconos vectoriales de infraestructura
│   ├── eolica.svg
│   ├── hut.svg
│   └── transmission-tower.svg
├── .gitignore                  # Reglas de exclusión de archivos
└── README.md                   # Documentación técnica
```

---

## 🛠️ Tecnologías Utilizadas

- **Frontend Core:** HTML5 semántico, CSS3 moderno con variables y diseño responsivo, JavaScript Vanilla (ES6+).
- **Librería de Mapas:** Leaflet 1.9.4.
- **Procesamiento Geoespacial:** Omnivore y ToGeoJSON para renderizado dinámico de KML y compresión KMZ (JSZip) en el navegador.

---

## 💻 Ejecución Local

Para probar el visor localmente:

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/efrainlav/Dashboard-Proyecto-Obra.git
   cd Dashboard-Proyecto-Obra
   ```

2. Iniciar un servidor web local (necesario para permitir la carga de capas KML/KMZ locales mediante `fetch` sin bloqueos CORS):
   ```bash
   # Con Python 3:
   python3 -m http.server 8000
   
   # O con Node.js (npx serve):
   npx serve .
   ```

3. Abrir en el navegador:
   ```text
   http://localhost:8000
   ```
