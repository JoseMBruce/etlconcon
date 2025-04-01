# Descripción del repositorio

Los archivos de este repositorio contienen los scripts utilizados para la realización de todo el proceso de ingesta de datos para su uso posterior.

### Archivos principales:

- **`webscraping_*.py`** → Archivos utilizados para obtener la información desde distintos portales deportivos.  
- **`clean_data.py`** → Archivo encargado de limpiar los datos, transformarlos y unificar la información proveniente desde distintas fuentes.  
- **`update_gsheet_service.py`** → Archivo encargado de realizar la carga de datos en el Google Sheet.  
- **`orchestator.py`** → Se creó con el objetivo de realizar con un solo comando la extracción de datos de manera local. Finalmente, no se utilizó por la demora de cada proceso.  
- **`*.csv`** → Corresponde a archivos que se han utilizado para el panel. Actualmente, `final_4.csv` es el archivo principal en uso.  

## Manual de Uso

Para usar un archivo de webscraping, se debe ejecutar un comando con la siguiente estructura en la terminal:

```sh
python webscraping_soccerway.py "url_del_portal" "archivo_csv_final.csv"
```

Por ejemplo:

```sh
python webscraping_soccerway.py "https://es.soccerway.com/national/chile/primera-division/2025/regular-season/r85780/" "raw_soccerway_primera_cl.csv"
```

Cabe destacar que los selectores de las tablas en las páginas podrían variar según la liga que se esté usando, por lo que hay que revisarlos en caso de error.

Si es una liga nueva, se debe incorporar el archivo correspondiente en el código de `clean_data.py`.


