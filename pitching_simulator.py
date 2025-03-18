import random

from utils import calcular_porcentage, simular_equipo_local_atacando

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
        self.brazo = brazo
        
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
    def __init__(self, equipo_local="Dodgers", equipo_visitante="Oklands", modo="partido_1p"):
        self.reset_cuenta()
        self.outs = 0
        self.inning = 1
        self.parte = "Alta"
        self.hombres_en_base = [False, False, False]
        self.carreras = {"Visitante": 0, "Local": 0}
        self.equipo_bateando = "Visitante"
        self.equipo_local = equipo_local
        self.equipo_rival = equipo_visitante
        self.resultado = f"{equipo_visitante} {self.carreras['Visitante']} - {self.carreras['Local']} {equipo_local}"
        self.modo = modo
        self.actualizar_resultado()

    def actualizar_resultado(self):
        self.resultado = f"{self.equipo_rival} {self.carreras['Visitante']} - {self.carreras['Local']} {self.equipo_local}"
        
        
    def reset_cuenta(self):
        self.strikes = 0
        self.bolas = 0

    def avanzar_corredores(self, tipo_jugada, bases=0):
        """
        Avanza los corredores según el tipo de jugada especificada.
        
        Parámetros:
        - tipo_jugada: str que indica el tipo de jugada ('hit', 'wild_pitch', 'walk', 'home_run').
        - bases: int que indica el número de bases que avanza el bateador en caso de un hit o home run.
        
        Retorna:
        - carreras: int que indica el número de carreras anotadas en la jugada.
        """
        nuevas_bases = [False, False, False]
        carreras = 0

        if tipo_jugada == 'HR':
            # El bateador anota
            carreras += 1
            # Todos los corredores en base anotan
            for base in self.hombres_en_base:
                if base:
                    carreras += 1
            # Las bases quedan vacías
            self.hombres_en_base = [False, False, False]

        elif tipo_jugada == 'HIT' and 1 <= bases <= 3:
            # Avanzar corredores en base según el número de bases del hit
            for i in range(2, -1, -1):
                if self.hombres_en_base[i]:
                    nueva_posicion = i + bases
                    if nueva_posicion >= 3:  # El corredor anota
                        carreras += 1
                    else:
                        nuevas_bases[nueva_posicion] = True
            # Colocar al bateador en la base correspondiente
            nuevas_bases[bases - 1] = True
            self.hombres_en_base = nuevas_bases

        elif tipo_jugada == 'WILD_PITCH':
            # Todos los corredores en base avanzan una base
            for i in range(2, -1, -1):
                if self.hombres_en_base[i]:
                    nueva_posicion = i + 1
                    if nueva_posicion >= 3:  # El corredor anota
                        carreras += 1
                    else:
                        nuevas_bases[nueva_posicion] = True
            # El bateador no avanza en un wild pitch
            self.hombres_en_base = nuevas_bases

        elif tipo_jugada in ['WALK','HBP']:
            # Avanzar corredores solo si son forzados
            if not self.hombres_en_base[0]:
                # Primera base está libre, el bateador toma la primera base
                nuevas_bases[0] = True
            else:
                # Primera base ocupada, forzar avance de corredores
                for i in range(2, -1, -1):
                    if self.hombres_en_base[i]:
                        nueva_posicion = i + 1
                        if nueva_posicion >= 3:  # El corredor anota
                            carreras += 1
                        else:
                            nuevas_bases[nueva_posicion] = True
                # El bateador toma la primera base
                nuevas_bases[0] = True
            self.hombres_en_base = nuevas_bases

        self.carreras[self.equipo_bateando] += carreras
        self.actualizar_resultado()
        return carreras

        
    def avanzar_out(self):
        self.outs += 1
        if self.inning == 9 and self.outs == 3 and self.parte == 'Baja':
            print(self.resultado)
        if self.outs >= 3:
            self.outs = 0
            self.hombres_en_base = [False, False, False]
            if self.modo == "partido_1p":
                self.inning += 1
                carreras = simular_equipo_local_atacando()
                self.carreras['Local'] += carreras
                self.actualizar_resultado()
            else:
                if self.parte == "Alta":
                    self.parte = "Baja"
                    self.equipo_bateando = "Local"
                else:
                    self.parte = "Alta"
                    self.inning += 1
                    self.equipo_bateando = "Visitante"

class JuegoBeisbol:
    MODIFICADORES = {
        "rapida": {"zona": 1.3, "cerca": 0.9, "lejos": 0.5},
        "quebrada": {"zona": 1.1, "cerca": 0.7, "lejos": 0.3}
    }
    MOD_CALIDAD = {1:0.6, 2:0.8, 3:1.0, 4:1.2, 5:1.5}
    MOD_CALIDAD_OUT = {1:1.5, 2:1.2, 3:1.0, 4:0.8, 5:0.6}
    TASAS_SWING = {
        "rapida": {"zona":0.85, "cerca":0.40, "lejos":0.01},
        "quebrada": {"zona":0.72, "cerca":0.52, "lejos":0.05}
    }
    TASAS_CONTACTO = {
        "rapida": {"zona":0.6, "cerca":0.40, "lejos":0.2},
        "quebrada": {"zona":0.5, "cerca":0.35, "lejos":0.1}
    }

    def __init__(self, equipo_local='Vencejos', equipo_visitante="Dodgers"):
        self.jugadores = [
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R'),
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R'),
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R'),
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R'),
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R'),
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R'),
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R'),
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R'),
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R'),
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R'),
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R'),
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R'),
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R'),
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R'),
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R'),
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R'),
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R'),
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R'),
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R'),
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R'),
            Jugador("Mookie Betts", 0.289, 0.370, 100, 28, 3, 24, 650, 'R')
        ]

        if equipo_visitante == "Dodgers":
            self.jugadores_equipo_visitante = self.jugadores[:9]
            self.jugadores_equipo_local = self.jugadores[9:]
        else:
            self.jugadores_equipo_visitante = self.jugadores[9:]
            self.jugadores_equipo_local = self.jugadores[:9]

        self.order_local = 0
        self.order_visitante = 0
        self.bateador_actual = self.jugadores_equipo_visitante[self.order_visitante]
        self.partido = Partido(equipo_local, equipo_visitante)

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
                texto = 'carrera anotada' if carreras == 1 else 'carreras anotadas!'
                resultado["detalles"] += f" {carreras} {texto}!"
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
            porcentage = 0.03 if 'rapida' in tipo_bola else 0.06 
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
                self.partido.actualizar_resultado()
            self.partido.avanzar_out()
            self.partido.reset_cuenta()
            self._siguiente_bateador()
            return resultado
        else:  # Ground out
            if random.random() < 0.3 and sum(self.partido.hombres_en_base) > 0:
                resultado = {"accion": "DOBLE_PLAY", "detalles": "Doble play!", "cambio_cuenta": f"{self.partido.bolas}-{self.partido.strikes}"}
                if self.partido.outs <= 1:
                    self.partido.avanzar_out()
                    self.partido.avanzar_out()
                else:
                    self.partido.avanzar_out()
                self.partido.reset_cuenta()
            else:
                resultado = {"accion": "GROUND_OUT", "detalles": "Rodado para out!", "cambio_cuenta": f"{self.partido.bolas}-{self.partido.strikes}"}
                self.partido.avanzar_out()
                self.partido.reset_cuenta()
            self._siguiente_bateador()
            return resultado

    def _siguiente_bateador(self):
        if self.partido.equipo_bateando == 'Local':
            self.order_local = (self.order_local + 1) % len(self.jugadores_equipo_local)
            self.bateador_actual = self.jugadores_equipo_local[self.order_local]
        else:
            self.order_visitante = (self.order_visitante + 1) % len(self.jugadores_equipo_visitante)
            self.bateador_actual = self.jugadores_equipo_visitante[self.order_visitante]

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
        if ubicacion == "cerca":
            prob_swing /= (self.bateador_actual.obp / 0.350)
        prob_swing = max(0.1, min(0.9, prob_swing))
        
        if random.random() < prob_swing:
            return self._evaluar_swing(calidad, tipo_bola, ubicacion)
        else:
            return self._manejar_no_swing(tipo_bola, ubicacion)

    def _evaluar_swing(self, calidad, tipo_bola, ubicacion):
        mod_tipo = self.MODIFICADORES[tipo_bola][ubicacion]
        mod_calidad = self.MOD_CALIDAD[calidad]
        #prob_hit_ini = calcular_porcentage(self.bateador_actual.avg)
        prob_hit = self.bateador_actual.avg * mod_tipo / mod_calidad
        prob_hit *= 1.515
        
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
        carreras = self.partido.avanzar_corredores('HIT' if bases < 4 else 'HR', bases)
        self.partido.reset_cuenta()
        self._siguiente_bateador()
        if carreras == 4:
            resultado = {
            "accion": "GRAN_SLAM",
            "detalles": f"{self.bateador_actual.nombre} conecta un GRAN SLAM!!!!!",
            "cambio_cuenta": "0-0"}
        else:
            resultado = {
                "accion": f"HIT_{bases}",
                "detalles": f"{self.bateador_actual.nombre} conecta un hit de {bases} base{'s' if bases>1 else ''}!",
                "cambio_cuenta": "0-0"}
        return resultado

    def _generar_out(self, calidad, tipo_bola, ubicacion): 
        prob_contacto = self.TASAS_CONTACTO[tipo_bola][ubicacion]
        prob_contacto *= (self.bateador_actual.avg / 0.280)
        prob_contacto = prob_contacto * self.MOD_CALIDAD_OUT[calidad]
        
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
        brazo = 'Diestro' if self.bateador_actual.brazo == 'R' else 'Zurdo'
        return {
            "inning": self.partido.inning,
            "parte": self.partido.parte,
            "outs": self.partido.outs,
            "cuenta": f"{self.partido.bolas}-{self.partido.strikes}",
            "hombres_en_base": ["1B" if self.partido.hombres_en_base[0] else "", 
                              "2B" if self.partido.hombres_en_base[1] else "", 
                              "3B" if self.partido.hombres_en_base[2] else ""],
            "resultado": self.partido.resultado,
            "bateador_actual": self.bateador_actual.nombre,
            "stats_bateador": f"AVG: {self.bateador_actual.avg}, OBP: {self.bateador_actual.obp}, HR: {self.bateador_actual.hr}, Brazo: {brazo}"
        }
    
    
    def mostrar_jugadores_rival(self):
        """Muestra la lista de jugadores disponibles"""
        for i, jugador in enumerate(self.jugadores_equipo_visitante):
            i+=1
            print(f"{i}: {jugador.nombre} - AVG: {jugador.avg}, OBP: {jugador.obp}, HR: {jugador.hr}, Brazo: {jugador.brazo}")
  

    def simular_temporada(self, num_juegos=144):
        total_hits = 0
        total_pa = 0
        total_hr = 0
        bolas = 0
        fly = 0
        for _ in range(num_juegos):
            self.partido = Partido("Oklands", "Dodgers", "partido_2p")
            while self.partido.inning <= 9:
                resultado = self.lanzar(
                    calidad=3,
                    tipo_bola=random.choices(["rapida", "quebrada"], weights=[0.64,0.36])[0],
                    ubicacion=random.choices(["zona", "cerca", "lejos", "hit_batter", "wild"], weights=[0.55, 0.20, 0.15, 0.05, 0.05] )[0]
                )
                if "HIT" in resultado["accion"] or "GRAN_SLAM" == resultado["accion"]:
                    total_hits += 1
                total_pa += 1
                total_hr += 1 if resultado["accion"] == "GRAN_SLAM" else 0
                bolas += 1 if resultado["accion"] == "BASE_POR_BOLAS" else 0
                bolas += 1 if resultado["accion"] == "HBP" else 0
                fly += 1 if 'Elevado de sacrificio!' in resultado['detalles'] else 0
        total = total_pa - bolas
        total_obp = (bolas + total_hits + fly) / total_pa
        print('\nPartidos: ', num_juegos)
        print('Apariciones: ', total_pa)
        print('Hits: ', total_hits)
        print('Home runs: ', total_hr)
        print('Base por Bolas: ', bolas)
        print(f"AVG: {total_hits/total:.3f}.")
        print(f"OBP {total_obp:.3f}.")

def main():
    print("¡Bienvenido al Simulador de Pitcheo de Béisbol!")
    print("Tú eres el lanzador y debes indicar tus lanzamientos.")

    # Selección de equipo
    print("\nElija el equipo contra el que jugar:")
    print("1. Los Angeles Dodgers")
    print("2. Sacramento Oklands")
    opcion = input("Seleccione una opción (1/2): ")
    
    if opcion == "1":
        equipo_visitante = "Dodgers"
    elif opcion == "2":
        equipo_visitante = "Oklands"
    else:
        print("Opción inválida. Jugando contra los Dodgers por defecto.")
        equipo_visitante = "Dodgers"
    equipo_local = input("Escriba el nombre de su equipo: ")
    juego = JuegoBeisbol(equipo_local, equipo_visitante)
    
    simular = input("Desea simular una temporada (0=No/1=Si): ")
    if simular == "1":
        juego.simular_temporada()
        
    
    print("\nJugadores Rivales:")
    juego.mostrar_jugadores_rival()
    
    while True:
        print("\n" + "="*50)
        estado = juego.obtener_estado_partido()
        print(f"Inning: {estado['parte']} del {estado['inning']}")
        print(f"Outs: {estado['outs']}")
        print(f"Cuenta: {estado['cuenta']}")
        print(f"Hombres en base: {', '.join([b for b in estado['hombres_en_base'] if b])}")
        print(f"Resultado: {juego.partido.resultado}")
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
            
            if resultado["accion"] in ["PONCHE", "OUT", "FLY_OUT", "GROUND_OUT", "HIT_1", "HIT_2", "HIT_3", "GRAN_SLAM", "BASE_POR_BOLAS", "HBP"]:
                juego._siguiente_bateador()
        
        except ValueError:
            print("Entrada inválida. Intenta de nuevo.")
        except KeyboardInterrupt:
            print("\n¡Gracias por jugar!")
            break

if __name__ == "__main__":
    main()