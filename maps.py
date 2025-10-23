"""
Programa: ruta_optima_latam_oop.py
Descripción:
Versión orientada a objetos del programa de ruta óptima en LATAM.
- Usa grafos completos entre ciudades representativas de Latinoamérica (lat/lon).
- Calcula una ruta optimizada (Nearest Neighbor + 2-opt) para visitar N ciudades.
- Calcula precio por tramo y total, con moneda y precio por km configurables.

Autor: Asistente - versión optimizada con clases
"""

import math
import itertools
import unicodedata

# ---------------------------
# Datos base: ciudades LATAM
# ---------------------------
CITIES = {
    "Bogota": (4.7110, -74.0721),
    "Medellin": (6.2442, -75.5812),
    "Cali": (3.4516, -76.5320),
    "Cartagena": (10.3910, -75.4794),
    "Caracas": (10.4806, -66.9036),
    "Quito": (-0.1807, -78.4678),
    "Guayaquil": (-2.1700, -79.9224),
    "Lima": (-12.0464, -77.0428),
    "Santiago": (-33.4489, -70.6693),
    "BuenosAires": (-34.6037, -58.3816),
    "Montevideo": (-34.9011, -56.1645),
    "Asuncion": (-25.2637, -57.5759),
    "LaPaz": (-16.4897, -68.1193),
    "Sucre": (-19.0196, -65.2619),
    "Brasilia": (-15.7939, -47.8828),
    "SaoPaulo": (-23.5505, -46.6333),
    "RioDeJaneiro": (-22.9068, -43.1729),
    "CiudadMexico": (19.4326, -99.1332),
    "Guadalajara": (20.6597, -103.3496),
    "Monterrey": (25.6866, -100.3161),
    "Havana": (23.1136, -82.3666),
    "SanJoseCR": (9.9281, -84.0907),
    "PanamaCity": (8.9824, -79.5199),
    "SantoDomingo": (18.4861, -69.9312),
    "Tegucigalpa": (14.0723, -87.1921),
    "Managua": (12.1140, -86.2362),
    "SanSalvador": (13.6929, -89.2182),
    "BelizeCity": (17.5046, -88.1962),
}

class CalculadoraDistancias:
    RADIO_TIERRA_KM = 6371.0

    @staticmethod
    def haversine(coord1, coord2):
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = (math.sin(dphi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return CalculadoraDistancias.RADIO_TIERRA_KM * c

class GrafoCiudades:
    def __init__(self, ciudades_coords):
        self.nodos = list(ciudades_coords.keys())
        self.coordenadas = ciudades_coords
        self.distancias = {}
        self._construir_grafo()

    def _construir_grafo(self):
        for u, v in itertools.permutations(self.nodos, 2):
            d = CalculadoraDistancias.haversine(self.coordenadas[u], self.coordenadas[v])
            self.distancias[(u, v)] = d

    def peso(self, u, v):
        return self.distancias.get((u, v), float('inf'))

class RutaOptima:
    def __init__(self, grafo):
        self.grafo = grafo

    def _longitud_ruta(self, ruta):
        return sum(self.grafo.peso(ruta[i], ruta[i + 1]) for i in range(len(ruta) - 1))

    def _nearest_neighbor(self, inicio):
        no_visitadas = set(self.grafo.nodos)
        ruta = [inicio]
        no_visitadas.remove(inicio)
        actual = inicio
        while no_visitadas:
            siguiente = min(no_visitadas, key=lambda x: self.grafo.peso(actual, x))
            ruta.append(siguiente)
            no_visitadas.remove(siguiente)
            actual = siguiente
        return ruta

    def _two_opt(self, ruta):
        mejor = ruta[:]
        mejor_long = self._longitud_ruta(mejor)
        mejoro = True
        while mejoro:
            mejoro = False
            for i in range(1, len(mejor) - 2):
                for j in range(i + 1, len(mejor)):
                    if j - i == 1:
                        continue
                    nueva = mejor[:]
                    nueva[i:j] = mejor[j - 1:i - 1:-1]
                    nueva_long = self._longitud_ruta(nueva)
                    if nueva_long < mejor_long:
                        mejor, mejor_long = nueva, nueva_long
                        mejoro = True
        return mejor

    def calcular_ruta(self, inicio):
        ruta_inicial = self._nearest_neighbor(inicio)
        ruta_opt = self._two_opt(ruta_inicial)
        return ruta_inicial, ruta_opt

class CalculadoraCostos:
    def __init__(self, precio_por_km=0.5, moneda="USD"):
        self.precio_por_km = precio_por_km
        self.moneda = moneda

    def costo(self, distancia_km):
        return distancia_km * self.precio_por_km

    def imprimir_ruta(self, grafo, ruta):
        total_dist, total_cost = 0.0, 0.0
        lineas = []
        for i in range(len(ruta) - 1):
            u, v = ruta[i], ruta[i + 1]
            d = grafo.peso(u, v)
            c = self.costo(d)
            total_dist += d
            total_cost += c
            lineas.append(f"{u} -> {v}: {d:.2f} km | {c:.2f} {self.moneda}")
        lineas.append(f"TOTAL: {total_dist:.2f} km | {total_cost:.2f} {self.moneda}")
        return "\n".join(lineas)

class InterfazConsola:
    def __init__(self):
        self.moneda = input("Ingresa la moneda (por defecto USD): ").strip() or "USD"
        try:
            self.precio_km = float(input("Precio por km (por defecto 0.5): ").strip() or 0.5)
        except ValueError:
            print("Precio inválido, usando 0.5")
            self.precio_km = 0.5
        self.costo = CalculadoraCostos(self.precio_km, self.moneda)

    def listar_ciudades(self):
        print("\nCiudades disponibles:")
        for c in sorted(CITIES.keys()):
            print(" -", c)

    def _normalizar(self, texto):
        # Quita tildes y pasa a minúsculas
        texto = unicodedata.normalize('NFD', texto)
        texto = texto.encode('ascii', 'ignore').decode('utf-8')
        return texto.lower().strip()
    
    def _parsear_ciudades(self, texto):
        partes = [p.strip() for p in texto.split(",") if p.strip()]
        # Mapeo en minúsculas y sin tildes
        ciudades_normalizadas = {self._normalizar(k): k for k in CITIES.keys()}
        resultado = []

        for p in partes:
            p_norm = self._normalizar(p)
            if p_norm not in ciudades_normalizadas:
                raise ValueError(f"Ciudad no encontrada: '{p}'. Usa los nombres listados.")
            resultado.append(ciudades_normalizadas[p_norm])
        return resultado

    def modo_optimizacion(self):
        self.listar_ciudades()
        s = input("\nIngresa las ciudades a visitar (mínimo 2, separadas por coma): ").strip()
        ciudades = self._parsear_ciudades(s)
        if len(ciudades) < 2:
            print("Debes ingresar al menos 2 ciudades.")
            return

        subgrafo = GrafoCiudades({c: CITIES[c] for c in ciudades})
        optimizador = RutaOptima(subgrafo)
        ruta_nn, ruta_opt = optimizador.calcular_ruta(ciudades[0])

        print("\nRuta inicial (Nearest Neighbor):")
        print(self.costo.imprimir_ruta(subgrafo, ruta_nn))
        print("\nRuta optimizada:")
        print(self.costo.imprimir_ruta(subgrafo, ruta_opt))

    def ejecutar(self):
        print("Programa: Mejor ruta en LATAM ")
        while True:
            print("\nMenú:")
            print(" 1 - crear ruta")
            print(" 2 - Mostrar ciudades disponibles")
            print(" 0 - Salir")
            op = input("Opción: ").strip()
            if op == "1":
                try:
                    self.modo_optimizacion()
                except Exception as e:
                    print("Error:", e)
            elif op == "2":
                self.listar_ciudades()
            elif op == "0":
                print("Saliendo...")
                break
            else:
                print("Opción no válida.")

interfaz = InterfazConsola()
interfaz.ejecutar()
