import os
import csv

STOPWORDS = {"n/a", "none", "null", "nan", "undefined", "unknown", "empty", "void", "nil", "zero", "false", "no data"}

def is_stopword(termino):
    if termino.lower().strip() in STOPWORDS:
        return True
    return False

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

#Abre cada archivo para crear objeto speedrun y luego lo guarda en los indices
def cargarDatasets(carpeta):
    indice_posts = {}
    indice_usuarios = {}
    indice_invertido = {}
    jugadores = {}  
    for archivo in os.listdir(carpeta):
        if archivo.endswith('.csv'):
            with open(os.path.join(carpeta, archivo), 'r') as f:
                reader = csv.DictReader(f)
                for fila in reader:
                    if fila == {}:
                        continue
                    categoria = archivo.split('.')[0]
                    registro = speedrun(
                        id = fila["id"],
                        player_id = fila["player_id"],
                        player_name = fila["player_name"],
                        player_country = fila["player_country"],
                        platform = fila["platform"],
                        primary_time_seconds = float(fila["primary_time_seconds"]),
                        real_time_seconds = float(fila["real_time_seconds"]),
                        place = int(fila["place"]),
                        verified = fila["verified"],
                        speedrun_date = fila["speedrun_link"],
                        submitted_date = fila["submitted_date"],
                        archivo = archivo,
                    )
                    terminos = [categoria, fila["platform"], fila["player_country"]]

                    
                    for termino in terminos:
                        termino = termino.lower().strip()

                        if not is_stopword(termino):
                            if not termino in indice_invertido:
                                indice_invertido[termino] = ListaEnlazada()
                            indice_invertido[termino].insertar(registro)
    
                    if not fila["player_id"] in jugadores:
                        jugadores[fila["player_id"]] = jugador(
                            player_id = fila["player_id"],
                            player_name = fila["player_name"],
                            player_country = fila["player_country"],
                        )
                    indice_posts[registro.id] = registro
                    if registro.player_id not in indice_usuarios:
                        indice_usuarios[registro.player_id] = ListaEnlazada()
                    indice_usuarios[registro.player_id].insertar(registro)
            
    indice_amigos = {}
    for id_A, jugador_A in jugadores.items():
        for id_B, jugador_B in jugadores.items():
            if id_A != id_B and jugador_A.player_country == jugador_B.player_country:
                if id_A not in indice_amigos:
                    indice_amigos[id_A] = ListaEnlazada()
                    
                indice_amigos[id_A].insertar(jugador_B)
    return indice_posts, indice_invertido, indice_amigos


class Node:                                                         #guarda un dato y puntero al siguiente nodo
    def __init__(self, data):
        self.data = data
        self.siguiente = None

class ListaEnlazada:
    def __init__(self):
        self.head = None
    
    def insertar(self, data):                                             #agrega un dato al final
        nuevo_nodo = Node(data)
        if self.head is None:
            self.head = nuevo_nodo
        else:
            actual = self.head
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo
    
    def buscar(self, data):                                                  #recore la lista buscando coincidencias y retorna una nueva lista con los resultados
        resultados = ListaEnlazada()
        actual = self.head
        while actual:
            if actual.data == data:
                resultados.insertar(actual.data)
            actual = actual.siguiente
        return resultados

    def vacia(self):                                                                 #retorna true si no tiene elementos
        return self.head is None
    
#Buscador
posts, indice_invertido, indice_amigos = cargarDatasets("C:/Users/aiiwk/Downloads/tarea/tarea/archive")
buscador = input("Ingresa un termino a buscar: ")
resultado = indice_invertido.get(buscador.lower().strip())

if resultado is None:
    print("No se encontraron resultados")
else:
    actual = resultado.head
    while actual is not None:
        print(actual.data)
        actual = actual.siguiente