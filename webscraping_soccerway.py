from playwright.async_api import async_playwright
import csv
import asyncio
import sys

async def extract_team_links(page):
    """
    Extrae los enlaces de los equipos de una tabla específica.

    Args:
        page: Instancia de la página de Playwright.

    Returns:
        Una lista de enlaces completos de los equipos.
    """
    # Seleccionar la tabla específica por ID
    table = await page.query_selector("#page_competition_1_block_competition_tables_12_block_competition_league_table_1_table") #esto funciona para chile
    #table = await page.query_selector("#page_competition_1_block_competition_tables_13_block_competition_league_table_1_table") #esto par arg

    try:
        # Esperar el botón y hacer clic en "Rechazarlas todas"
        await page.locator("#onetrust-reject-all-handler").click(timeout=5000)
        print("Cookies rechazadas")
    except:
        print("No apareció el popup de cookies")

    if not table:
        print("Tabla específica no encontrada.")
        return []

    # Selecciona las filas dentro de esa tabla
    rows = await table.query_selector_all("tr.team_rank")

    # Lista para guardar los enlaces
    team_links = []

    # Extraer enlaces de cada fila
    for row in rows:
        # Busca el enlace dentro de la fila
        link_element = await row.query_selector("td.text.team.large-link a")
        if link_element:
            href = await link_element.get_attribute("href")
            if href:
                # Construir el enlace completo
                full_link = f"https://el.soccerway.com{href}"
                team_links.append(full_link)
                print(f"Extrayendo link {full_link}")

    return team_links

async def extract_player_links(page, team_url):
    """

    Extrae los enlaces de los jugadores desde la página de un equipo.

    Args:
        page: Instancia de la página de Playwright.
        team_url: URL del equipo.

    Returns:
        Una lista de enlaces completos de los jugadores.
    """
    try:

        print(f"esperando que cargue pagina")
        # Navegar a la página del equipo
        await page.goto(team_url)

        print("Esperando que cargue la tabla de jugadores...")
        await page.wait_for_selector("#page_team_1_block_team_squad_12-table", timeout=60000) 
        
        
            
        # Seleccionar la tabla de la plantilla (squad container)
        squad_table = await page.query_selector("#page_team_1_block_team_squad_12-table")
        
        print(f"esperando que cargue tabla")

        if not squad_table:
            print(f"No se encontró la tabla de jugadores en {team_url}")
            return []

        # Seleccionar todas las filas dentro de la tabla
        player_rows = await squad_table.query_selector_all("tr")

        # Usar un `set` para almacenar solo enlaces únicos
        player_links_set = set()
        print("Extrayendo enlaces de los jugadores...")

        for row in player_rows:
            # Buscar todos los enlaces dentro de cada fila
            link_elements = await row.query_selector_all("a[href^='/players/']")
            
            for link_element in link_elements:
                href = await link_element.get_attribute("href")
                if href:
                    full_link = f"https://el.soccerway.com{href}"
                    player_links_set.add(full_link)  # Se añade al set para evitar duplicados

        # Convertimos el `set` a una lista para retornar
        player_links = list(player_links_set)
        
        print(f"Se encontraron {len(player_links)} enlaces únicos de jugadores.")
        return player_links
    
    except Exception as e:
        print(f"Error al cargar la página {team_url}: {e}")
        return []



async def extract_player_info(page, player_url):
    """
    Extrae la información de un jugador desde su página.
    
    Args:
        page: Instancia de la página de Playwright.
        player_url: URL del jugador.
    
    Returns:
        Un diccionario con la información del jugador.
    """
    # Navegar a la página del jugador
    await page.goto(player_url)

    # Extraer la información del jugador
    player_info = {}

    # Lista de atributos opcionales con sus selectores
    attributes = {
        'Nombre': 'dd[data-first_name="first_name"]',
        'Apellidos': 'dd[data-last_name="last_name"]',
        'Nacionalidad': 'dd[data-nationality="nationality"]',
        'Fecha de nacimiento': 'dd[data-date_of_birth="date_of_birth"]',
        'Edad': 'dd[data-age="age"]',
        'País de nacimiento': 'dd[data-country_of_birth="country_of_birth"]',
        'Posición': 'dd[data-position="position"]',
        'Altura': 'dd[data-height="height"]',
        'Peso': 'dd[data-weight="weight"]',
        'Pie': 'dd[data-foot="foot"]'
    }

    # Extraer atributos disponibles
    for key, selector in attributes.items():
        element = await page.query_selector(selector)
        player_info[key] = await element.inner_text() if element else None

    # Extraer el title del primer equipo en la tabla de equipos
    team = await page.query_selector('td.team a')
    player_info['Equipo'] = await team.get_attribute('title') if team else None

    # Extraer la temporada actual (season)
    season = await page.query_selector('td.season a')
    player_info['Temporada'] = await season.inner_text() if season else None

    # Agregar la URL del jugador al diccionario
    player_info['URL'] = player_url

    try:
        # Seleccionar la tabla de estadísticas correcta
        stats_table = await page.query_selector("#page_player_1_block_player_career_9_table")

        if stats_table:
            # Obtener todas las filas de la tabla
            rows = await stats_table.query_selector_all("tbody tr")

            # Tomar solo las dos primeras filas (temporada actual y anterior)
            for row in rows[:2]:  
                cols = await row.query_selector_all("td")

                # Asegurar que hay suficientes columnas para extraer datos
                if len(cols) >= 13:
                    team_link = await cols[1].query_selector("a")
                    league_link = await cols[2].query_selector("a")
                    temporada = await cols[0].inner_text()

                    # Agregar cada campo como una nueva clave en el diccionario
                    player_info[f"{temporada}_Temporada"] = temporada
                    player_info[f"{temporada}_Equipo"] = await team_link.get_attribute("title") if team_link else await cols[1].inner_text()
                    player_info[f"{temporada}_Liga"] = await league_link.inner_text() if league_link else await cols[2].inner_text()
                    player_info[f"{temporada}_Minutos Jugados"] = await cols[3].inner_text()
                    player_info[f"{temporada}_Apariciones"] = await cols[4].inner_text()
                    player_info[f"{temporada}_Alineaciones"] = await cols[5].inner_text()
                    player_info[f"{temporada}_Entra"] = await cols[6].inner_text()
                    player_info[f"{temporada}_Sale"] = await cols[7].inner_text()
                    player_info[f"{temporada}_Comenzó de suplente"] = await cols[8].inner_text()
                    player_info[f"{temporada}_Gol"] = await cols[9].inner_text()
                    player_info[f"{temporada}_Amarilla"] = await cols[10].inner_text()
                    player_info[f"{temporada}_Segunda Amarilla"] = await cols[11].inner_text()
                    player_info[f"{temporada}_Roja"] = await cols[12].inner_text()

    except Exception as e:
        logging.warning(f"No se pudieron extraer las temporadas de {player_url}: {e}")

    return player_info

# Función para guardar los datos en un archivo CSV
def guardar_en_csv(datos, archivo):
    with open(archivo, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=datos.keys())

        # Si el archivo está vacío, escribe los encabezados
        if file.tell() == 0:
            writer.writeheader()

        # Escribe los datos del jugador
        writer.writerow(datos)


async def main(url, output_csv):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)  # Cambia a False si quieres ver el navegador
        context = await browser.new_context()
        page = await context.new_page()

        # Navega a la página
        await page.goto(url)

        try:
            # Intentar cerrar el popup de cookies si existe
            await page.locator("#onetrust-reject-all-handler").click(timeout=5000)
            print("Cookies rechazadas")
        except:
            print("No apareció el popup de cookies")

        # Extraer enlaces de los equipos
        team_links = await extract_team_links(page)

        all_player_links = []
        for team_url in team_links:
            player_links = await extract_player_links(page, team_url)
            all_player_links.extend(player_links)

        print(f"Se extrajeron {len(all_player_links)} jugadores")

        # Guardar los datos de los jugadores en un archivo CSV
        for player_url in all_player_links:
            try:
                print(f"Extrayendo información de: {player_url}")
                player_info = await extract_player_info(page, player_url)
                if player_info:  # Verifica que la extracción fue exitosa
                    guardar_en_csv(player_info, output_csv)
                else:
                    print(f"⚠️ No se pudo extraer información de {player_url}")
            except Exception as e:
                print(f"❌ Error al procesar {player_url}: {e}")

        await browser.close()

# Manejo de argumentos
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python webscraping_soccerway.py <URL> <nombre_archivo_csv>")
        sys.exit(1)

    url = sys.argv[1]
    output_csv = sys.argv[2]

    # Ejecutar main con los parámetros recibidos
    asyncio.run(main(url, output_csv))
    print("Programa finalizado")