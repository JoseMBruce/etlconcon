from playwright.async_api import async_playwright
import asyncio
import logging
import csv
import re
import sys
import os

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Log en la consola
        logging.FileHandler("extract_players.log")  # Log en un archivo
    ]
)


async def scrape_player_data(player_url):
    async with async_playwright() as p:
        # Inicializa el navegador
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Navega a la URL del jugador
        await page.goto(player_url)

        # Extrae los datos
        full_name = await page.locator('.panel-head .panel-subtitle:nth-of-type(2)').text_content()  # Usa el segundo subtítulo
        nationality = await page.locator('.panel-body.stat-list .stat:nth-child(1) .small-row:nth-child(4)').text_content()
        age = await page.locator('.panel-body.stat-list .stat:nth-child(1) .big-row').text_content()
        elo = await page.locator('.panel-body.stat-list .stat:nth-child(4) .round-row.mb5.green span').text_content()

       # Extraer todo el texto relacionado con la fecha de nacimiento
        birth_div = await page.query_selector('div.panel-body.ta-c.mh10')
        birth_date_text = None  # Valor por defecto si no se encuentra la fecha
        
        if birth_div:
            birth_date_text = await birth_div.text_content()  # Extrae todo el texto
        
         # Eliminar espacios en blanco y saltos de línea al principio y al final
        birth_date_text = birth_date_text.strip() if birth_date_text else None
        """
# Lista de los atributos en orden de aparición en la página
        attribute_names = ["salto","estirada","paradas","saques","colocación","reflejos","ritmo", "tiro", "pase", "regate", "defensa", "físico"]

        # Para cada atributo, verificamos si el div correspondiente con la clase cl-name slice-X existe antes de intentar extraerlo
        for idx, attribute in enumerate(attribute_names, start=1):
            # Verificamos si el elemento del atributo existe antes de intentar extraerlo
            attribute_locator = page.locator(f'div.cl-name.slice-{idx} .cname div')
            value_locator = page.locator(f'div.cl-name.slice-{idx} .cvalue')

            try:
                # Si el elemento no está visible, asignamos "Desconocido" para ese atributo
                if not await attribute_locator.is_visible() or not await value_locator.is_visible():
                    attributes[attribute.capitalize()] = "Desconocido"
                else:
                    # Extraemos el nombre y el valor si está visible
                    attribute_name = await attribute_locator.text_content()
                    attribute_value_element = await value_locator.text_content()

                    # Si el valor está presente, lo asignamos, sino asignamos "Desconocido"
                    if attribute_value_element:
                        attributes[attribute_name.strip().capitalize()] = attribute_value_element.strip()
                    else:
                        attributes[attribute_name.strip().capitalize()] = "Desconocido"

            except Exception as e:
                # Si hay un error al extraer el atributo, asignamos "Desconocido"
                print(f"Error al extraer el atributo {attribute.capitalize()}: {e}")
                attributes[attribute.capitalize()] = "Desconocido"

        # Cierra el navegador
        await browser.close()
        """
         # Extraer todos los atributos disponibles
        attributes = {}

        # Buscar todos los elementos de atributos en la página
        attribute_elements = await page.locator('div.cl-name').all()

        for element in attribute_elements:
            try:
                attribute_name = await element.locator('.cname div').text_content()
                attribute_value = await element.locator('.cvalue').text_content()

                # Limpiar texto y guardar en el diccionario
                attributes[attribute_name.strip().capitalize()] = attribute_value.strip() if attribute_value else "Desconocido"
            except:
                continue  # Si falla, simplemente sigue con el siguiente atributo

        await browser.close()

        # Devuelve los datos como un diccionario
        return {
            "Nombre completo": full_name.strip(),
            "Nacionalidad": nationality.strip(),
            "Edad": int(age.strip()) if age.strip().isdigit() else 0,
            "ELO": int(elo.strip()) if elo.strip().isdigit() else 0,
            "birth_date": birth_date_text,
            **attributes  # Incluye los atributos con sus valores
        }
    
async def scrape_team_players(team_url):
    """
    Scrape the names and links of football players from a team's page on BeSoccer.

    Args:
        team_url (str): URL of the team's page on BeSoccer.

    Returns:
        list of dict: A list of dictionaries, each containing 'name' and 'link' of a player.
    """
    players = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(team_url)

        # Wait for the table with players to load
        await page.wait_for_selector("#team_performance")

        # Extract player rows from the table
        rows = await page.query_selector_all("#team_performance .row-body")
        for row in rows:
            name_element = await row.query_selector(".name a")
            if name_element:
                name = (await name_element.inner_text()).strip()
                link = await name_element.get_attribute("href")
                if name and link:
                    players.append({"name": name, "link": link})

        await browser.close()

    return players

async def extract_team_links_besoccer(page):
    """
    Extrae los enlaces de los equipos de una tabla específica en Besoccer.

    Args:
        page: Instancia de la página de Playwright.

    Returns:
        Una lista de enlaces completos de los equipos.
    """
    # Selecciona la tabla de equipos por la clase
    table = await page.query_selector(".table-body.table-custom.competition-result")

    try:
        # Esperar el botón de cookies y rechazar si aparece
        await page.locator("#onetrust-reject-all-handler").click(timeout=5000)
        print("Cookies rechazadas")
    except:
        print("No apareció el popup de cookies")

    if not table:
        print("Tabla específica no encontrada.")
        return []

    # Selecciona las filas dentro de la tabla
    rows = await table.query_selector_all("tr.row-body")

    # Lista para guardar los enlaces de los equipos
    team_links = []

    # Extrae los enlaces de cada fila
    for row in rows:
        # Busca el enlace dentro de la fila (enlace a los equipos)
        link_element = await row.query_selector("td.name a[data-cy='team']")
        if link_element:
            href = await link_element.get_attribute("href")
            if href:
                # Modifica el enlace para agregar 'plantilla/' antes del nombre del equipo
                # Ejemplo: https://es.besoccer.com/equipo/plantilla/colo-colo
                base_url = href.split("/equipo/")[0]  # Parte de la URL hasta "equipo"
                team_name = href.split("/equipo/")[1]  # El nombre del equipo
                full_link = f"{base_url}/equipo/plantilla/{team_name}"
                team_links.append(full_link)
                print(f"Extrayendo link de plantilla {full_link}")

    return team_links

def guardar_en_csv(datos, archivo):
    file_exists = os.path.isfile(archivo)  # Verifica si el archivo ya existe

    with open(archivo, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=ATRIBUTOS)

        # Si el archivo es nuevo, escribe los encabezados
        if not file_exists or file.tell() == 0:
            writer.writeheader()

        # Completar con valores vacíos los atributos faltantes
        complete_data = {field: datos.get(field, "0") for field in ATRIBUTOS}

        # Escribe los datos del jugador
        writer.writerow(complete_data)

async def main(url, output_csv):
    async with async_playwright() as p:
        # Inicializa el navegador y abre una página
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Accede a la URL de la competición
        await page.goto(url)

        # Llamada a la función de extracción
        team_links = await extract_team_links_besoccer(page)

        players = []
        for link in team_links:
            scrape_players = await scrape_team_players(link)
            players.extend(scrape_players)

        print(f"Listado de jugadores:{players}")

        for player in players:
            print(f"Extrayendo datos de: {player['name']}")
            info_player = await scrape_player_data(player['link'])  # Asegúrate de usar await aquí
            print(info_player)
            # Guardamos la información de cada jugador en el archivo CSV
            guardar_en_csv(info_player, output_csv)

        # Cierra el navegador
        await browser.close()

# Lista de atributos fijos (se asegura de que todos los jugadores tengan las mismas columnas)
ATRIBUTOS = [
    "Nombre completo", "Nacionalidad", "Edad", "ELO", "birth_date",
    "Ritmo", "Tiro", "Pase", "Regate", "Defensa", "Físico",
    "Salto", "Estirada", "Paradas", "Saques", "Colocación", "Reflejos"
]

# Manejo de argumentos
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python webscraping_besoccer.py <URL> <nombre_archivo_csv>")
        sys.exit(1)

    url = sys.argv[1]
    output_csv = sys.argv[2]

    asyncio.run(main(url, output_csv))
