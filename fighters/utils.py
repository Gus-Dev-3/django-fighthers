# mi_aplicacion/utils.py
import re
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone

def extract_tournament_id(url: str) -> str:
    parsed_url = urlparse(url)
    path = parsed_url.path
    match = re.search(r'/tournament/([^/]+)/', path)
    if match:
        return match.group(1)
    else:
        raise ValueError("No se pudo encontrar el identificador del torneo en la URL.")




def has_passed_and_more_than_3_days(timestamp):
        if not timestamp:
            return False
        
        # Convertir timestamp a datetime
        event_date = datetime.utcfromtimestamp(timestamp)
        # Obtener la fecha y hora actual
        now = datetime.utcnow()
        # Calcular la diferencia
        delta = now - event_date
        
        # Verificar si ha pasado más de 3 días
        return delta > timedelta(days=0)
    


