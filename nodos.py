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
        self.adjacencia = {}

    def agregar_vertice(self, usuario_id):
        if usuario_id not in self.adjacencia:
            self.adjacencia[usuario_id] = ListaEnlazada()

    def agregar_arista(self, usuario_A, usuario_B):
        self.agregar_vertice(usuario_A)
        self.agregar_vertice(usuario_B)

        if usuario_A == usuario_B:
            return

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