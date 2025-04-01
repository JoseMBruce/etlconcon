# Descripción del repositorio

Los archivos de este repositorio contienen los scripts utilizados para la realización de todo el proceso de ingesta de datos para su uso posterior.

### Archivos principales:

- **`webscraping_*.py`** → Archivos utilizados para obtener la información desde distintos portales deportivos.  
- **`clean_data.py`** → Archivo encargado de limpiar los datos, transformarlos y unificar la información proveniente desde distintas fuentes.  
- **`update_gsheet_service.py`** → Archivo encargado de realizar la carga de datos en el Google Sheet.  
- **`orchestator.py`** → Se creó con el objetivo de realizar con un solo comando la extracción de datos de manera local. Finalmente, no se utilizó por la demora de cada proceso.  
- **`*.csv`** → Corresponde a archivos que se han utilizado para el panel. Actualmente, `final_4.csv` es el archivo principal en uso.  

