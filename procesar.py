from collections import deque

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