"""
Clasificador de prioridades.

Estrategia:
1. Intenta clasificar usando un modelo de OpenAI (gpt-5.4-nano).
2. Si la API falla por cualquier motivo, cae al clasificador local
   basado en palabras clave.

El fallback garantiza que el sistema sigue funcionando sin internet
o cuando OpenAI está caído.
"""
import os
from enum import Enum
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

# Cliente lazy: solo se instancia la primera vez que se necesita.
# Si no hay API key configurada, evitamos crear el cliente.
_cliente = None


def _get_cliente():
    global _cliente
    if _cliente is None:
        # Si no hay key, esto fallara y se usara el fallback.
        _cliente = OpenAI()
    return _cliente


# ==================== ESQUEMA DE RESPUESTA ====================
# Definimos el formato exacto que esperamos del modelo.
# El Enum restringe la salida a estas 4 cadenas, ninguna otra.

class NivelPrioridad(str, Enum):
    CRITICA = "critica"
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


class ClasificacionTicket(BaseModel):
    prioridad: NivelPrioridad
    razon: str  # explicacion corta del modelo


# ==================== PROMPT ====================

PROMPT_SISTEMA = (
    "Sos un clasificador de tickets de soporte tecnico. "
    "Asignas una prioridad entre: critica, alta, media, baja.\n\n"
    "Criterios:\n"
    "- CRITICA: caidas totales, perdida de datos, multiples usuarios "
    "afectados, sin acceso a servicios criticos.\n"
    "- ALTA: errores que impiden trabajar a un usuario individual, "
    "fallas importantes.\n"
    "- MEDIA: problemas que ralentizan pero no bloquean, lentitud, "
    "intermitencia.\n"
    "- BAJA: consultas, cambios cosmeticos, mejoras opcionales.\n\n"
    "Devolve la prioridad y una razon breve en una sola frase."
)


# ==================== CLASIFICADOR CON IA ====================

def clasificar_con_ia(descripcion: str, categoria: str) -> tuple[str, str]:
    """
    Llama a OpenAI para clasificar el ticket.
    Retorna (prioridad, razon). Lanza excepcion si falla.
    """
    cliente = _get_cliente()
    respuesta = cliente.chat.completions.parse(
        model="gpt-5.4-nano",
        messages=[
            {"role": "system", "content": PROMPT_SISTEMA},
            {
                "role": "user",
                "content": f"Categoria: {categoria}\nDescripcion: {descripcion}"
            }
        ],
        response_format=ClasificacionTicket,
        temperature=0  # respuestas deterministas: mismo input = misma salida
    )
    resultado = respuesta.choices[0].message.parsed
    return resultado.prioridad.value, resultado.razon


# ==================== CLASIFICADOR LOCAL (FALLBACK) ====================

PALABRAS_CRITICAS = [
    "caído", "caida", "no funciona", "todos", "nadie",
    "perdida de datos", "no puedo acceder", "urgente",
    "bloqueado", "sin acceso", "completo"
]

PALABRAS_ALTAS = [
    "error", "falla", "no carga", "no abre", "no responde",
    "no puedo", "imposible", "grave"
]

PALABRAS_MEDIAS = [
    "lento", "tarda", "demora", "intermitente",
    "a veces", "ocasional", "raro"
]

PALABRAS_BAJAS = [
    "cambiar", "actualizar", "consulta", "quisiera",
    "me gustaría", "cuando pueda", "pequeño"
]

FALLBACK_CATEGORIA = {
    "red": "alta",
    "hardware": "media",
    "software": "media",
    "cuenta de usuario": "baja",
    "otro": "baja"
}


def clasificar_por_palabras(descripcion: str, categoria: str) -> tuple[str, str]:
    """
    Clasifica usando palabras clave. No depende de internet.
    Retorna (prioridad, razon).
    """
    desc = descripcion.lower()

    for palabra in PALABRAS_CRITICAS:
        if palabra in desc:
            return "critica", f"palabra clave detectada: '{palabra}'"

    for palabra in PALABRAS_ALTAS:
        if palabra in desc:
            return "alta", f"palabra clave detectada: '{palabra}'"

    for palabra in PALABRAS_MEDIAS:
        if palabra in desc:
            return "media", f"palabra clave detectada: '{palabra}'"

    for palabra in PALABRAS_BAJAS:
        if palabra in desc:
            return "baja", f"palabra clave detectada: '{palabra}'"

    # sin palabras clave: usar categoria como criterio
    prioridad = FALLBACK_CATEGORIA.get(categoria, "media")
    return prioridad, f"sin palabras clave, fallback por categoria '{categoria}'"


# ==================== PUNTO DE ENTRADA UNIFICADO ====================

def asignar_prioridad(descripcion: str, categoria: str) -> str:
    """
    Asigna prioridad a un ticket. Intenta primero con IA;
    si falla, usa el clasificador local.
    Imprime informacion sobre que metodo se uso y por que.
    Retorna solo la prioridad (string).
    """
    try:
        prioridad, razon = clasificar_con_ia(descripcion, categoria)
        print(f"  → [IA] Prioridad asignada: {prioridad}")
        print(f"    Razon: {razon}")
        return prioridad
    except Exception as e:
        prioridad, razon = clasificar_por_palabras(descripcion, categoria)
        print(f"  ⚠ API no disponible ({type(e).__name__}). Usando clasificador local.")
        print(f"  → [Local] Prioridad asignada: {prioridad}")
        print(f"    Razon: {razon}")
        return prioridad
