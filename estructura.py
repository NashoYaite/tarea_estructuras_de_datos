import os
import csv
from nodos import ListaEnlazada, Grafo

STOPWORDS = {"n/a", "none", "null", "nan", "undefined", "unknown", "empty", "void", "nil", "zero", "false", "no data"}

def is_stopword(termino):
    t = termino.lower().strip()
    return t == "" or t in STOPWORDS


class jugador:
    def __init__(self, player_id, player_name, player_country):
        self.player_id = player_id
        self.player_name = player_name
        self.player_country = player_country

    def __repr__(self):
        return f"jugador(player_id={self.player_id}, name={self.player_name}, country={self.player_country})"


class speedrun:
    def __init__(self, id, player_id, player_name, player_country,
                 platform, primary_time_seconds, real_time_seconds,
                 place, verified, speedrun_date, submitted_date, archivo):
        self.id = id
        self.player_id = player_id
        self.player_name = player_name
        self.player_country = player_country
        self.platform = platform
        self.primary_time_seconds = primary_time_seconds
        self.real_time_seconds = real_time_seconds
        self.place = place
        self.verified_date = verified
        self.links = speedrun_date
        self.fecha = submitted_date
        self.archivo = archivo

    def __repr__(self):
        return f"speedrun(id={self.id}, player={self.player_name}, place={self.place}, archivo = {self.archivo})"


def _fila_esta_vacia(fila):
    return not any(v and v.strip() for v in fila.values() if v is not None)


def _encontrar_carpeta_datos(carpeta):
    candidatas = [
        carpeta,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), carpeta),
        os.path.dirname(os.path.abspath(__file__)),
        ".",
    ]
    for c in candidatas:
        if os.path.isdir(c) and any(f.endswith(".csv") for f in os.listdir(c)):
            return c
    raise FileNotFoundError(
        f"No se encontró ninguna carpeta con archivos .csv. Se probó: {candidatas}. "
    )


def cargarDatasets(carpeta):
    carpeta = _encontrar_carpeta_datos(carpeta)

    indice_posts = {}
    indice_usuarios = {}
    indice_invertido = {}
    jugadores = {}
    indice_nombres = {}
    mejor_place_por_categoria = {}

    for archivo in os.listdir(carpeta):
        if not archivo.endswith('.csv'):
            continue

        with open(os.path.join(carpeta, archivo), 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for fila in reader:
                if _fila_esta_vacia(fila):
                    continue

                categoria = archivo.split('.')[0]

                try:
                    registro = speedrun(
                        id=fila["id"],
                        player_id=fila["player_id"],
                        player_name=fila["player_name"],
                        player_country=fila["player_country"],
                        platform=fila["platform"],
                        primary_time_seconds=float(fila["primary_time_seconds"]),
                        real_time_seconds=float(fila["real_time_seconds"]),
                        place=int(fila["place"]),
                        verified=fila["verified"],
                        speedrun_date=fila["speedrun_link"],
                        submitted_date=fila["submitted_date"],
                        archivo=archivo,
                    )
                except (ValueError, KeyError) as e:
                    print(f"Aviso: fila omitida en {archivo} por dato inválido ({e})")
                    continue

                terminos = [categoria, fila["platform"], fila["player_country"]]
                for termino in terminos:
                    termino_norm = termino.lower().strip()
                    if not is_stopword(termino_norm):
                        if termino_norm not in indice_invertido:
                            indice_invertido[termino_norm] = ListaEnlazada()
                        indice_invertido[termino_norm].insertar(registro)

                player_id = fila["player_id"].strip()

                if player_id:
                    if player_id not in jugadores:
                        jugadores[player_id] = jugador(
                            player_id=player_id,
                            player_name=fila["player_name"],
                            player_country=fila["player_country"],
                            )
                    if player_id not in indice_usuarios:
                        indice_usuarios[player_id] = ListaEnlazada()
                    indice_usuarios[player_id].insertar(registro)

                    mejores_cat = mejor_place_por_categoria.setdefault(categoria, {})
                    if player_id not in mejores_cat or registro.place < mejores_cat[player_id]:
                        mejores_cat[player_id] = registro.place

                    nombre_norm = fila["player_name"].strip().lower()
                    if nombre_norm:
                        if nombre_norm not in indice_nombres:
                            indice_nombres[nombre_norm] = []
                        if player_id not in indice_nombres[nombre_norm]:
                            indice_nombres[nombre_norm].append(player_id)

                indice_posts[registro.id] = registro

    grafo_social = Grafo()

    for id_jugador in jugadores.keys():
        grafo_social.agregar_vertice(id_jugador)

    VENTANA_RANKING = 3

    for categoria, mejores in mejor_place_por_categoria.items():
        ranking = sorted(mejores.items(), key=lambda par: par[1])
        n = len(ranking)
        for i in range(n):
            pid_i, place_i = ranking[i]
            for j in range(i + 1, n):
                pid_j, place_j = ranking[j]
                if place_j - place_i > VENTANA_RANKING:
                    break
                grafo_social.agregar_arista(pid_i, pid_j)

    return indice_posts, indice_invertido, grafo_social, jugadores, indice_nombres