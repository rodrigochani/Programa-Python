from PyQt5.QtWidgets import QDialog, QPushButton, QVBoxLayout, QLabel, QLineEdit, QFileDialog
from qgis.core import QgsVectorLayer, QgsProject, QgsProcessingFeatureSourceDefinition, QgsVectorFileWriter
import os
import processing  # Importando el módulo processing
import urllib.request

class MiVentana(QDialog):
    def __init__(self, parent=None):
        super(MiVentana, self).__init__(parent)

        # Widgets
        self.label1 = QLabel("Número de padrón Catastral (si posee):")
        self.line_edit1 = QLineEdit()
        self.label2 = QLabel("Ruta del archivo para intersección:")
        self.line_edit2 = QLineEdit()
        self.boton1 = QPushButton("Seleccionar archivo")
        self.label3 = QLabel("Nombre del plan:")
        self.line_edit3 = QLineEdit()
        self.boton_ejecutar = QPushButton("Ejecutar")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.line_edit1)
        layout.addWidget(self.label2)
        layout.addWidget(self.line_edit2)
        layout.addWidget(self.boton1)
        layout.addWidget(self.label3)
        layout.addWidget(self.line_edit3)
        
        layout.addWidget(self.boton_ejecutar)

        self.setLayout(layout)

        # Conectar botones a acciones
        self.boton1.clicked.connect(self.seleccionar_archivo)
        self.boton_ejecutar.clicked.connect(self.ejecutar_proceso)
        
           
    def descargar_kml(self):
        numero_padron = self.line_edit1.text()
        archivo_seleccionado = self.line_edit2.text()
        nombre_plan = self.line_edit3.text()

        url = f"http://190.221.181.230:85/kml.asp?txtpadron={numero_padron}"

        # Carpeta de descarga
        if numero_padron or archivo_seleccionado:
            carpeta_descarga = os.path.join('C:/Users/.../', nombre_plan)
            # Si la carpeta no existe, crearla
        if not os.path.exists(carpeta_descarga):
            os.makedirs(carpeta_descarga)

                # Ruta completa del archivo a descargar
        ruta_descarga = f'C:/Users/.../'/{nombre_plan}/padron_{numero_padron}.kml'

        try:
            # Descargar el archivo
            urllib.request.urlretrieve(url, ruta_descarga)
            return ruta_descarga
        except urllib.error.HTTPError:
            return None

    def seleccionar_archivo(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo", "", "Shapefiles (*.shp);;All Files (*)")
        if filename:
            self.line_edit2.setText(filename)
           
         
       
    def ejecutar_proceso(self):
        ruta_kml = self.descargar_kml()

        # Si descargar_kml devuelve None, usar el archivo seleccionado
        archivo_interseccion = ruta_kml if ruta_kml else self.line_edit2.text()

        # Asumiendo que tienes otro archivo con el que realizar la intersección
        archivo_base = 'D:/.../Archivo.shp'
        
        # Intersección
        inter_result = processing.run("qgis:intersection", {
            'INPUT': archivo_base,
            'OVERLAY': archivo_interseccion,
            'OUTPUT': 'memory:'
        })

        # Disolución
        dissolved = processing.run("qgis:dissolve", {
            'INPUT': inter_result['OUTPUT'],
            'FIELD': ['color'],
            'OUTPUT': 'memory:'
            })
        
        # Obtener todos los nombres de campos de la capa dissolved
        all_fields = [field.name() for field in dissolved['OUTPUT'].fields()]

        if self.line_edit1: 
            # Filtrar los campos que no queremos eliminar
            campos_a_mantener = ['Name', 'description', 'color', 'sup_ha']
        else:
            campos_a_mantener = ['color', 'sup_ha']

        campos_a_eliminar = [field for field in all_fields if field not in campos_a_mantener]
                
        nombre_plan = self.line_edit3.text()
                     
        # Obtener los índices de los campos a eliminar
        indexes_to_delete = [dissolved['OUTPUT'].fields().indexFromName(field) for field in campos_a_eliminar if dissolved['OUTPUT'].fields().indexFromName(field) != -1]
        
        if campos_a_eliminar:
            dissolved['OUTPUT'].startEditing()
            dissolved['OUTPUT'].deleteAttributes(indexes_to_delete)
            dissolved['OUTPUT'].commitChanges()
                    
        dissolved_cleaned = dissolved
        
        dissolved_with_area = processing.run("qgis:fieldcalculator", {
        'INPUT': dissolved_cleaned['OUTPUT'],
        'FIELD_NAME': 'sup_ha',
        'FIELD_TYPE': 0, # 0 indica que es un campo decimal (double)
        'FIELD_LENGTH': 10, 
        'FIELD_PRECISION': 3,
        'NEW_FIELD': False,  # Indica que no estamos creando un nuevo campo, sino actualizando uno existente
        'FORMULA': '$area / 10000',  # Fórmula para calcular la superficie y convertir de m² a hectáreas
        'OUTPUT': 'memory:'
})
        
        # Eliminar filas por color
        colores_eliminar = ["Marron Oscuro", "Marron Claro", "NoData"]
        ids_eliminar = []

        for feature in dissolved_with_area['OUTPUT'].getFeatures():
            if feature['color'] in colores_eliminar:
                ids_eliminar.append(feature.id())

        if ids_eliminar:
            dissolved_with_area['OUTPUT'].startEditing()
            dissolved_with_area['OUTPUT'].deleteFeatures(ids_eliminar)
            dissolved_with_area['OUTPUT'].commitChanges()
        
                

        if dissolved_with_area :
            # Guardar el archivo resultante en formato SHP
            output_file = f'C:/Users/Desktop/Desktop/Convocatoria 2022/{nombre_plan}/{nombre_plan}_Plan'
            # Guardamos el resultado como SHP
            QgsVectorFileWriter.writeAsVectorFormat(dissolved_with_area['OUTPUT'], output_file, "utf-8", dissolved_with_area['OUTPUT'].crs(), "ESRI Shapefile")
            print(f"Resultado guardado en {output_file}")
            # Guardar el archivo resultante en formato KML
            output_file2 = f'C:/Users/Desktop/Desktop/Convocatoria 2022/{nombre_plan}/{nombre_plan}_Plan.kml'
            # Guardamos el resultado como KML
            QgsVectorFileWriter.writeAsVectorFormat(dissolved_with_area['OUTPUT'], output_file2, "utf-8", dissolved_with_area['OUTPUT'].crs(), "kml")
            print(f"Resultado guardado en {output_file2}")
            self.close()
        else: 
            print ('No se logró una intersección. El padrón está vacío.')
        
        # Suponiendo que 'campo_para_contar' es el nombre del campo en el que estás interesado
        campo_para_contar = "color"

        # Obtener los índices de las características basadas en el campo específico
        indices = [feature[campo_para_contar] for feature in dissolved_with_area['OUTPUT'].getFeatures()]
                
        if len (indices) > 1 :
            dissolved_unique = processing.run("qgis:dissolve", {
            'INPUT': dissolved_with_area['OUTPUT'],
            'FIELD': [],
            'OUTPUT': 'memory:'
            })
        
        dissolved_unique_with_area = processing.run("qgis:fieldcalculator", {
        'INPUT': dissolved_unique['OUTPUT'],
        'FIELD_NAME': 'sup_ha',
        'FIELD_TYPE': 0, # 0 indica que es un campo decimal (double)
        'FIELD_LENGTH': 10, 
        'FIELD_PRECISION': 3,
        'NEW_FIELD': False,  # Indica que no estamos creando un nuevo campo, sino actualizando uno existente
        'FORMULA': '$area / 10000',  # Fórmula para calcular la superficie y convertir de m² a hectáreas
        'OUTPUT': 'memory:'
        })
        
        if dissolved_unique_with_area :
            # Guardar el archivo resultante en formato KML
            output_file3 = f'C:/.../{nombre_plan}/{nombre_plan}_dis_Plan.kml'
            # Guardamos el resultado como KML
            QgsVectorFileWriter.writeAsVectorFormat(dissolved_unique_with_area['OUTPUT'], output_file3, "utf-8", dissolved_unique_with_area['OUTPUT'].crs(), "kml")
            print(f"Resultado guardado en {output_file3}")
            
        else: 
            print ('No se logró la disolución. No había más categorías.')
        
        # Agregar la capa SHP a QGIS
        shp_layer = QgsVectorLayer(output_file + ".shp", f"{nombre_plan}_SHP", "ogr")
        if shp_layer.isValid():
            QgsProject.instance().addMapLayer(shp_layer)

        # Agregar la capa KML a QGIS
        kml_layer = QgsVectorLayer(output_file2, f"{nombre_plan}_KML", "ogr")
        if kml_layer.isValid():
            QgsProject.instance().addMapLayer(kml_layer)
            
        # Agregar la capa KML a QGIS
        kml_layer2 = QgsVectorLayer(output_file3, f"{nombre_plan}_dis_KML", "ogr")
        if kml_layer2.isValid():
            QgsProject.instance().addMapLayer(kml_layer2)
        self.close()    
        
ventana = MiVentana()
ventana.exec_()