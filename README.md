# Visor Proyecto Eólico vr 1.0

Visor geográfico interactivo para la visualización geoespacial de infraestructura eléctrica y eólica, torres de transmisión, aerogeneradores, ocupaciones de cauce, comunidades del área de influencia y avance/programación de obra.

---

## 🌐 Despliegue en Vivo (GitHub Pages)

El proyecto se encuentra publicado y en funcionamiento como una aplicación web estática mediante **GitHub Pages**:

🔗 **[https://efrainlav.github.io/Dashboard-Proyecto-Obra/](https://efrainlav.github.io/Dashboard-Proyecto-Obra/)**

Opera al 100% en el navegador del cliente sin requerir servidores backend ni bases de datos externas.

---

## 📌 Fuentes de Información Geográfica y Comunitaria

La información territorial, cartográfica y de contexto comunitario incorporada en este visor proviene de las siguientes fuentes de acceso público:

1. **Autoridad Nacional de Licencias Ambientales (ANLA):**
   - Las geometrías y capas espaciales de infraestructura técnica —incluyendo la localización y trazado de las torres de transmisión eléctrica, la ubicación de los aerogeneradores, el polígono perimetral del área del parque eólico y los puntos de ocupación de cauce— fueron tomadas a partir de la información geográfica pública de licenciamiento ambiental dispuesta por la **ANLA**.

2. **SEI – Anajia Guajira (Stockholm Environment Institute):**
   - Los datos geográficos, nombres y atributos de caracterización de las comunidades locales y asentamientos del área de influencia fueron recopilados y tomados del portal oficial de herramientas del Stockholm Environment Institute (SEI):
   - 🔗 **[SEI Anajia Guajira](https://www.sei.org/tools/anajia-guajira-es/)** (`https://www.sei.org/tools/anajia-guajira-es/`).

---

## ⚠️ Declaración Expresa sobre los Datos de Seguimiento y Avance de Obra (Datos Demo / Ficticios)

> [!IMPORTANT]
> ### AVISO LEGAL: LOS DATOS DE SEGUIMIENTO NO SON REALES
> 
> **Se deja expresa y categórica constancia de que todos los datos de seguimiento, indicadores porcentuales de avance físico de obra, frentes de trabajo y cronogramas contenidos en este repositorio NO son reales.**
> 
> - **Avance de Obra Simulado:** Los porcentajes y métricas presentados en los paneles de control de **Avance Torres** (*ahuyentamiento, excavación, solado, acero, concreto y relleno*) y **Aerogeneradores** (*cimentación, plataformas, canalizaciones, izaje, cableado y comisionamiento*) han sido generados de forma sintética/simulada con fines estrictamente didácticos, ilustrativos y de demostración técnica de capacidades en interfaces geográficas (GIS).
> - **Programación Semanal Ficticia:** Las actividades operativas, fechas, cuadrillas y asignaciones detalladas en `programacion-semanal.json` corresponden a información de prueba para validar la reactividad del mapa y la navegación temporal.
> - **Sin Información Confidencial ni Operativa:** Este visor **no contiene información confidencial**, reservada, comercial, contractual, financiera ni operativa real de ningún proyecto en construcción ni de compañía alguna.
> - **Desarrollo Independiente:** Este proyecto es un desarrollo independiente para investigación y prototipado de tableros de control de obra y no cuenta con patrocinio, representación ni vínculo oficial con ningún operador privado o entidad estatal.

---

## 🚀 Características Principales

- **Diseño de Alto Contraste para Campo:**
  - Paleta visual en verde bosque (`#1e513f`), blanco y acentos ámbar (`#dd9a39` / `#d97706`), inspirada en tableros KPI profesionales (ArcGIS Online) y optimizada para visibilidad en pantallas de dispositivos móviles bajo condiciones de alta radiación solar (como en La Guajira).

- **Panel de Control de Avance de Obra (KPIs Interactivos):**
  - **Pestaña Avance Torres:**
    - Muestra porcentajes de ejecución para: *Excavación*, *Relleno*, *Solado*, *Acero*, *Concreto* y *Ahuyentamiento*.
    - **Comportamiento Reactivo:** Si se hace clic en una torre específica, expone su avance individual; si se selecciona una comunidad, calcula y refleja automáticamente el promedio ponderado de las torres asociadas a dicha comunidad; si no hay selección activa, presenta el promedio general consolidado de todas las torres del proyecto.
  - **Pestaña Aerogeneradores:**
    - Tarjetas KPI con el progreso de las 47 turbinas eólicas (*Cimentación*, *Plataformas*, *Canalizaciones*, *Izaje*, *Cableado* y *Comisionamiento*).
    - Desacoplada de las comunidades; responde a la selección individual de aerogeneradores o al consolidado total del parque.
  - **Pestaña Programación Semanal:**
    - Selector dinámico de semana de programación.
    - Pestañas por día (Lunes a Viernes y Consolidado semanal).
    - Filtrado reactivo en el mapa: resalta las torres y ocupaciones programadas para la jornada.

- **Mapa Cartográfico Interactivo (Leaflet 1.9.4):**
  - Control de capas base: callejero OpenStreetMap y satélite Esri World Imagery (híbrido con etiquetas).
  - Escala métrica y navegación fluida adaptada a escritorio y dispositivos móviles.

- **Capas Geográficas (KML y KMZ):**
  - **Torres de transmisión:** Trazado y ubicación de estructuras (`kml/Torres.kml`).
  - **Aerogeneradores:** Posición de turbinas eólicas (`kml/Aeros_Parque.kml`).
  - **Polígono del parque:** Delimitación perimetral del área del proyecto (`kml/Area_Parque.kml`).
  - **Ocupaciones de cauce:** Puntos de intervención hídrica en línea y parque (`kml/Ocupacion_Cauce_Linea.kml`, `kml/Ocupaciones_Cauce_Parque.kml`).
  - **Comunidades:** Localización de asentamientos del área de influencia (`kml/Comunidades_2026.kmz`). Popup simplificado con: Nombre, Semáforo, Zona y Coordenadas con formato truncado a 8 caracteres máximo.

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
├── png/                        # Recursos visuales y logotipo
│   └── dummy_logo.jpg
├── svg/                        # Iconos vectoriales de infraestructura
│   ├── eolica.svg
│   ├── hut.svg
│   └── transmission-tower.svg
├── .gitignore                  # Reglas de exclusión de archivos
└── README.md                   # Documentación técnica y aviso legal
```

---

## 🛠️ Tecnologías Utilizadas

- **Frontend Core:** HTML5 semántico, CSS3 moderno con variables y diseño responsivo, JavaScript Vanilla (ES6+).
- **Librería de Mapas:** Leaflet 1.9.4.
- **Procesamiento Geoespacial:** Omnivore y ToGeoJSON para renderizado dinámico de KML y compresión KMZ (JSZip) en el navegador.

---

## 💻 Ejecución Local

Para ejecutar y probar el visor localmente:

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/efrainlav/Dashboard-Proyecto-Obra.git
   cd Dashboard-Proyecto-Obra
   ```

2. Iniciar un servidor HTTP local (requerido para permitir la carga de capas KML/KMZ locales mediante peticiones `fetch` sin restricciones de origen CORS):
   ```bash
   # Opción 1: Python 3
   python3 -m http.server 8000

   # Opción 2: Node.js (npx serve)
   npx serve .
   ```

3. Abrir en el navegador:
   ```text
   http://localhost:8000
   ```
