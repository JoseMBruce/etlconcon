from playwright.async_api import async_playwright
import asyncio
import csv
import sys

BASE_URL = "https://www.transfermarkt.es"

import logging
from playwright.async_api import async_playwright

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

BASE_URL = "https://www.transfermarkt.es"

async def extract_players_from_club(club_url, club_name):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print(f"Iniciando extracción para el club: {club_name}")

        # Accede a la URL del club
        await page.goto(club_url)

        # Espera a que la lista de jugadores esté cargada
        await page.wait_for_selector(".items")

        # Extrae las filas de la tabla de jugadores que están dentro de #yw1
        player_rows = await page.query_selector_all("#yw1 .items tbody tr")
        print(f"Total de filas en la tabla de jugadores: {len(player_rows)}")

        # Filtra filas válidas que contengan información
        valid_rows = [
            row for row in player_rows if await row.query_selector("td.posrela table.inline-table tr:nth-child(1) td:nth-child(2) a")
        ]
        print(f"Filas válidas con jugadores detectadas: {len(valid_rows)}")

        # Extrae la información de cada jugador
        players = []
        for index, player_row in enumerate(valid_rows):
            try:
                print(f"Procesando jugador {index + 1}/{len(valid_rows)} del club {club_name}")
                
                # Nombre del jugador
                player_name_element = await player_row.query_selector("td.hauptlink a")
                player_name = await player_name_element.inner_text() if player_name_element else "Sin nombre"
                
                # Link al perfil del jugador
                player_link = await player_name_element.get_attribute("href") if player_name_element else ""
                player_link = BASE_URL + player_link if player_link else "Sin link"
                print(f"Jugador detectado: {player_name} - Link: {player_link}")
                
                
                # Posición principal
                position_element = await player_row.query_selector('td.posrela table.inline-table tr:nth-child(2) td:nth-child(1)')
                position = await position_element.inner_text() if position_element else "Sin posición"
                position = position.strip()

                # Valor de mercado
                market_value_element = await player_row.query_selector('td.rechts.hauptlink a')
                market_value = await market_value_element.inner_text() if market_value_element else "Sin valor"

                # Nacionalidad
                nationality_element = await player_row.query_selector("td.zentriert img")
                nationality = await nationality_element.get_attribute("title") if nationality_element else "Sin nacionalidad"

                pie = "Desconocido"
                agente = "Desconocido"
                club_actual = club_name
                fichado = "Desconocido"
                contrato_hasta = "Desconocido"

                # Inicializamos el nombre completo
                full_name = player_name

                # Solo accedemos al perfil del jugador si el enlace es válido
                if player_link != "Sin link":
                    print(f"Accediendo al perfil del jugador: {player_name}")
                    new_page = await browser.new_page()  # Abrir una nueva página
                    await new_page.goto(player_link)

                    try:
                        # Espera a que la sección del nombre completo esté disponible
                        await new_page.wait_for_selector("span.info-table__content.info-table__content--bold", timeout=5000)
                        
                        # Extrae el nombre completo desde el selector
                        full_name_element = await new_page.query_selector("span.info-table__content.info-table__content--bold")
                        if full_name_element:
                            full_name = await full_name_element.inner_text()  # Extrae el nombre completo
                            print(f"Nombre completo extraído: {full_name}")
                        else:
                            logging.warning(f"Nombre completo no encontrado para {player_name}. Usando el nombre encontrado en la lista.")
                    except Exception as e:
                        logging.error(f"Error al obtener el nombre completo para {player_name}: {e}")

                    # Extraer los detalles del jugador como posición secundaria, pie, agente, etc.
                    try:
                        await new_page.wait_for_selector(".detail-position", timeout=5000)  # Espera por el selector
                        secondary_position_element = await new_page.query_selector(
                            "div.detail-position__box div.detail-position__position:nth-child(2) dd.detail-position__position"
                        )
                        secondary_position = position  # Por defecto, igual a la posición principal
                        if secondary_position_element:
                            secondary_position = await secondary_position_element.inner_text()
                            secondary_position = secondary_position.strip()
                            print(f"Posición secundaria detectada para {player_name}: {secondary_position}")
                        
                        # Fecha de nacimiento
                        birth_date_element = await new_page.query_selector('span:has-text("F. Nacim./Edad:") + span')
                        birth_date = await birth_date_element.inner_text() if birth_date_element else "Sin fecha"

                        # Pie
                        pie_element = await new_page.query_selector('span:has-text("Pie:") + span')
                        pie = await pie_element.inner_text() if pie_element else "Desconocido"

                        # Agente
                        agente_element = await new_page.query_selector('span:has-text("Agente:") + span')
                        agente = await agente_element.inner_text() if agente_element else "Desconocido"

                        # Club Actual
                        club_actual_element = await new_page.query_selector('span:has-text("Club actual:") + a')
                        club_actual = await club_actual_element.inner_text() if club_actual_element else club_name

                        # Fichado
                        fichado_element = await new_page.query_selector('span.info-table__content--regular:has-text("Fichado:") + span')
                        fichado = await fichado_element.inner_text() if fichado_element else "Desconocido"
                        fichado = fichado.strip()  # Eliminar posibles espacios extra

                        # Contrato hasta
                        contrato_hasta_element = await new_page.query_selector('span:has-text("Contrato hasta:") + span')
                        contrato_hasta = await contrato_hasta_element.inner_text() if contrato_hasta_element else "Desconocido"
                        contrato_hasta = contrato_hasta.strip()  # Eliminar posibles espacios extra
                    except Exception as e:
                        logging.error(f"Error al obtener detalles para {player_name}: {e}")
                    finally:
                        await new_page.close()

                # Guardar los datos del jugador
                players.append({
                    "full_name": full_name,
                    "birth_date": birth_date,
                    "position": position,
                    "secondary_position": secondary_position,
                    "market_value": market_value,
                    "nationality": nationality,
                    "club_name": club_name,
                    "pie": pie,
                    "agente": agente,
                    "player_link": player_link,
                    "fichado": fichado,
                    "contrato_hasta": contrato_hasta
                })

            except Exception as e:
                logging.error(f"Error al procesar jugador {index + 1}: {e}")

        await browser.close()

        return players


    

async def extract_table(url, output_csv):
    async with async_playwright() as p:
        # Abre un navegador Chromium
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Accede a la URL de Transfermarkt
        await page.goto(url)

        # Espera que la tabla esté cargada
        await page.wait_for_selector("#yw1")

        # Extrae las filas de la tabla
        rows = await page.query_selector_all("#yw1 .items tbody tr")

        # Abre el archivo CSV para escribir los datos
        with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Nombre Jugador", "Fecha Nacimiento", "Posicion","Posicion Secundaria", "Equipo", "Link Jugador", "Valor de Mercado", "Nacionalidad","Pie","Agente","Fichado","Contrato Hasta"])  # Cabecera

            # Itera sobre cada club (en este caso, limita a los primeros N clubes si se necesita)
            for row in rows:
                club_name_element = await row.query_selector("td.hauptlink.no-border-links a")
                club_name = await club_name_element.inner_text() if club_name_element else "Sin equipo"
                club_url_element = await row.query_selector("td.hauptlink.no-border-links a")
                club_url = await club_url_element.get_attribute('href') if club_url_element else ""
                club_url = BASE_URL + club_url if club_url else ""

                # Extrae jugadores de cada club
                players = await extract_players_from_club(club_url, club_name)

                # Guarda los jugadores en el CSV
                for player in players:
                    writer.writerow([
                        player['full_name'],
                        player['birth_date'],
                        player['position'],
                        player['secondary_position'],
                        player['club_name'],
                        player['player_link'],
                        player['market_value'],
                        player['nationality'],
                        player['pie'],
                        player['agente'],
                        player['fichado'],
                        player['contrato_hasta']
                    ])

        # Cierra el navegador
        await browser.close()

# Manejo de argumentos
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python webscraping_transfermarkt.py <URL> <nombre_archivo_csv>")
        sys.exit(1)

    url = sys.argv[1]
    output_csv = sys.argv[2]

    # Ejecutar la función con los argumentos recibidos
    asyncio.run(extract_table(url, output_csv))