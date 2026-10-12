from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import resend

# Cargar credenciales del archivo .env
load_dotenv()

# Si esta en produccion se apaga la documentación
is_production = os.getenv("ENV") == "production"

# Variables de entorno dinámicas (con valores por defecto por si acaso)
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "http://tudominio.com")
EMAIL_FROM = os.getenv("EMAIL_FROM", "Portafolio <formulario@narcisoguzman.com>")

app = FastAPI(
	title="Portafolio Mail API",
	docs_url=None if is_production else "/docs",
	redoc_url=None if is_production else "/redoc",
	openapi_url=None if is_production else "/openapi.json"
)

# Configurar CORS (Permitir que el frontend se comunique con esta API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

# Definir la estructura de datos que esperamos recibir del formulario
class ContactForm(BaseModel):
    nombre: str
    apellido: str
    email: str
    mensaje: str

# Inicialización global de la API key de Resend
resend.api_key = os.getenv("RESEND_API_KEY")

@app.post("/api/contact")
async def send_email(form: ContactForm):
    destinatario = os.getenv("EMAIL_CONTACT")
    extracto_mensaje = form.mensaje[:40] + "..." if len(form.mensaje) > 40 else form.mensaje

    body = f"""Datos del contacto:
----------------------------------------
Nombre: {form.nombre} {form.apellido}
Correo: {form.email}

Mensaje:
----------------------------------------
{form.mensaje}
"""

    try:
        # Llamada directa a la API de Resend para enviar el correo
        r = resend.Emails.send({
            "from": EMAIL_FROM,
            "to": destinatario,
            "reply_to": form.email,
            "subject": f"Portafolio | {form.nombre}: {extracto_mensaje}",
            "text": body
        })
        return {"status": "success", "message": "Correo enviado con éxito.", "data": r}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar el correo: {str(e)}")