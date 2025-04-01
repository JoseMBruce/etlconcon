import subprocess
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ligas = {
    "primera_cl": [
        {
            "url" : "https://es.soccerway.com/national/chile/primera-division/2025/regular-season/r85780/",
            "archivo" : "raw_soccerway_primera_cl.csv"

        },
        {
            "url" : "https://www.transfermarkt.es/primera-division-de-chile/startseite/wettbewerb/CLPD",
            "archivo" : "raw_transfermarkt_primera_cl.csv"
        },
        {
            "url" :  "https://es.besoccer.com/competicion/clasificacion/primera_chile_liga_unica",
            "archivo" : "raw_besoccer_primera_cl.csv"
        }

    ],
    "primera_b_cl": [
        {
            "url" : "https://es.soccerway.com/national/chile/primera-b/2025/regular-season/r86051/",
            "archivo" : "raw_soccerway_primera_b_cl.csv"

        },
        {
            "url" : "https://www.transfermarkt.es/primera-b/startseite/wettbewerb/CL2B",
            "archivo" : "raw_transfermarkt_primera_b_cl.csv"
        },
        {
            "url" :  "https://es.besoccer.com/competicion/clasificacion/torneo_transicion_primera_b_chile",
            "archivo" : "raw_besoccer_primera_b_cl.csv"
        }

    ],
    "segunda_cl": [
        {
            "url" : "https://es.soccerway.com/national/chile/segunda-division/2025/regular-season/r85318/",
            "archivo" : "raw_soccerway_segunda_cl.csv"

        },
        {
            "url" :  "https://es.besoccer.com/competicion/clasificacion/segunda_chile",
            "archivo" : "raw_besoccer_segunda_cl.csv"
        }

    ],
    "tercera_a_cl": [
        {
            "url" : "https://es.soccerway.com/national/chile/tercera-a/2025/regular-season/r85331/",
            "archivo" : "raw_soccerway_tercera_a_cl.csv"

        },
        {
            "url" :  "https://es.besoccer.com/competicion/clasificacion/segunda_chile",
            "archivo" : "raw_besoccer_segunda_cl.csv"
        }

    ],
    "primera_b_arg": [
        {
            "url" : "https://es.soccerway.com/national/argentina/prim-b-metro/2025/apertura/r86270/",
            "archivo" : "raw_soccerway_primera_b_arg.csv"

        },
        {
            "url" : "https://www.transfermarkt.es/primera-b-metropolitana-apertura/startseite/wettbewerb/AR3C",
            "archivo" : "raw_transfermarkt_primera_b_arg.csv"
        },
        {
            "url" :  "https://es.besoccer.com/competicion/clasificacion/primera_b_metropolitana",
            "archivo" : "raw_besoccer_primera_b_arg.csv"
        }

    ],
    "segunda_uruguay": [
        {
            "url" : "https://es.soccerway.com/national/uruguay/segunda-division/2025/2nd-phase/r86203/",
            "archivo" : "raw_soccerway_segunda_uruguay.csv"

        },
        {
            "url" : "https://www.transfermarkt.es/segunda-division-profesional/startseite/wettbewerb/URU2",
            "archivo" : "raw_transfermarkt_segunda_uruguay.csv"
        },
        {
            "url" :  "https://www.besoccer.com/Competition/table/transicion_segunda_uruguay",
            "archivo" : "raw_besoccer_segunda_uruguay.csv"
        }

    ]

}


# Ejecutar cada script secuencialmente con manejo de errores
for liga, sitios in ligas.items():
        
    if liga == "primera_b_arg":
        logging.info(f"Ejecutando scraping para {liga}...")

        for sitio in sitios:
            input_url = sitio["url"]
            archivo_salida = sitio["archivo"]

            # Determinar el nombre del script a ejecutar según la liga
            if "soccerway" in input_url:
                script = ["python", "webscraping_soccerway.py", input_url, archivo_salida]
            elif "transfermarkt" in input_url:

                script = ["python", "webscraping_transfermarkt.py", input_url, archivo_salida]
            elif "besoccer" in input_url:
                script = ["python", "webscraping_besoccer.py", input_url, archivo_salida]
            else:
                logging.error(f"URL no reconocida: {input_url}")
                continue

            logging.info(f"Ejecutando {script}...")
            try:
                result = subprocess.run(script, capture_output=True, text=True, check=True)
                logging.info(result.stdout)
            except subprocess.CalledProcessError as e:
                logging.error(f"Error en {script[1]}: {e.stderr}")

logging.info("Ejecución completada.")