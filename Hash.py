class NodeHash:
    def __init__(self, key, value):
        self.key = key        # terminos (str)
        self.value = value    # (int)
        self.next = None      # puntero hacia el siguiente nodo

class TablaHash:
    def __init__(self, size):
        self.size = size
        self.table = [None] * size
        self.total_colisiones = 0
        self.largo_maximo_cadena = 0

    def _hashDjb2(self, key):
        hash_value = 5381
        for char in key:
            hash_value = (hash_value * 33) + ord(char)
            hash_value = hash_value & 0xFFFFFFFF  # truncado 32bits
        return hash_value % self.size

    def insert(self, key): 
        index = self._hashDjb2(key)

        # si la pos esta vacia
        if self.table[index] is None:
            self.table[index] = NodeHash(key, 1)
            return
        
        actual = self.table[index]
        largoActual = 1  

        while actual is not None:
            if actual.key == key:
                actual.value += 1  
                return
            if actual.next is None:
                actual.next = NodeHash(key, 1) 
                self.total_colisiones += 1  
                largoActual += 1  
                if largoActual > self.largo_maximo_cadena:
                    self.largo_maximo_cadena = largoActual
                return
            largoActual += 1 
            actual = actual.next

    def get(self, key):
        index = self._hashDjb2(key)  
        current = self.table[index]

        while current is not None:
            if current.key == key:
                return current.value
            current = current.next

        return None  # retorna none si no hay nada
    
def obtener_primo_adecuado(N):
    rangos_primos = [
        (500, 1009),
        (1000, 2003),
        (3000, 5003),
        (6000, 10007),
        (13000, 20011),
        (33000, 50021),
        (66000, 100003)
    ]
    for limit, primo in rangos_primos:
        if N <= limit:
            return primo
    return 100003
    
def construir_tabla_hash(indice_invertido):
    N = len(indice_invertido)
    M = obtener_primo_adecuado(N) 
    tablaHash = TablaHash(M)
    
    for termino in indice_invertido:
        lista = indice_invertido[termino]
        actual = lista.head
        while actual is not None:
            tablaHash.insert(termino)  # si funciona
            actual = actual.siguiente
    return tablaHash

        #hola_me_llamo_ignacio #snakecase
        #holaMellamoIgnacio  #camelCase
        #CosasDeLaVida 
        #hola-me-soy-ya KEBAB

