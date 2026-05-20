import firebase_admin
from firebase_admin import credentials, firestore

# 1. Conexión
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def inicializar_admin():
    # Tu cédula como ID único
    admin_id = "31902000"
    
    data = {
        "nombre_completo": "Juan Luis Laya Rojas",
        "rol": "admin",
        "equipo_id": "STAFF_01",
        "tickets": {
            "comida": 10,
            "tirolina": 1,
            "concierto": 1
        },
        "status": "activo"
    }
    
    db.collection('participantes').document(admin_id).set(data)
    print(f"🚀 [VENV] Perfil {admin_id} creado con éxito.")

# --- ESTO ES LO QUE FALTA PARA QUE "AGARRE" ---
if __name__ == "__main__":
    inicializar_admin()