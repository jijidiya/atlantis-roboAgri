try:
    import secrets
    URL_SERVEUR = secrets.API_URL
except (ImportError, AttributeError):
    URL_SERVEUR = "http://192.168.1.10:8000"
CHEMIN_PING = "/api/ping/"
CHEMIN_MISSION = "/api/robot/mission"
CHEMIN_MESSAGES = "/api/robot/messages"
CHEMIN_ETAT = "/api/robot/etat"
CHEMIN_SYNC = "/api/robot/messages/sync"

DELAI_POLLING_S = 3          
TIMEOUT_REQUETE_S = 5
DELAI_CONNEXION_MAX_S = 15
DELAI_RECONNEXION_S = 5
SIGNAL_VIE_S = 5
SERVEUR_NTP = "pool.ntp.org" 
DELAIS_REESSAI_S = (3, 6, 12)  
DELAI_REESSAI_MAX_S = 30


TAILLE_MAX_FILE = 100        
TAILLE_PAQUET_SYNC = 20      
PAS_COMPTEUR = 10            
FICHIER_COMPTEUR = "compteur.txt"


BROCHE_HUMIDITE = 34         
BROCHE_ALIM_HUMIDITE = 32    
DELAI_STABILISATION_MS = 200 
NB_LECTURES = 5              
BRUT_MIN_VALIDE = 0          
BRUT_MAX_VALIDE = 4095       
BRUT_SEC = 2800              
BRUT_EAU = 1200

BROCHE_BATTERIE = 35         
RAPPORT_DIVISEUR = (100 + 47) / 47   
TENSION_BATT_MIN = 4.4       
TENSION_BATT_MAX = 6.4       
SEUIL_BATTERIE_FAIBLE = 20  
NB_LECTURES_BATT = 5         


TYPES_MESSAGE = ("mission_recue", "etape_atteinte", "mesure",
                 "changement_etat", "incident")
ETATS_ROBOT = ("repos", "en_deplacement", "en_mesure",
               "arret", "erreur", "hors_ligne")
GRAVITES_INCIDENT = ("info", "avertissement", "bloquant")


INTERVALLE_MESURE_S = 10     