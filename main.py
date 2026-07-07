from estructura import cargarDatasets
from procesar import obtener_grados_conexion
from Hash import construir_tabla_hash  # entrega 3

def formatear_speedrun(registro, numero=None):
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
    j = jugadores.get(player_id)
    if j is None:
        return f"(desconocido) [ID: {player_id}]"
    return f"{j.player_name or 'N/A'} ({j.player_country or 'N/A'}) [ID: {player_id}]"


def resolver_usuario(entrada, jugadores, indice_nombres):
    entrada = entrada.strip()
    if entrada in jugadores:
        return [entrada]
    return indice_nombres.get(entrada.lower(), [])


if __name__ == "__main__":
    CARPETA_DATOS = "archive"

    #(entrega 1 y 2)
    posts, indice_invertido, grafo_social, jugadores, indice_nombres = cargarDatasets(CARPETA_DATOS)
    
    # entrega 3
    tabla_frecuencias = construir_tabla_hash(indice_invertido)

    print("BUSCADOR DE TÉRMINOS")
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

    print("\nSISTEMA DE GRADOS DE CONEXIÓN")
    for i in range(3):
        entrada = input(f"\n[{i+1}/3] Ingrese el nombre del usuario para calcular su grafo: ")

        candidatos = resolver_usuario(entrada, jugadores, indice_nombres)

        if not candidatos:
            print("El usuario no existe en el dataset")
            continue

        if len(candidatos) > 1:
            print("Ese nombre no es único, se encontraron varios jugadores"
                  "Vuelve a intentarlo usando el ID del jugador:")
            for pid in candidatos:
                print(f"  - {formatear_contacto(pid, jugadores)}")
            continue

        usuario_id = candidatos[0]
        g1, g2, g3 = obtener_grados_conexion(grafo_social, usuario_id)

        if g1 is None:
            print("El usuario no existe en la red")
        else:
            print(f"Usuario raíz: {formatear_contacto(usuario_id, jugadores)}")
            print("Contactos de 1° Grado (Amigos directos):")
            print(*(f"     {formatear_contacto(pid, jugadores)}" for pid in g1), sep="\n") if g1 else print("     (ninguno)")
            print("Contactos de 2° Grado (Amigos de amigos):")
            print(*(f"     {formatear_contacto(pid, jugadores)}" for pid in g2), sep="\n") if g2 else print("     (ninguno)")
            print("Contactos de 3° Grado (Amigos lejanos):")
            print(*(f"     {formatear_contacto(pid, jugadores)}" for pid in g3), sep="\n") if g3 else print("     (ninguno)")

    # entrega 3
    print("\n metricas de la entrega 3")
    print(f"Tamaño de la tabla (M): {tabla_frecuencias.size}")
    print(f"Total de colisiones registradas: {tabla_frecuencias.total_colisiones}")
    print(f"Largo máximo de cadena observado: {tabla_frecuencias.largo_maximo_cadena}")
    print(f"Largo promedio de cadena observado: {tabla_frecuencias.calcular_largo_promedio_cadena()}")

    print("\nTerminos N mas frecuentes")
    try:
        n_solicitado = int(input("Cuantos terminos quieres visualizar:  "))
        top_elementos = tabla_frecuencias.obtener_top_n(n_solicitado)

        print("\n Puesto   | Termino          | Frecuencia (apariciones)")
        print("-" * 60)
        for idx, (term, freq) in enumerate(top_elementos, start=1):
            print(f"{idx}°".ljust(8) + f"| {term}".ljust(18) + f"| {freq} veces")
        print("-" * 60)
    except ValueError:
        print("entrada invalida, usa un entero. (1,2,3, etc bla bla)")