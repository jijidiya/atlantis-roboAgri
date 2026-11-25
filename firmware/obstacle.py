from machine import Pin, time_pulse_us
import time

BROCHE_TRIG = 18        
BROCHE_ECHO = 19        
DISTANCE_ARRET = 20     
DISTANCE_REPRISE = 25   
VITESSE_SON = 0.0343    
DELAI_MAX = 30000      
NB_MESURES = 3          


TRIG = Pin(BROCHE_TRIG, Pin.OUT)
ECHO = Pin(BROCHE_ECHO, Pin.IN)


def mesurer_distance():
    TRIG.value(0)
    time.sleep_us(2)
    TRIG.value(1)
    time.sleep_us(10)
    TRIG.value(0)
    duree = time_pulse_us(ECHO, 1, DELAI_MAX)
    if duree < 0:
        return None
    return duree * VITESSE_SON / 2


def mesurer_distance_fiable():
    mesures = []
    for i in range(NB_MESURES):
        d = mesurer_distance()
        if d is not None:
            mesures.append(d)
        time.sleep_ms(60)
    if len(mesures) == 0:
        return None
    mesures.sort()
    return mesures[len(mesures) // 2]


def obstacle_detecte(distance, deja_arrete):

    if distance is None:
        return False
    if distance <= DISTANCE_ARRET:
        return True
    if distance > DISTANCE_REPRISE:
        return False
    return deja_arrete

if __name__ == "__main__":
    arret = False
    while True:
        d = mesurer_distance_fiable()
        arret = obstacle_detecte(d, arret)
        if d is None:
            print("Aucun écho -> AVANCE")
        elif arret:
            print(d, "cm -> STOP")
        else:
            print(d, "cm -> AVANCE")
