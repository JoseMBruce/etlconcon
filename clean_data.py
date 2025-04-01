import pandas as pd
import logging
import csv
import locale
import re
import unicodedata
from datetime import datetime
import numpy as np

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", mode="a", encoding="utf-8"),  # Guarda en un archivo
        logging.StreamHandler()  # Muestra en consola
    ]
)

# Función para convertir la fecha de nacimiento
def convertir_fecha(fecha):
    try:
        # Eliminar espacios extra al principio y al final
        fecha = fecha.strip()

        # Separar la fecha de la edad usando el primer espacio
        fecha_sin_edad = fecha.split("(")[0]  # Tomamos solo la parte "11/03/1995"
        
        # Separar la fecha en día, mes, y año
        dia, mes, anio = fecha_sin_edad.split("/")  # Separa la fecha en día, mes, año
        
        # Diccionario de meses
        meses = {
            "01": "enero", "02": "febrero", "03": "marzo", "04": "abril", "05": "mayo", "06": "junio",
            "07": "julio", "08": "agosto", "09": "septiembre", "10": "octubre", "11": "noviembre", "12": "diciembre"
        }
        
        # Convertir el mes numérico al nombre
        mes_nombre = meses[mes]
        
        # Formatear la fecha en el formato requerido sin la edad entre paréntesis
        return f"{dia}_{mes_nombre}_{anio}"
    except Exception as e:
        logging.error(f"Error al convertir la fecha {fecha}: {e}")
        return fecha  # En caso de error, devolvemos la fecha original

def leer_csv(archivo):
    """Lee un archivo CSV y lo devuelve como un DataFrame de pandas."""
    try:
        df = pd.read_csv(archivo)
        logging.info(f"Archivo {archivo} cargado correctamente con {df.shape[0]} filas y {df.shape[1]} columnas.")
        return df
    except Exception as e:
        logging.error(f"Error al leer el archivo {archivo}: {e}")
        return None

def limpiar_texto(texto):
    """
    Limpia espacios en blanco adicionales en un texto, reemplaza múltiples espacios con un solo espacio,
    y convierte el texto a minúsculas. También formatea fechas sin la hora.

    Parámetros:
    texto (str, datetime, int, etc.): Texto o dato a limpiar.

    Retorna:
    str: Texto limpio o una cadena vacía en caso de error.
    """
    try:
        if pd.isna(texto):  # Si es NaN, devolver una cadena vacía
            return ""
        
        # Si el valor es una fecha, convertirla a string en formato YYYY-MM-DD
        if isinstance(texto, pd.Timestamp):  
            return texto.strftime("%d_%B_%Y")  # Convertir a string sin la hora
        
        return "_".join(str(texto).strip().split()).lower()  # Convertir a texto limpio
    except Exception as e:
        logging.error(f"Error al limpiar texto: {e}")
        return ""  # Retorna cadena vacía en caso de error

def agregar_llave_primaria_soccerway(df):
    """
    Agrega una llave primaria 'soccerway_pk' concatenando 'Nombre', 'Apellidos', 'Nacionalidad' y 'Fecha de nacimiento'.

    Parámetros:
    df (pd.DataFrame): DataFrame con las columnas necesarias.

    Retorna:
    pd.DataFrame: DataFrame con la columna 'soccerway_pk' agregada.
    """

    df_temp = df.copy() 

    try:
        columnas_necesarias = ["Nombre", "Apellidos", "Nacionalidad", "Fecha de nacimiento"]
        for col in columnas_necesarias:
            if col not in df.columns:
                raise ValueError(f"Falta la columna '{col}' en el archivo CSV.")

        # Limpiar espacios en blanco en cada celda de las columnas necesarias
        for col in columnas_necesarias:
            df_temp[col] = df_temp[col].apply(limpiar_texto)

        # Crear la llave primaria sin espacios extra
        df.insert(0, "soccerway_pk", df_temp["Nombre"] + "_" + df_temp["Apellidos"] + "_" + df_temp["Nacionalidad"] + "_" + df_temp["Fecha de nacimiento"])

        logging.info("Llave primaria agregada correctamente en soccerway.")
        return df

    except Exception as e:
        logging.error(f"Error: {e}")
        return None
    
def agregar_llave_primaria_tmkt(df):
    """
    Agrega una llave primaria 'soccerway_pk' concatenando 'Nombre Jugador', 'Nacionalidad' y 'Fecha nacimiento',
    y devuelve el DataFrame con la columna 'soccerway_pk' agregada.

    Parámetros:
    df (pd.DataFrame): DataFrame con las columnas necesarias.

    Retorna:
    pd.DataFrame: DataFrame con la columna 'soccerway_pk' agregada.
    """
    df_temp = df.copy() 

    try:
        columnas_necesarias = ["Nombre Jugador", "Nacionalidad", "Fecha Nacimiento"]
        for col in columnas_necesarias:
            if col not in df_temp.columns:
                raise ValueError(f"Falta la columna '{col}' en el archivo CSV.")

        # Convertir la columna 'Fecha nacimiento'
        df_temp["Fecha Nacimiento"] = df_temp["Fecha Nacimiento"].apply(convertir_fecha)

        # Limpiar espacios en blanco en cada celda de las columnas necesarias
        for col in columnas_necesarias:
            df_temp[col] = df_temp[col].apply(limpiar_texto)

        insert_pk = df_temp["Nombre Jugador"] + "_" + df_temp["Nacionalidad"] + "_" + df_temp["Fecha Nacimiento"]
       
        # Crear la llave primaria sin espacios extra
        df.insert(0, "tmkt_pk",insert_pk )

        logging.info("Llave primaria agregada correctamente en tmkt.")
        return df

    except Exception as e:
        logging.error(f"Error: {e}")
        return None
    
def guardar_en_csv(datos, archivo):
    with open(archivo, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=datos.keys())

        # Si el archivo está vacío, escribe los encabezados
        if file.tell() == 0:
            writer.writeheader()

        # Escribe los datos del jugador
        writer.writerow(datos)

def formatear_fechas_soccerway(df, columna_fecha):
    """
    Formatea las fechas de una columna en el DataFrame para que los días siempre tengan dos dígitos.

    Parámetros:
    df (pd.DataFrame): El DataFrame que contiene la columna de fechas.
    columna_fecha (str): El nombre de la columna de fechas que se va a formatear.

    Retorna:
    pd.DataFrame: DataFrame con las fechas formateadas.
    """
    try:
        # Establecer el locale a español para que pandas reconozca los nombres de los meses
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

        # Convertir la columna de fecha a datetime especificando el formato
        df[columna_fecha] = pd.to_datetime(df[columna_fecha], format='%d %B %Y', errors='coerce')

        return df
    
    except Exception as e:
        print(f"Error al formatear las fechas: {e}")
        return df
    
def extraer_fecha_de_columna_besoccer(df, columna_fecha):
    """
    Extrae y formatea las fechas de la columna del DataFrame, quedándose solo con el formato 'DD mes YYYY'.
    
    Parámetros:
    df (pd.DataFrame): DataFrame que contiene la columna con las fechas.
    columna_fecha (str): El nombre de la columna que contiene las cadenas con la fecha en el formato 'Nacido el DD mes YYYY en ...'.
    
    Retorna:
    pd.DataFrame: DataFrame modificado con la nueva columna 'fecha_formateada'.
    """
    # Expresión regular para encontrar la fecha en el formato 'DD mes YYYY'
    patron_fecha = r'Nacido el (\d{1,2}) (\w+) (\d{4})'
    
    # Función para extraer y formatear la fecha
    def formatear_fecha(cadena):
        if not isinstance(cadena, str):  # Verifica si cadena no es un string
            return None  

        cadena = cadena.strip()  # Elimina espacios en blanco al inicio y al final

        patron_fecha = r"(\d{1,2}) (\w+) (\d{4})"  # Asegúrate de definir tu patrón correctamente
        coincidencia = re.search(patron_fecha, cadena)

        if coincidencia:
            dia = coincidencia.group(1).zfill(2)  # Asegura que el día tenga dos dígitos
            mes = coincidencia.group(2)
            anio = coincidencia.group(3)
            return f"{dia} {mes} {anio}"
        
        return None  # Si no se encuentra la fecha

    # Aplicar la función a la columna especificada
    df['birth_date'] = df[columna_fecha].apply(formatear_fecha)
    
    # Devolver el DataFrame modificado
    return df

def agregar_llave_primaria_besoccer(df):
    """
    Agrega una llave primaria 'soccerway_pk' concatenando 'Nombre Jugador', 'Nacionalidad' y 'Fecha nacimiento',
    y devuelve el DataFrame con la columna 'soccerway_pk' agregada.

    Parámetros:
    df (pd.DataFrame): DataFrame con las columnas necesarias.

    Retorna:
    pd.DataFrame: DataFrame con la columna 'soccerway_pk' agregada.
    """
    df_temp = df.copy() 

    try:
        columnas_necesarias = ["Nombre completo", "Nacionalidad", "birth_date"]
        for col in columnas_necesarias:
            if col not in df_temp.columns:
                raise ValueError(f"Falta la columna '{col}' en el archivo CSV.")

        # Limpiar espacios en blanco en cada celda de las columnas necesarias
        for col in columnas_necesarias:
            df_temp[col] = df_temp[col].apply(limpiar_texto)

        insert_pk = df_temp["Nombre completo"] + "_" + df_temp["Nacionalidad"] + "_" + df_temp["birth_date"]
       
        # Crear la llave primaria sin espacios extra
        df.insert(0, "besoccer_pk",insert_pk )

        logging.info("Llave primaria agregada correctamente en besoccer.")
        return df

    except Exception as e:
        logging.error(f"Error: {e}")
        return None
    
def quitar_tildes(texto):
    """
    Elimina los tildes de las letras en un texto.
    
    Parámetros:
    texto (str): Texto del que se deben quitar los tildes.
    
    Retorna:
    str: Texto sin tildes.
    """
    # Normalizar el texto a forma de compatibilidad con decomposición
    texto_normalizado = unicodedata.normalize('NFD', texto)
    # Filtrar los caracteres que no son acentos (diacríticos)
    texto_sin_tildes = ''.join([c for c in texto_normalizado if not unicodedata.combining(c)])
    return texto_sin_tildes

def aplicar_quitar_tildes(df, columna):
    """
    Aplica la función quitar_tildes a una columna del DataFrame y devuelve el DataFrame modificado.
    
    Parámetros:
    df (pd.DataFrame): DataFrame que contiene la columna a modificar.
    columna (str): Nombre de la columna a la que se le deben quitar los tildes.
    
    Retorna:
    pd.DataFrame: DataFrame modificado con la columna sin tildes.
    """
    # Aplicar la función quitar_tildes a la columna especificada
    df[columna] = df[columna].apply(quitar_tildes)
    
    # Devolver el DataFrame modificado
    return df



# Soccerway -------------------------------------------------------------------------

archivos_ligas_soccerway = ["raw_soccerway_primera_cl.csv","raw_soccerway_primera_b_cl.csv","raw_soccerway_segunda_cl.csv","raw_soccerway_primera_b_arg.csv","raw_soccerway_tfa_arg_1.csv","raw_soccerway_tfa_arg_2.csv","raw_soccerway_tfa_arg_3.csv","raw_soccerway_tfa_arg_4.csv"]

# Leemos archivos de soccerway y los unimos -----------------------------------------------------
df_soccerway_primera_cl = leer_csv("raw_soccerway_primera_cl.csv")
df_soccerway_primera_b_cl = leer_csv("raw_soccerway_primera_b_cl.csv")
df_soccerway_segunda_cl = leer_csv("raw_soccerway_segunda_cl.csv")
df_soccerway_primera_b_arg = leer_csv("raw_soccerway_primera_b_arg.csv")
df_soccerway_primera_c_arg = leer_csv("raw_soccerway_primera_c_arg.csv")
df_soccerway_tfa_arg_1 = leer_csv("raw_soccerway_tfa_arg_1.csv")
df_soccerway_tfa_arg_2 = leer_csv("raw_soccerway_tfa_arg_2.csv")
df_soccerway_tfa_arg_3 = leer_csv("raw_soccerway_tfa_arg_3.csv")
df_soccerway_tfa_arg_4 = leer_csv("raw_soccerway_tfa_arg_4.csv")
lista_df_soccerway = [df_soccerway_primera_cl,df_soccerway_primera_b_cl,df_soccerway_segunda_cl,df_soccerway_primera_b_arg,df_soccerway_primera_c_arg,df_soccerway_tfa_arg_1,df_soccerway_tfa_arg_2,df_soccerway_tfa_arg_3,df_soccerway_tfa_arg_4]

#Aplicamos transformaciones ------------------------------------------------
df_soccerway = pd.concat(lista_df_soccerway, ignore_index=True)
df_soccerway =formatear_fechas_soccerway(df_soccerway,"Fecha de nacimiento")
df_soccerway = agregar_llave_primaria_soccerway(df_soccerway)
df_soccerway = aplicar_quitar_tildes(df_soccerway,"soccerway_pk")
archivo_soccerway = "stg_soccerway.csv"
df_soccerway.to_csv(archivo_soccerway, index=False, encoding="utf-8")

# Transfermarkt -------------------------------------------------------------------------

archivos_ligas_transfermarkt = ["raw_transfermarkt_primera_cl.csv","raw_transfermarkt_primera_b_cl.csv","raw_transfermarkt_primera_b_arg.csv"]

# Leemos archivos transfermarkt
df_transfermarkt_primera_cl = leer_csv("raw_transfermarkt_primera_cl.csv")
df_transfermarkt_primera_b_cl = leer_csv("raw_transfermarkt_primera_b_cl.csv")
df_transfermarkt_primera_b_arg = leer_csv("raw_transfermarkt_primera_b_arg.csv")
lista_df_transfermarkt = [df_transfermarkt_primera_cl,df_transfermarkt_primera_b_cl,df_transfermarkt_primera_b_arg]

#Aplicamos transformaciones
df_transfermarkt = pd.concat(lista_df_transfermarkt, ignore_index=True)
df_transfermarkt = agregar_llave_primaria_tmkt(df_transfermarkt)
df_transfermarkt = aplicar_quitar_tildes(df_transfermarkt,"tmkt_pk")
archivo_tmkt = "stg_tmkt.csv"
df_transfermarkt.to_csv(archivo_tmkt, index=False, encoding="utf-8")


# Besoccer -------------------------------------------------------------------------

archivos_ligas_besoccer = ["raw_besoccer_primera_cl.csv","raw_besoccer_primera_b_cl.csv","raw_besoccer_segunda_cl"]

df_besoccer_primera_cl = leer_csv("raw_besoccer_primera_cl.csv")
df_besoccer_primera_b_cl = leer_csv("raw_besoccer_primera_b_cl.csv")
df_besoccer_segunda_cl = leer_csv("raw_besoccer_segunda_cl.csv")
lista_df_besoccer = [df_besoccer_primera_cl,df_besoccer_primera_b_cl,df_besoccer_segunda_cl]

df_besoccer = pd.concat(lista_df_besoccer, ignore_index=True)
df_besoccer = extraer_fecha_de_columna_besoccer(df_besoccer,"birth_date")
df_besoccer = agregar_llave_primaria_besoccer(df_besoccer)
df_besoccer = aplicar_quitar_tildes(df_besoccer,"besoccer_pk")
archivo_besoccer = "stg_besoccer.csv"
df_besoccer.to_csv(archivo_besoccer, index=False, encoding="utf-8")



archivo_csv = "clean_data_final_4.csv"

df_consolidado_aux =pd.merge(df_soccerway,df_transfermarkt, left_on = "soccerway_pk", right_on = "tmkt_pk", how = "left")

df_consolidado =pd.merge(df_consolidado_aux,df_besoccer, left_on = "soccerway_pk", right_on = "besoccer_pk", how = "left")

# Transformaciones Finales
columnas_a_reemplazar = [
    'Salto', 'Estirada', 'Paradas', 'Saques', 'Colocación', 
    'Reflejos', 'Ritmo', 'Tiro', 'Pase', 'Regate', 'Defensa', 
    'Físico', 'ELO',
    '2025_Temporada', '2025_Equipo', '2025_Liga', '2025_Minutos Jugados', 
    '2025_Apariciones', '2025_Alineaciones', '2025_Entra', '2025_Sale', 
    '2025_Comenzó de suplente', '2025_Gol', '2025_Amarilla', 
    '2025_Segunda Amarilla', '2025_Roja', '2024_Temporada', '2024_Equipo', 
    '2024_Liga', '2024_Minutos Jugados', '2024_Apariciones', '2024_Alineaciones', 
    '2024_Entra', '2024_Sale', '2024_Comenzó de suplente', '2024_Gol', 
    '2024_Amarilla', '2024_Segunda Amarilla', '2024_Roja','Valor de Mercado','Edad_x','Fisico'
]

# Filtrar solo las columnas que existen en el DataFrame para evitar errores
columnas_presentes = [col for col in columnas_a_reemplazar if col in df_consolidado.columns]


# Reemplazar "?" y "Desconocido" por 0, y luego rellenar los valores NaN con 0
df_consolidado[columnas_presentes] = df_consolidado[columnas_presentes].replace({"?": 0, "Desconocido": 0}).fillna(0)

# Lista de las columnas que deseas convertir a entero
columnas_entero = ['Salto', 'Estirada', 'Paradas', 'Saques', 'Colocación', 
                   'Reflejos', 'Ritmo', 'Tiro', 'Pase', 'Regate', 'Defensa', 
                   'Físico', 'ELO']

# Convertir las columnas seleccionadas a tipo entero
df_consolidado[columnas_entero] = df_consolidado[columnas_entero].astype(int)

# Lista de columnas a rellenar con "Sin información"
columnas_texto = [
    'Fecha de nacimiento', 'Altura', 'Peso', 'Pie_x', 'Posicion Secundaria', 
    'Link Jugador', 'Agente', 'Fichado', 'Contrato Hasta'
]

# Filtrar solo las columnas que existen en el DataFrame
columnas_presentes_texto = [col for col in columnas_texto if col in df_consolidado.columns]

# Rellenar valores vacíos con "Sin información" en las columnas de texto
df_consolidado[columnas_presentes_texto] = df_consolidado[columnas_presentes_texto].fillna("Sin información")


# Eliminar duplicados y quedarte solo con el primer valor de cada 'soccerway_pk'
df_consolidado = df_consolidado.drop_duplicates(subset="soccerway_pk", keep="first")

col_a_eliminar = [
    "2019/2020_Temporada", "2019/2020_Equipo", "2019/2020_Liga", "2019/2020_Minutos Jugados",
    "2019/2020_Apariciones", "2019/2020_Alineaciones", "2019/2020_Entra", "2019/2020_Sale",
    "2019/2020_Comenzó de suplente", "2019/2020_Gol", "2019/2020_Amarilla", 
    "2019/2020_Segunda Amarilla", "2019/2020_Roja", "tmkt_pk", "Nombre Jugador", 
    "Fecha Nacimiento", "Posicion", "Equipo_y", "Nacionalidad_y", "Pie_y", "besoccer_pk", 
    "Nombre completo", "Nacionalidad", "Edad_y", "birth_date"
]

df_consolidado = df_consolidado.drop(columns=[col for col in col_a_eliminar if col in df_consolidado.columns])
df_consolidado = df_consolidado.dropna(subset=["Nombre"])

# Crear la columna 'Nombre Jugador' concatenando 'Nombre' y 'Apellidos'
df_consolidado['Nombre Jugador'] = df_consolidado['Nombre'] + ' ' + df_consolidado['Apellidos']


columnas_a_convertir = ["Temporada", "2025_Temporada", "2024_Temporada"]

# Convertir las columnas a números, reemplazar NaN con 0 y asegurarse de que sean int
for col in columnas_a_convertir:
    if col in df_consolidado.columns:  # Verifica que la columna exista
        df_consolidado[col] = pd.to_numeric(df_consolidado[col], errors="coerce").fillna(0).astype(int)

# Lista de columnas permitidas
columnas_permitidas = [
    'soccerway_pk', 'Nombre', 'Apellidos','Nombre Jugador', 'Nacionalidad_x', 'Fecha de nacimiento', 
    'Edad_x', 'País de nacimiento', 'Posición', 'Altura', 'Peso', 'Pie_x', 'Equipo_x', 
    'Temporada', 'URL', '2025_Temporada', '2025_Equipo', '2025_Liga', '2025_Minutos Jugados', 
    '2025_Apariciones', '2025_Alineaciones', '2025_Entra', '2025_Sale', '2025_Comenzó de suplente', 
    '2025_Gol', '2025_Amarilla', '2025_Segunda Amarilla', '2025_Roja', '2024_Temporada', 
    '2024_Equipo', '2024_Liga', '2024_Minutos Jugados', '2024_Apariciones', '2024_Alineaciones', 
    '2024_Entra', '2024_Sale', '2024_Comenzó de suplente', '2024_Gol', '2024_Amarilla', 
    '2024_Segunda Amarilla', '2024_Roja', 'Posicion Secundaria', 'Link Jugador', 'Valor de Mercado', 
    'Agente', 'Fichado', 'Contrato Hasta', 'ELO', 'Ritmo', 'Tiro', 'Pase', 'Regate', 'Defensa',
    'Físico', 'Salto', 'Estirada', 'Paradas', 'Saques', 'Colocación', 'Reflejos'
]

# Seleccionar solo las columnas permitidas que existan en el DataFrame
df_consolidado = df_consolidado[[col for col in columnas_permitidas if col in df_consolidado.columns]]

# Diccionario con las columnas renombradas (quitando "_x")
columnas_renombradas = {
    'Nacionalidad_x': 'Nacionalidad',
    'Edad_x': 'Edad',
    'Pie_x': 'Pie',
    'Equipo_x': 'Equipo'
}
# Renombrar las columnas si existen en el DataFrame
df_consolidado = df_consolidado.rename(columns=columnas_renombradas)

# Diccionario con los nombres de las ligas
ligas_dict = {
    "PRD": "Primera División de Chile",
    "PA1": "Primera División de Argentina",
    "0": "Desconocido",
    "LPA": "Liga Profesional Argentina",
    "PRA": "Primera B de Argentina",
    "PRB": "Primera B de Chile",
    "SED": "Segunda División de Chile",
    "PRN": "Primera Nacional (Segunda División de Argentina)",
    "PBM": "Primera B Metropolitana (Tercera División de Argentina)",
    "PRC": "Primera C (Cuarta División de Argentina)",
    "TFA": "Torneo Federal A (Argentina)"
}

# Reemplazar los códigos de liga con sus nombres en las columnas 2025_Liga y 2024_Liga
df_consolidado["2025_Liga"] = df_consolidado["2025_Liga"].replace(ligas_dict)
df_consolidado["2024_Liga"] = df_consolidado["2024_Liga"].replace(ligas_dict)


# Verificar si hay valores NaN, inf o -inf en el DataFrame
has_nan = df_consolidado.isna().any().any()
# Filtrar solo las columnas numéricas
df_numeric = df_consolidado.select_dtypes(include=[np.number])

# Verificar si hay valores inf o -inf en las columnas numéricas
has_inf = np.isinf(df_numeric).any().any()
print(f"¿Hay valores inf o -inf?: {has_inf}")

print(f"¿Hay valores NaN?: {has_nan}")

# Ver qué columnas tienen al menos un NaN en df_consolidado
columns_with_nan = df_consolidado.columns[df_consolidado.isna().any()].tolist()
print("columnas con Nan")
print(columns_with_nan)




df_consolidado.to_csv(archivo_csv, index=False, encoding="utf-8")

print(df_consolidado.columns.tolist())

