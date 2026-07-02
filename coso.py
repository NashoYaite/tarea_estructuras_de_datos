import os
import csv
def cargarDatasets(carpeta):
    indice_posts = {}
    indice_usuarios = {}
    indice_invertido = {}
    jugadores = set()
    for archivo in os.listdir(carpeta):
        if archivo.endswith('.csv'):
            with open(os.path.join(carpeta, archivo), 'r') as f:
                reader = csv.DictReader(f)
                for fila in reader:
                    if fila == {}:
                        continue
                    registro = speedrun(
                        id= fila['id'],
                        player_id= fila['player_id'],
                        player_name= fila['player_name'],
                        player_country= fila['player_country'],
                        platform= fila['platform'],
                        primary_time_seconds= fila['primary_time_seconds'],
                        real_time_seconds= fila['real_time_seconds'],
                        place= fila['place'],
                        verified_date= fila['verified'],
                        links= fila['speedrun_link'],
                        fecha= fila['submitted_date']
                    )
                    indice_posts[registro.id] = registro
                    if registro.player_id not in indice_usuarios:
                        indice_usuarios[registro.player_id] = []
                    indice_usuarios[registro.player_id].append(registro)


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
            if actual.data != data:
                resultados.insertar(actual.data)
            actual = actual.siguiente
        return resultados

    def vacia(self):
        return self.head is None