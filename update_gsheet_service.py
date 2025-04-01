import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import logging
import numpy as np

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Log en la consola
        logging.FileHandler("extract_players.log")  # Log en un archivo
    ]
)

# Configuración de la API
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Carga de las credenciales
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(credentials)

# Abre el Google Sheet por URL o nombre
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1aI0BUpyGfcWSrfee98eWkEKUsQffKiiS-g23POhyawc/edit?gid=0#gid=0"

# Autenticación con Google Sheets
sheet = client.open_by_url(spreadsheet_url).sheet1  # Selecciona la primera hoja (sheet1)

logging.info("Leyendo CSV")
# Carga el archivo CSV como un DataFrame
csv_file = "clean_data_final_4.csv"
df_nuevo = pd.read_csv(csv_file)


try:
    # Leer los datos existentes en el Google Sheet
    logging.info("Leyendo datos actuales en Google Sheets")
    df_actual = pd.DataFrame(sheet.get_all_records())  # Convertir los datos existentes en DataFrame

    # Unir df_nuevo con df_actual usando "soccerway_pk" y agregar la columna "Valoracion Scouting"
    df_nuevo = df_nuevo.merge(df_actual[['soccerway_pk', 'Valoracion Scouting']], on='soccerway_pk', how='left')

    # Rellenar los valores NaN en la columna "Valoracion Scouting" con "Predeterminado"
    df_nuevo['Valoracion Scouting'].fillna('Predeterminada', inplace=True)

    logging.info("Limpiando GSheet")
    sheet.clear()


    logging.info("Comienza carga de datos...")
    

    # Actualizar todo el contenido en el Google Sheet
    sheet.update([df_nuevo.columns.values.tolist()] + df_nuevo.values.tolist())  # Encabezados + valores

    logging.info(f"Datos del archivo '{csv_file}' insertados correctamente en el Google Sheet.")

except Exception as e:
    logging.error(f"Error al actualizar los datos en Google Sheets: {e}")
    logging.info("Restaurando el DataFrame anterior...")
    
    # Reemplazar NaN por cadenas vacías si es necesario
    df_actual = df_actual.fillna("")  # Esto es opcional, dependiendo de cómo quieras tratar los NaN

    # Asegúrate de aplicar transformaciones solo a las columnas de tipo 'O' (cadenas de texto)
    df_actual = df_actual.apply(lambda x: x.map(str) if x.dtype == 'O' else x)

    
    #Cargar el DataFrame restaurado en Google Sheets

    sheet.update([df_actual.columns.values.tolist()] + df_actual.values.tolist())  # Cargar el DataFrame restaurado
    logging.info("Datos restaurados correctamente desde el GSheet.")

