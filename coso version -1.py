import os
import csv
from collections import deque

STOPWORDS = {"n/a", "none", "null", "nan", "undefined", "unknown", "empty", "void", "nil", "zero", "false", "no data"}

def is_stopword(termino):
    """
    FIX: ahora también trata el string vacío "" como stopword.
    Antes, un país vacío ("") no estaba en STOPWORDS, así que se indexaba
    como si fuera un país real y, peor aún, se usaba para armar el grafo
    social (ver más abajo), uniendo a todos los jugadores sin país en un
    solo grupo ficticio.
    """
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


class Node:
    def __init__(self, data):
        self.data = data
        self.siguiente = None


class ListaEnlazada:
    def __init__(self):
        self.head = None

    def insertar(self, data):
        nuevo_nodo = Node(data)
        if self.head is None:
            self.head = nuevo_nodo
        else:
            actual = self.head
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo

    def buscar(self, data):
        resultados = ListaEnlazada()
        actual = self.head
        while actual:
            if actual.data == data:
                resultados.insertar(actual.data)
            actual = actual.siguiente
        return resultados

    def vacia(self):
        return self.head is None


class Grafo:
    def __init__(self):
        # Cada clave será un ID de jugador y su valor será una ListaEnlazada propia [cite: 66]
        self.adjacencia = {}

    def agregar_vertice(self, usuario_id):
        if usuario_id not in self.adjacencia:
            self.adjacencia[usuario_id] = ListaEnlazada()

    def agregar_arista(self, usuario_A, usuario_B):
        # Al ser un grafo no dirigido, se agrega en ambos sentidos [cite: 41, 67]
        self.agregar_vertice(usuario_A)
        self.agregar_vertice(usuario_B)

        # Validar que no existan bucles (un usuario consigo mismo) [cite: 67]
        if usuario_A == usuario_B:
            return

        # Validar que no se dupliquen las aristas [cite: 67]
        if not self.son_amigos(usuario_A, usuario_B):
            self.adjacencia[usuario_A].insertar(usuario_B)
            self.adjacencia[usuario_B].insertar(usuario_A)

    def son_amigos(self, usuario_A, usuario_B):
        actual = self.adjacencia[usuario_A].head
        while actual:
            if actual.data == usuario_B:
                return True
            actual = actual.siguiente
        return False


def formatear_speedrun(registro, numero=None):
    """
    NUEVO: presentación legible de un resultado del buscador de términos.
    Antes se usaba print(actual.data), que mostraba el __repr__ crudo del
    objeto (una sola línea con todos los atributos pegados). Ahora se
    muestra en un bloque con etiquetas, más fácil de leer.
    """
    encabezado = f"[{numero}] " if numero is not None else ""
    categoria = registro.archivo.split('.')[0]
    lineas = [
        f"{encabezado}{registro.player_name or 'N/A'} ({registro.player_country or 'N/A'})",
        f"    Categoría: {categoria}  |  Plataforma: {registro.platform}  |  Puesto: {registro.place}°",
        f"    Tiempo: {registro.primary_time_seconds}s  |  Verificado: {registro.verified_date}",
        f"    ID run: {registro.id}  |  Link: {registro.links}",
    ]
    return "\n".join(lineas)


def formatear_contacto(player_id, jugadores):
    """NUEVO: muestra un contacto del grafo como 'Nombre (País) [ID]' en vez
    de solo el ID crudo, para que los grados de conexión sean legibles."""
    j = jugadores.get(player_id)
    if j is None:
        return f"(desconocido) [ID: {player_id}]"
    return f"{j.player_name or 'N/A'} ({j.player_country or 'N/A'}) [ID: {player_id}]"


def resolver_usuario(entrada, jugadores, indice_nombres):
    """
    NUEVO: permite que la búsqueda en el grafo acepte tanto el ID exacto de
    un jugador como su nombre (igual que el buscador de términos acepta
    texto libre). Devuelve una lista de player_id que coinciden:
      - lista vacía        -> no se encontró nada
      - lista de 1 elemento -> coincidencia única, se puede usar directo
      - lista de 2+ elementos -> nombre ambiguo, hay que desambiguar por ID
    """
    entrada = entrada.strip()
    if entrada in jugadores:
        return [entrada]
    return indice_nombres.get(entrada.lower(), [])


def _fila_esta_vacia(fila):
    """FIX: 'if fila == {}' nunca era True con csv.DictReader (una línea en
    blanco produce un dict con valores vacíos, no un dict vacío). Ahora se
    detecta correctamente una fila sin datos útiles."""
    return not any(v and v.strip() for v in fila.values() if v is not None)


def _encontrar_carpeta_datos(carpeta):
    """FIX: la ruta original 'tarea/archive' estaba hardcodeada y no existe
    en este entorno. Si la carpeta pedida no existe, se buscan alternativas
    razonables (carpeta 'archive' junto al script, o el propio directorio
    del script) antes de fallar con un mensaje claro."""
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
        "Ajusta la variable CARPETA_DATOS al inicio del bloque principal."
    )


# Abre cada archivo para crear objeto speedrun y luego lo guarda en los índices
def cargarDatasets(carpeta):
    carpeta = _encontrar_carpeta_datos(carpeta)

    indice_posts = {}
    indice_usuarios = {}
    indice_invertido = {}
    jugadores = {}
    indice_nombres = {}  # NUEVO: nombre normalizado -> lista de player_id

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
                    # FIX: fila con datos corruptos/incompletos que no se pueden
                    # convertir (ej. place o tiempos vacíos). Se omite en vez de
                    # tumbar todo el programa.
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

                # FIX: antes, cuando player_id venía vacío ("" ), todos esos
                # registros se agrupaban bajo la misma clave "" en 'jugadores'
                # e 'indice_usuarios', mezclando corredores distintos como si
                # fueran uno solo. Ahora esas filas se indexan igual en
                # indice_posts (para el buscador de términos) pero NO entran
                # a 'jugadores' ni a 'indice_usuarios' ni al grafo social,
                # porque no hay forma confiable de identificar a esa persona.
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

                    # NUEVO: se indexa el nombre (normalizado) para poder
                    # buscar en el grafo por nombre, igual que el buscador
                    # de términos. Se guarda una lista porque dos jugadores
                    # distintos podrían compartir el mismo nombre.
                    nombre_norm = fila["player_name"].strip().lower()
                    if nombre_norm:
                        if nombre_norm not in indice_nombres:
                            indice_nombres[nombre_norm] = []
                        if player_id not in indice_nombres[nombre_norm]:
                            indice_nombres[nombre_norm].append(player_id)

                indice_posts[registro.id] = registro

    # --- CONSTRUCCIÓN DEL GRAFO ---
    # FIX: en vez de comparar TODOS los pares de jugadores (O(n²) sobre el
    # total, incluyendo países vacíos que antes formaban una camarilla
    # ficticia), se agrupa primero por país válido y solo se conectan los
    # jugadores dentro de cada grupo. Esto es más rápido y elimina el bug
    # de los países vacíos.
    grafo_social = Grafo()

    for id_jugador in jugadores.keys():
        grafo_social.agregar_vertice(id_jugador)

    grupos_por_pais = {}
    for pid, j in jugadores.items():
        pais_norm = (j.player_country or "").lower().strip()
        if is_stopword(pais_norm):
            continue  # país vacío o inválido: no se usa para crear amistades
        grupos_por_pais.setdefault(pais_norm, []).append(pid)

    for pais, ids in grupos_por_pais.items():
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                grafo_social.agregar_arista(ids[i], ids[j])

    # NUEVO: se retornan también 'jugadores' e 'indice_nombres' para poder
    # resolver búsquedas por nombre en el sistema de grados de conexión.
    return indice_posts, indice_invertido, grafo_social, jugadores, indice_nombres


# Algoritmo BFS por Niveles [cite: 75]
def obtener_grados_conexion(grafo, usuario_raiz):
    if usuario_raiz not in grafo.adjacencia:
        return None, None, None

    visitados = set()
    cola = deque()

    primer_grado = set()
    segundo_grado = set()
    tercer_grado = set()

    cola.append(usuario_raiz)
    visitados.add(usuario_raiz)

    nivel_actual = 1

    while cola and nivel_actual <= 3:
        nodos_en_nivel = len(cola)

        for _ in range(nodos_en_nivel):
            actual_id = cola.popleft()

            lista_amigos = grafo.adjacencia[actual_id]
            nodo_actual_amigo = lista_amigos.head

            while nodo_actual_amigo:
                amigo_id = nodo_actual_amigo.data

                if amigo_id not in visitados:
                    visitados.add(amigo_id)
                    cola.append(amigo_id)

                    if nivel_actual == 1:
                        primer_grado.add(amigo_id)
                    elif nivel_actual == 2:
                        segundo_grado.add(amigo_id)
                    elif nivel_actual == 3:
                        tercer_grado.add(amigo_id)

                nodo_actual_amigo = nodo_actual_amigo.siguiente

        nivel_actual += 1

    return primer_grado, segundo_grado, tercer_grado

if __name__ == "__main__":
    # FIX: ajusta esta ruta a donde tengas tus CSV. Si no existe, el código
    # intentará automáticamente la carpeta del script y el directorio actual.
    CARPETA_DATOS = "archive"

    posts, indice_invertido, grafo_social, jugadores, indice_nombres = cargarDatasets(CARPETA_DATOS)

    # 1. Buscador de términos (Entrega I)
    print("--- BUSCADOR DE TÉRMINOS ---")
    buscador = input("Ingresa un término a buscar: ")
    resultado = indice_invertido.get(buscador.lower().strip())

    if resultado is None:
        print("No se encontraron resultados")
    else:
        actual = resultado.head
        contador = 1
        while actual is not None:
            print(formatear_speedrun(actual.data, contador))
            print("-" * 60)
            actual = actual.siguiente
            contador += 1

    print("\n--- SISTEMA DE GRADOS DE CONEXIÓN ---")
    for i in range(3):
        entrada = input(f"\n[{i+1}/3] Ingrese el ID o el nombre del usuario raíz: ")

        
        candidatos = resolver_usuario(entrada, jugadores, indice_nombres)

        if not candidatos:
            print("El usuario no existe en la red (ni por ID ni por nombre).")
            continue

        if len(candidatos) > 1:
            print("Ese nombre no es único, encontré varios jugadores. "
                  "Vuelve a intentarlo usando el ID exacto:")
            for pid in candidatos:
                print(f"  - {formatear_contacto(pid, jugadores)}")
            continue

        usuario_id = candidatos[0]
        g1, g2, g3 = obtener_grados_conexion(grafo_social, usuario_id)

        if g1 is None:
            print("El usuario no existe en la red.")
        else:
            print(f"Usuario raíz: {formatear_contacto(usuario_id, jugadores)}")
            print("-> Contactos de 1° Grado (Amigos directos):")
            print(*(f"     {formatear_contacto(pid, jugadores)}" for pid in g1), sep="\n") if g1 else print("     (ninguno)")
            print("-> Contactos de 2° Grado (Amigos de amigos):")
            print(*(f"     {formatear_contacto(pid, jugadores)}" for pid in g2), sep="\n") if g2 else print("     (ninguno)")
            print("-> Contactos de 3° Grado (Amigos lejanos):")
            print(*(f"     {formatear_contacto(pid, jugadores)}" for pid in g3), sep="\n") if g3 else print("     (ninguno)")