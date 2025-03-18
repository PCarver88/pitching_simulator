import random

class Jugador:
    def __init__(self, nombre, avg, obp, singles, dobles, triples, hr, pa, brazo):
        self.nombre = nombre
        self.avg = avg
        self.obp = obp
        self.singles = singles
        self.dobles = dobles
        self.triples = triples
        self.hr = hr
        self.pa = pa
        
        self.bb_rate = (obp - avg) / (1 - avg) if avg < 1 else 0
        self.total_hits = singles + dobles + triples + hr
        
        if self.total_hits > 0:
            self.single_rate = singles / self.total_hits
            self.double_rate = dobles / self.total_hits
            self.triple_rate = triples / self.total_hits
            self.hr_rate = hr / self.total_hits
        else:
            self.single_rate = 0.7
            self.double_rate = 0.2
            self.triple_rate = 0.02
            self.hr_rate = 0.08

class Partido:
    def __init__(self):
        self.reset_cuenta()
        self.outs = 0
        self.inning = 1
        self.parte = "Alta"
        self.hombres_en_base = [False, False, False]
        self.carreras = {"Visitante": 0, "Local": 0}
        self.equipo_bateando = "Visitante"
        
    def reset_cuenta(self):
        self.strikes = 0
        self.bolas = 0

    def avanzar_corredores(self, tipo_jugada, bases=0):
        nuevas_bases = [False, False, False]
        carreras = 0

        if tipo_jugada == 'HR':
            carreras = 1 + sum(self.hombres_en_base)
            self.hombres_en_base = [False, False, False]
            
        elif tipo_jugada == 'HIT' and 1 <= bases <= 3:
            for i in range(2, -1, -1):
                if self.hombres_en_base[i]:
                    nueva_pos = i + bases
                    if nueva_pos >= 3:
                        carreras += 1
                    else:
                        nuevas_bases[nueva_pos] = True
            nuevas_bases[bases - 1] = True
            self.hombres_en_base = nuevas_bases
            
        elif tipo_jugada == 'WILD_PITCH':
            for i in range(3):
                if self.hombres_en_base[i]:
                    if i == 2:
                        carreras += 1
                    else:
                        nuevas_bases[i + 1] = True
            self.hombres_en_base = nuevas_bases
            
        elif tipo_jugada in ['WALK','HBP']:
            nuevas_bases = [True] + self.hombres_en_base[:2]
            for i in range(3, 0, -1):
                if nuevas_bases[i]:
                    nuevas_bases[i] = False
                    carreras += 1
            self.hombres_en_base = nuevas_bases[:3]

        self.carreras[self.equipo_bateando] += carreras
        return carreras
        
    def avanzar_out(self):
        self.outs += 1
        if self.outs >= 3:
            self.outs = 0
            self.hombres_en_base = [False, False, False]
            if self.parte == "Alta":
                self.parte = "Baja"
                self.equipo_bateando = "Local"
            else:
                self.parte = "Alta"
                self.inning += 1
                self.equipo_bateando = "Visitante"

class JuegoBeisbol:
    BASE_HIT_PROB = 0.108
    MODIFICADORES = {
        "rapida": {"zona": 1.3, "cerca": 0.9, "lejos": 0.5},
        "quebrada": {"zona": 1.1, "cerca": 0.7, "lejos": 0.3}
    }
    MOD_CALIDAD = {1:0.6, 2:0.8, 3:1.0, 4:1.2, 5:1.5}
    TASAS_SWING = {
        "rapida": {"zona":0.75, "cerca":0.45, "lejos":0.01},
        "quebrada": {"zona":0.60, "cerca":0.55, "lejos":0.05}
    }
    TASAS_CONTACTO = {
        "rapida": {"zona":0.85, "cerca":0.50, "lejos":0.2},
        "quebrada": {"zona":0.68, "cerca":0.35, "lejos":0.1}
    }

    def __init__(self, equipo="Dodgers"):
        self.jugadores = [
            Jugador("Shohei Ohtani", 0.307, 0.392, 70, 25, 5, 35, 550, 'L'),
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R'),
            Jugador("Freddie Freeman", 0.341, 0.410, 85, 50, 0, 29, 600, 'L'),
            Jugador("Teoscar Hernández", 0.267, 0.316, 90, 25, 1, 33, 560, 'R'),
            Jugador("Max Muncy", 0.212, 0.333, 60, 20, 0, 36, 580, 'L'),
            Jugador("Michael Conforto", 0.238, 0.330, 70, 15, 0, 15, 400, 'L'),
            Jugador("Tommy Edman", 0.265, 0.324, 90, 20, 5, 13, 600, 'A'),
            Jugador("Will Smith", 0.248, 0.330, 80, 20, 0, 20, 500, 'R'),
            Jugador("Chris Taylor", 0.240, 0.300, 85, 15, 5, 10, 450, 'L'),
            Jugador("Esteury Ruiz", 0.250, 0.310, 100, 15, 5, 5, 500, 'R'),
            Jugador("Zach Gelof", 0.240, 0.320, 85, 20, 2, 15, 550, 'R'),
            Jugador("Lawrence Butler", 0.260, 0.330, 90, 25, 3, 20, 580, 'L'),
            Jugador("Brent Rooker", 0.230, 0.310, 70, 15, 0, 25, 500, 'R'),
            Jugador("Seth Brown", 0.220, 0.300, 60, 20, 2, 20, 480, 'L'),
            Jugador("Gio Urshela", 0.270, 0.320, 95, 25, 1, 10, 550, 'R'),
            Jugador("Luis Urías", 0.245, 0.330, 80, 20, 1, 15, 520, 'R'),
            Jugador("Jhonny Pereda", 0.230, 0.310, 60, 15, 0, 10, 400, 'R'),
            Jugador("Jacob Wilson", 0.250, 0.320, 85, 20, 2, 8, 500, 'R')
        ]

        if equipo == "Dodgers":
            self.jugadores = self.jugadores[:9]
        else:
            self.jugadores = self.jugadores[9:]

        self.order = 0
        self.bateador_actual = self.jugadores[self.order]
        self.partido = Partido()

    def _manejar_hbp(self):
        resultado = {
            "accion": "HBP",
            "detalles": f"{self.bateador_actual.nombre} golpeado por el lanzamiento!",
            "cambio_cuenta": "0-0"
        }
        self.partido.avanzar_corredores('HBP', 1)
        self.partido.reset_cuenta()
        self._siguiente_bateador()
        return resultado

    def _manejar_wild_pitch(self):
        resultado = {
            "accion": "WILD_PITCH",
            "detalles": "Lanzamiento descontrolado!",
            "cambio_cuenta": f"{self.partido.bolas}-{self.partido.strikes}"
        }
        self.partido.bolas += 1
        if self.partido.bolas >= 4:
            resultado["detalles"] += " Base por bolas!"
            resultado["accion"]+= "BASE_POR_BOLAS"
            self.partido.avanzar_corredores('WALK', 1)
            self.partido.reset_cuenta()
            self._siguiente_bateador()
        else:
            carreras = self.partido.avanzar_corredores('WILD_PITCH', 0)
            if carreras > 0:
                resultado["detalles"] += f" {carreras} carrera(s) anotada(s)!"
        return resultado

    def _manejar_lanzamiento_lejos(self):
        self.partido.bolas += 1
        if self.partido.bolas >= 4:
            resultado = {
                "accion": "BASE_POR_BOLAS",
                "detalles": f"{self.bateador_actual.nombre} recibe base por bolas!",
                "cambio_cuenta": "0-0"
            }
            self.partido.avanzar_corredores('WALK', 1)
            self.partido.reset_cuenta()
            self._siguiente_bateador()
        else:
            resultado = {
                "accion": "BOLA",
                "detalles": "Bola fuera de la zona!",
                "cambio_cuenta": f"{self.partido.bolas}-{self.partido.strikes}"
            }
        return resultado

    def _manejar_no_swing(self, tipo_bola, ubicacion):
        if ubicacion == "zona":
            self.partido.strikes += 1
            resultado = {
                "accion": "STRIKE",
                "detalles": "Strike cantado!",
                "cambio_cuenta": f"{self.partido.bolas}-{self.partido.strikes}"
            }
            if self.partido.strikes >= 3:
                resultado["accion"] = "PONCHE"
                resultado["detalles"] = "Ponche!"
                self.partido.avanzar_out()
                self.partido.reset_cuenta()
                self._siguiente_bateador()
            return resultado
        else:
            porcentage = 0.14 if 'rapida' in tipo_bola else 0.24 # 14% de strikes en bola rapida y 24 en quebrada fuera
            if random.random() < porcentage:  
                self.partido.strikes += 1
                resultado = {
                        "accion": "STRIKE",
                        "detalles": "Strike cantado!",
                        "cambio_cuenta": f"{self.partido.bolas}-{self.partido.strikes}"
                    }
                if self.partido.strikes >= 3:
                    resultado["accion"] = "PONCHE"
                    resultado["detalles"] = "Ponche!"
                    self.partido.avanzar_out()
                    self.partido.reset_cuenta()
                    self._siguiente_bateador()
                return resultado
            else:
                self.partido.bolas += 1
                if self.partido.bolas >= 4:
                    resultado = {
                        "accion": "BASE_POR_BOLAS",
                        "detalles": f"{self.bateador_actual.nombre} recibe base por bolas!",
                        "cambio_cuenta": "0-0"
                    }
                    self.partido.avanzar_corredores('WALK', 1)
                    self.partido.reset_cuenta()
                    self._siguiente_bateador()
                else:
                    resultado = {
                        "accion": "BOLA",
                        "detalles": "Bola fuera de la zona!",
                        "cambio_cuenta": f"{self.partido.bolas}-{self.partido.strikes}"
                    }
                return resultado

    def _manejar_contacto_sin_hit(self):
        rand = random.random()
        if rand < 0.4:  # Foul
            if self.partido.strikes < 2:
                self.partido.strikes += 1
            return {
                "accion": "FOUL",
                "detalles": "Foul!",
                "cambio_cuenta": f"{self.partido.bolas}-{self.partido.strikes}"
            }
        elif rand < 0.7:  # Fly out
            resultado = {"accion": "FLY_OUT", "detalles": "Elevado para out!", "cambio_cuenta": f"{self.partido.bolas}-{self.partido.strikes}"}
            if random.random() < 0.1 and self.partido.hombres_en_base[2]:
                resultado["detalles"] = "Elevado de sacrificio! Carrera anotada!"
                self.partido.carreras[self.partido.equipo_bateando] += 1
            self.partido.avanzar_out()
            self._siguiente_bateador()
            return resultado
        else:  # Ground out
            if random.random() < 0.3 and sum(self.partido.hombres_en_base) > 0:
                resultado = {"accion": "DOBLE_PLAY", "detalles": "Doble play!", "cambio_cuenta": f"{self.partido.bolas}-{self.partido.strikes}"}
                self.partido.avanzar_out()
                self.partido.avanzar_out()
            else:
                resultado = {"accion": "GROUND_OUT", "detalles": "Rodado para out!", "cambio_cuenta": f"{self.partido.bolas}-{self.partido.strikes}"}
                self.partido.avanzar_out()
            self._siguiente_bateador()
            return resultado

    def _siguiente_bateador(self):
        self.order = (self.order + 1) % len(self.jugadores)
        self.bateador_actual = self.jugadores[self.order]

    def lanzar(self, calidad, tipo_bola, ubicacion, bateador=None):
        if bateador is not None:
            self.bateador_actual = self.jugadores[bateador]
            
        if ubicacion == "hit_batter":
            return self._manejar_hbp()
        if ubicacion == "wild":
            return self._manejar_wild_pitch()
        if ubicacion == "lejos":
            return self._manejar_lanzamiento_lejos()

        prob_swing = self.TASAS_SWING[tipo_bola][ubicacion]
        prob_swing *= (self.bateador_actual.obp / 0.350)
        prob_swing = max(0.1, min(0.9, prob_swing))
        
        if random.random() < prob_swing:
            return self._evaluar_swing(calidad, tipo_bola, ubicacion)
        else:
            return self._manejar_no_swing(tipo_bola, ubicacion)

    def _evaluar_swing(self, calidad, tipo_bola, ubicacion):
        mod_tipo = self.MODIFICADORES[tipo_bola][ubicacion]
        mod_calidad = self.MOD_CALIDAD[calidad]
        prob_hit = self.BASE_HIT_PROB * mod_tipo / mod_calidad
        prob_hit *= (self.bateador_actual.avg / 0.300)
        prob_hit = max(0.05, min(0.35, prob_hit))
        
        if random.random() < prob_hit:
            return self._generar_hit()
        else:
            return self._generar_out(calidad, tipo_bola, ubicacion)

    def _generar_hit(self):
        rand = random.random()
        if rand < self.bateador_actual.single_rate:
            bases = 1
        elif rand < self.bateador_actual.single_rate + self.bateador_actual.double_rate:
            bases = 2
        elif rand < self.bateador_actual.single_rate + self.bateador_actual.double_rate + self.bateador_actual.triple_rate:
            bases = 3
        else:
            bases = 4
            
        carreras = self.partido.avanzar_corredores('HIT' if bases <4 else 'HR', bases)
        self.partido.reset_cuenta()
        self._siguiente_bateador()
        return {
            "accion": f"HIT_{bases}",
            "detalles": f"{self.bateador_actual.nombre} conecta un hit de {bases} base{'s' if bases>1 else ''}!",
            "cambio_cuenta": "0-0"
        }

    def _generar_out(self, calidad, tipo_bola, ubicacion):
        prob_contacto = self.TASAS_CONTACTO[tipo_bola][ubicacion]
        prob_contacto *= (self.bateador_actual.avg / 0.300)
        
        if random.random() < prob_contacto:
            resultado = self._manejar_contacto_sin_hit()
        else:
            self.partido.strikes += 1
            resultado = {
                "accion": "STRIKE_SWING",
                "detalles": "Swing y falla!",
                "cambio_cuenta": f"{self.partido.bolas}-{self.partido.strikes}"
            }
        if self.partido.strikes >= 3:
            resultado["accion"] = "PONCHE"
            resultado["detalles"] = "Ponche!"
            self.partido.avanzar_out()
            self._siguiente_bateador()
            
        return resultado


    def obtener_estado_partido(self):
        """Retorna un diccionario con el estado actual del partido"""
        return {
            "inning": self.partido.inning,
            "parte": self.partido.parte,
            "outs": self.partido.outs,
            "cuenta": f"{self.partido.bolas}-{self.partido.strikes}",
            "hombres_en_base": ["1B" if self.partido.hombres_en_base[0] else "", 
                              "2B" if self.partido.hombres_en_base[1] else "", 
                              "3B" if self.partido.hombres_en_base[2] else ""],
            "carreras": self.partido.carreras,
            "bateador_actual": self.bateador_actual.nombre,
            "stats_bateador": f"AVG: {self.bateador_actual.avg}, OBP: {self.bateador_actual.obp}, HR: {self.bateador_actual.hr}"
        }
    
    
    def mostrar_jugadores(self):
        """Muestra la lista de jugadores disponibles"""
        for i, jugador in enumerate(self.jugadores):
            i+=1
            print(f"{i}: {jugador.nombre} - AVG: {jugador.avg}, OBP: {jugador.obp}, HR: {jugador.hr}")
  

    def simular_temporada(self, num_juegos=100):
        total_hits = 0
        total_pa = 0
        for _ in range(num_juegos):
            self.partido = Partido()
            while self.partido.inning <= 9:
                resultado = self.lanzar(
                    calidad=random.choices([1,2,3,4,5], weights=[0.05,0.2,0.55,0.2,0.1])[0],
                    tipo_bola=random.choice(["rapida", "quebrada"]),
                    ubicacion=random.choices(["zona", "cerca", "lejos", "hit_batter", "wild"], weights=[0.55,0.25,0.09,0.04,0.07])[0]
                )
                if "HIT" in resultado["accion"]:
                    total_hits += 1
                total_pa += 1
        print(f"AVG simulado: {total_hits/total_pa:.3f}")

def main():
    print("¡Bienvenido al Simulador de Pitcheo de Béisbol!")
    print("Tú eres el lanzador y debes indicar tus lanzamientos.")

    # Selección de equipo
    print("\nElija el equipo contra el que jugar:")
    print("1. Los Angeles Dodgers")
    print("2. Sacramento Oklands")
    opcion = input("Seleccione una opción (1/2): ")
    
    if opcion == "1":
        equipo = "Dodgers"
    elif opcion == "2":
        equipo = "Oklands"
    else:
        print("Opción inválida. Jugando contra los Dodgers por defecto.")
        equipo = "Dodgers"
    
    juego = JuegoBeisbol(equipo)
    print("\nJugadores disponibles:")
    juego.mostrar_jugadores()
    
    while True:
        print("\n" + "="*50)
        estado = juego.obtener_estado_partido()
        print(f"Inning: {estado['parte']} del {estado['inning']}")
        print(f"Outs: {estado['outs']}")
        print(f"Cuenta: {estado['cuenta']}")
        print(f"Hombres en base: {', '.join([b for b in estado['hombres_en_base'] if b])}")
        print(f"Carreras: Visitante {estado['carreras']['Visitante']} - Local {estado['carreras']['Local']}")
        print(f"Bateador actual: {estado['bateador_actual']} ({estado['stats_bateador']})")
        
        print("\nTu lanzamiento:")
        try:
            calidad = int(input("Calidad del lanzamiento (1-5): "))
            if not 1 <= calidad <= 5:
                print("Calidad debe estar entre 1 y 5.")
                continue
            
            tipo = input("Tipo de bola (0=rapida, 1=quebrada): ")
            if tipo not in ["0","1"]:
                print("Tipo debe ser '0' o '1'.")
                continue
            tipo = "rapida" if tipo == "0" else "quebrada"
                
            ubicacion = input("Ubicación (0=zona, 1=cerca, 2=lejos, 3=wild, 4=hit_batter): ")
            MAP_UBICACION = {
                "0": "zona",
                "1": "cerca", 
                "2": "lejos",
                "3": "wild",
                "4": "hit_batter"
            }
            ubicacion = MAP_UBICACION.get(ubicacion, "invalida")

            if ubicacion not in ["zona", "cerca", "lejos", "wild", "hit_batter"]:
                print("Ubicación no válida.")
                continue
                
            resultado = juego.lanzar(calidad, tipo, ubicacion)
            print("\nResultado:")
            print(resultado["detalles"])
            print(f"Cuenta actual: {resultado['cambio_cuenta']}")
            
            if resultado["accion"] in ["PONCHE", "OUT", "FLY_OUT", "GROUND_OUT", "HIT_1", "HIT_2", "HIT_3", "HIT_4", "BASE_POR_BOLAS", "HBP"]:
                juego._siguiente_bateador()
        
        except ValueError:
            print("Entrada inválida. Intenta de nuevo.")
        except KeyboardInterrupt:
            print("\n¡Gracias por jugar!")
            break

if __name__ == "__main__":
    main()