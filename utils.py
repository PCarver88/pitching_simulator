# Traer aqui funciones auxiliares
import random
import math

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
        return carreras



def calcular_porcentage(average):
    percent = average * 100
    num_tiradas = random.uniform(2.35, 2.75) # He calculado que se lanzan 2.55 bolas por vez al plato restando bolas malas
    T = 100 * (1 - math.pow(1 - percent/100, 1/num_tiradas))
    return round(T/100, 3)


def simular_equipo_local_atacando():
    return random.choices([0,1,2,3,4,5,6], weights=[0.50, 0.16, 0.12, 0.08, 0.07, 0.05,0.02])[0]



def avanzar_corredores_mal(self, tipo_jugada, bases=0):
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