import firebase_admin
from firebase_admin import credentials, firestore

# 1. Conectar con las llaves que ya tenemos
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def subir_scouts_masivo(lista_personas):
    batch = db.batch()
    
    for persona in lista_personas:
        # Usamos la cédula como ID del documento para que sea único
        doc_ref = db.collection('participantes').document(persona['cedula'])
        
        # Estructura completa para que la App de Flutter no de error
        datos_completos = {
            "nombre_completo": persona['nombre'],
            "cedula": persona['cedula'],
            "rol": persona.get('rol', 'corredor'), # Si no ponemos rol, por defecto es corredor
            "equipo_id": persona.get('equipo', 'SIN_EQUIPO'),
            "puntuacion_total": 0,
            "status": "activo",
            "tickets": {
                "comida": 2,
                "tirolina": 1,
                "concierto": 1
            }
        }
        
        batch.set(doc_ref, datos_completos)
    
    batch.commit()
    print(f"🚀 ¡Misión cumplida! Se cargaron {len(lista_personas)} scouts a Firebase.")

# --- AQUÍ ES DONDE METES LA DATA ---
# Puedes copiar y pegar de un Excel o lista que tengas
lista_de_inscritos = [
    {"cedula": "12345678", "nombre": "Luiseth Rojas", "equipo": "ROJO_01", "rol": "corredor"},
    {"cedula": "22334455", "nombre": "Carlos Perez", "equipo": "AZUL_02", "rol": "corredor"},
    {"cedula": "99887766", "nombre": "Vicky Amiga", "equipo": "STAFF", "rol": "staff"},
    # Sigue agregando todos los que necesites aquí...
]

if __name__ == "__main__":
    subir_scouts_masivo(lista_de_inscritos)