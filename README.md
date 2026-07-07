# Proyecto estructura de datos (Entrega 2 y 3)

Este archivo sirve de instructivo para utilizacion del codigo.

# defensa. 
el codigo se mantiene en 5 archivos que se basan en la entrega 2 y 3.
* **nodos.py**: Define las estructuras de datos dinámicas fundamentales en memoria dinámica (Clases "Node", "ListaEnlazada" y "Grafo").
* **estructura.py**: Contiene los modelos entidad-relación del dominio ("jugador" y "speedrun" ) junto con el motor de lectura y preprocesamiento de archivos CSV ("cargarDatasets").
* **procesar.py**: Aloja el algoritmo de recorrido por anchura (BFS) por niveles para el cálculo de los grados de conexión social.
* **Hash.py**: Implementa la estructura de la tabla hash propia, la función de dispersión djb2 truncada a 32 bits y los métodos de resolución de colisiones por encadenamiento separado.
* **main.py**: Actúa como el orquestador principal del sistema, gestionando el flujo global y la interfaz de consola interactiva para el usuario.


## Estructuras de Datos Utilizadas
### 1. Índice Invertido
Implementado sobre una estructura asociativa donde cada clave corresponde a un término normalizado (filtrado de stop words) y el valor apunta a una estructura lineal dinámica del tipo "ListaEnlazada". Permite realizar búsquedas cruzadas eficientes de registros sin escaneos secuenciales exhaustivos.

### 2. Grafo No Dirigido
Modelado mediante una lista de adyacencia construida sobre la implementación propia de "ListaEnlazada". Los vértices representan a los jugadores únicos y las aristas simétricas definen conexiones competitivas compartidas (dentro de un umbral de ranking parametrizado), garantizando la ausencia de bucles y aristas duplicadas.
### 3. Tabla Hash Propia
Estructura construida desde cero utilizando un arreglo estático de punteros a nodos de tipo "NodeHash". Las colisiones se resuelven mediante encadenamiento separado utilizando las sublistas dinámicas desarrolladas.

## Requisitos
* Un PC (que prenda.)
* Python 3.8 o superior.
* Dataset utilizado [Link](https://www.kaggle.com/datasets/mcpenguin/super-mario-64-speedruns)


# Instalacion y ejecucion.
### paso 1.
Clonar el proyecto con
```powershell
Git Clone https://github.com/NashoYaite/tarea_estructuras_de_datos
```
Ejemplo:
carpeta raiz/
├── archive/   
├── estructura.py/   
├── Hash.py/       
├── nodos.py/    
└── Procesar.py/           
└── Main.py/           

### paso 2. (Ejecucion)
Para ejecutar el proyecto utiliza el "Main.py" donde a traves de la terminal puedes hacer consultas.

