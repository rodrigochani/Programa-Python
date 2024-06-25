# Proyecto de Intersección de Capas Geoespaciales

Este repositorio contiene un script de Python desarrollado con PyQt5 y el módulo de procesamiento de QGIS. Permite a los usuarios seleccionar archivos de forma interactiva para realizar operaciones geoespaciales, como intersecciones y disoluciones de capas, y guardar los resultados en diferentes formatos.

## Características

- Interfaz gráfica de usuario para la entrada fácil de datos y selección de archivos.
- Descarga automática de archivos KML usando un número de padrón catastral.
- Intersección y disolución de capas geoespaciales.
- Cálculo de áreas y eliminación de características basadas en atributos específicos.
- Guardado de resultados en formatos SHP y KML.
- Adición de capas resultantes al proyecto actual de QGIS.

## Requisitos

Para ejecutar este script, necesitas tener instalado:

- Python 3.x
- PyQt5
- QGIS con el módulo `processing` habilitado

Puedes instalar PyQt5 usando pip:

```bash
pip install PyQt5
