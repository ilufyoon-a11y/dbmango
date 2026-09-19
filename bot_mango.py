import os
import json
import traceback
import threading
import asyncio
from datetime import datetime, date

import gspread

from flask import Flask

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

TOKEN = os.environ["TELEGRAM_TOKEN"]

SHEET_ID = "1FlYEJruBOy_l9Wqb09EFfapW3_DtrWABUUUrF68xJdU"
WORKSHEET_NAME = "Main"

# La tabla comienza en la fila 41
FILA_INICIAL = 41

# La tabla comienza en la columna K
COLUMNA_INICIAL = "K"
COLUMNA_FINAL = "S"


# ============================================================
# FLASK PARA RENDER
# ============================================================

app_flask = Flask(__name__)


@app_flask.route("/")
def inicio():
    return "🥭 Bot Mango está funcionando."


def iniciar_servidor():

    puerto = int(
        os.environ.get("PORT", 10000)
    )

    app_flask.run(
        host="0.0.0.0",
        port=puerto
    )


# ============================================================
# GOOGLE SHEETS
# ============================================================

def conectar_google_sheets():

    print("🔄 Intentando conectar con Google Sheets...")

    credenciales_json = os.environ.get("GOOGLE_CREDS")

    if not credenciales_json:
        raise PermissionError(
            "La variable GOOGLE_CREDS no existe en Render."
        )

    print("✅ GOOGLE_CREDS encontrada.")

    credenciales = json.loads(
        credenciales_json
    )

    print(
        "📧 Cuenta de servicio:",
        credenciales.get("client_email")
    )

    print(
        "🆔 ID de la hoja:",
        SHEET_ID
    )

    cliente = gspread.service_account_from_dict(
        credenciales
    )

    print(
        "✅ Autenticación con Google realizada."
    )

    try:

        print(
            "🔎 Intentando abrir Google Sheet..."
        )

        archivo = cliente.open_by_key(
            SHEET_ID
        )

        print(
            "✅ Google Sheet encontrado."
        )

    except Exception as error:

        print(
            "❌ ERROR AL ABRIR GOOGLE SHEET"
        )

        print(
            "TIPO:",
            type(error).__name__
        )

        print(
            "DETALLE:",
            repr(error)
        )

        traceback.print_exc()

        raise

    try:

        print(
            "🔎 Intentando abrir pestaña:",
            WORKSHEET_NAME
        )

        hoja = archivo.worksheet(
            WORKSHEET_NAME
        )

        print(
            "✅ Pestaña encontrada:",
            WORKSHEET_NAME
        )

    except Exception as error:

        print(
            "❌ ERROR AL ABRIR LA PESTAÑA"
        )

        print(
            "TIPO:",
            type(error).__name__
        )

        print(
            "DETALLE:",
            repr(error)
        )

        traceback.print_exc()

        raise

    return hoja


# ============================================================
# BUSCAR PRIMERA FILA DISPONIBLE
# ============================================================

def obtener_siguiente_fila(hoja):

    print(
        "🔎 Buscando fila disponible desde:",
        FILA_INICIAL
    )

    # Solo revisamos la columna K,
    # porque K es donde comienza CORREO.

    ultima_fila = hoja.row_count

    valores = hoja.get(
        f"{COLUMNA_INICIAL}"
        f"{FILA_INICIAL}:"
        f"{COLUMNA_INICIAL}"
        f"{ultima_fila}"
    )

    for indice, fila in enumerate(
        valores,
        start=FILA_INICIAL
    ):

        if not fila:
            print(
                "📍 Primera fila disponible:",
                indice
            )

            return indice

        contenido = fila[0].strip()

        if not contenido:

            print(
                "📍 Primera fila disponible:",
                indice
            )

            return indice

    siguiente = ultima_fila + 1

    print(
        "📍 Agregando nueva fila:",
        siguiente
    )

    return siguiente


# ============================================================
# ESTADOS DEL REGISTRO
# ============================================================

(
    CORREO,
    CONTRASENA,
    IP,
    PRIV,
    PLATAFORMA,
    ESTADO,
    BIN,
    TARJETA,
    VENCIMIENTO
) = range(9)


# ============================================================
# USUARIOS PARA RECORDATORIOS
# ============================================================

usuarios_activos = set()

recordatorios_enviados = set()


# ============================================================
# PLANTILLA BONITA
# ============================================================

def obtener_plantilla():

    return """๑𓈒⠀꒰⠀coɾɾeo 💌⠀꒱ :
๑𓈒⠀꒰⠀pɑsswoɾd 🗝️⠀꒱ :
๑𓈒⠀꒰⠀I.P 📍⠀꒱ :
๑𓈒⠀꒰⠀pɾiv ⛺⠀꒱ :
๑𓈒⠀꒰⠀plɑtɑfoɾmɑ 🎟️⠀꒱ :
๑𓈒⠀꒰⠀estɑdo 🍂⠀꒱ :
๑𓈒⠀꒰⠀bin 🏷️⠀꒱ :
๑𓈒⠀꒰⠀tɑɾjetɑ 💳⠀꒱ :
๑𓈒⠀꒰⠀vencimiento 🕰️⠀꒱ :"""


# ============================================================
# /START
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    usuarios_activos.add(
        update.effective_chat.id
    )

    await update.message.reply_text(
        "🥭 ¡Hola! Soy Bot Mango.\n\n"
        "Comandos disponibles:\n\n"
        "• /registrar\n"
        "• /rapido\n"
        "• /cancelar\n\n"
        "También puedes escribir:\n"
        "registrar\n"
        ".registrar\n"
        "rapido\n"
        ".rapido\n"
        "cancelar\n"
        ".cancelar"
    )


# ============================================================
# /REGISTRAR
# ============================================================

async def registrar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["registro"] = {}

    await update.message.reply_text(
        "📝 Vamos a registrar un nuevo dato.\n\n"
        "Primero escribe el correo de prueba."
    )

    return CORREO


async def recibir_correo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["registro"]["correo"] = (
        update.message.text.strip()
    )

    await update.message.reply_text(
        "🗝️ Escribe la contraseña de prueba."
    )

    return CONTRASENA


async def recibir_contrasena(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["registro"]["contrasena"] = (
        update.message.text.strip()
    )

    await update.message.reply_text(
        "📍 Escribe una IP de prueba."
    )

    return IP


async def recibir_ip(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["registro"]["ip"] = (
        update.message.text.strip()
    )

    await update.message.reply_text(
        "⛺ Escribe PRIV."
    )

    return PRIV


async def recibir_priv(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["registro"]["priv"] = (
        update.message.text.strip()
    )

    await update.message.reply_text(
        "🎟️ Escribe la plataforma."
    )

    return PLATAFORMA


async def recibir_plataforma(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["registro"]["plataforma"] = (
        update.message.text.strip()
    )

    await update.message.reply_text(
        "🍂 Escribe el estado."
    )

    return ESTADO


async def recibir_estado(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["registro"]["estado"] = (
        update.message.text.strip()
    )

    await update.message.reply_text(
        "🏷️ Escribe un BIN de prueba."
    )

    return BIN


async def recibir_bin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["registro"]["bin"] = (
        update.message.text.strip()
    )

    await update.message.reply_text(
        "💳 Escribe una tarjeta enmascarada "
        "o de prueba."
    )

    return TARJETA


async def recibir_tarjeta(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["registro"]["tarjeta"] = (
        update.message.text.strip()
    )

    await update.message.reply_text(
        "🕰️ Escribe la fecha de vencimiento.\n\n"
        "Formato: DD/MM/YYYY"
    )

    return VENCIMIENTO


# ============================================================
# GUARDAR REGISTRO NORMAL
# ============================================================

async def recibir_vencimiento(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["registro"]["vencimiento"] = (
        update.message.text.strip()
    )

    registro = context.user_data["registro"]

    fila = [
        registro["correo"],
        registro["contrasena"],
        registro["ip"],
        registro["priv"],
        registro["plataforma"],
        registro["estado"],
        registro["bin"],
        registro["tarjeta"],
        registro["vencimiento"]
    ]

    try:

        print(
            "📊 Enviando registro a Google Sheets..."
        )

        hoja = conectar_google_sheets()

        fila_actual = obtener_siguiente_fila(
            hoja
        )

        # IMPORTANTE:
        # Se escribe directamente de K a S.
        hoja.update(
            f"K{fila_actual}:S{fila_actual}",
            [fila]
        )

        print(
            "✅ FILA GUARDADA CORRECTAMENTE:",
            fila_actual
        )

        await update.message.reply_text(
            "✅ Registro guardado correctamente.\n\n"
            f"📍 Fila: {fila_actual}\n"
            "📊 Columnas: K → S"
        )

    except Exception as error:

        print(
            "❌ ERROR GOOGLE SHEETS"
        )

        print(
            "TIPO:",
            type(error).__name__
        )

        print(
            "DETALLE:",
            repr(error)
        )

        traceback.print_exc()

        await update.message.reply_text(
            "❌ No se pudo guardar el registro.\n"
            "Revisa los logs de Render."
        )

    context.user_data.clear()

    return ConversationHandler.END


# ============================================================
# CANCELAR
# ============================================================

async def cancelar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()

    await update.message.reply_text(
        "❌ Registro cancelado."
    )

    return ConversationHandler.END


# ============================================================
# /RAPIDO
# ============================================================

async def rapido(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    teclado = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📋 Copiar plantilla",
                callback_data="copiar_plantilla"
            )
        ]
    ])

    await update.message.reply_text(
        "✨ Aquí tienes la plantilla rápida.\n\n"
        "Pulsa el botón para recibirla lista "
        "para copiar.\n\n"
        "💡 Usa únicamente datos ficticios "
        "o enmascarados.",
        reply_markup=teclado
    )


# ============================================================
# BOTÓN COPIAR PLANTILLA
# ============================================================

async def copiar_plantilla(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer(
        "📋 Plantilla lista para copiar"
    )

    plantilla = obtener_plantilla()

    await query.message.reply_text(
        plantilla
    )


# ============================================================
# PROCESAR PLANTILLA RÁPIDA
# ============================================================

async def recibir_plantilla_rapida(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    texto = update.message.text

    campos = {

        "coɾɾeo": "correo",

        "pɑsswoɾd": "contrasena",

        "I.P": "ip",

        "pɾiv": "priv",

        "plɑtɑfoɾmɑ": "plataforma",

        "estɑdo": "estado",

        "bin": "bin",

        "tɑɾjetɑ": "tarjeta",

        "vencimiento": "vencimiento"
    }

    registro = {}

    for linea in texto.splitlines():

        if ":" not in linea:
            continue

        etiqueta, valor = linea.split(
            ":",
            1
        )

        etiqueta = etiqueta.strip()

        valor = valor.strip()

        for nombre_formato, nombre_campo in campos.items():

            if (
                nombre_formato.lower()
                in etiqueta.lower()
            ):

                registro[nombre_campo] = valor

                break

    campos_requeridos = [

        "correo",
        "contrasena",
        "ip",
        "priv",
        "plataforma",
        "estado",
        "bin",
        "tarjeta",
        "vencimiento"
    ]

    faltantes = [

        campo

        for campo in campos_requeridos

        if (
            campo not in registro
            or not registro[campo]
        )
    ]

    if faltantes:

        await update.message.reply_text(
            "⚠️ Faltan algunos campos:\n\n"
            + "\n".join(
                f"• {campo}"
                for campo in faltantes
            )
        )

        return

    fila = [

        registro["correo"],

        registro["contrasena"],

        registro["ip"],

        registro["priv"],

        registro["plataforma"],

        registro["estado"],

        registro["bin"],

        registro["tarjeta"],

        registro["vencimiento"]
    ]

    try:

        print(
            "📊 Guardando plantilla rápida..."
        )

        hoja = conectar_google_sheets()

        fila_actual = obtener_siguiente_fila(
            hoja
        )

        # K → S
        hoja.update(
            f"K{fila_actual}:S{fila_actual}",
            [fila]
        )

        print(
            "✅ PLANTILLA GUARDADA EN FILA:",
            fila_actual
        )

        await update.message.reply_text(
            "✨ ¡Registro rápido guardado!\n\n"
            f"📍 Fila: {fila_actual}\n"
            "📊 Columnas: K → S"
        )

    except Exception as error:

        print(
            "❌ ERROR AL GUARDAR PLANTILLA"
        )

        print(
            "TIPO:",
            type(error).__name__
        )

        print(
            "DETALLE:",
            repr(error)
        )

        traceback.print_exc()

        await update.message.reply_text(
            "❌ Ocurrió un error al guardar "
            "el registro."
        )


# ============================================================
# RECORDATORIO DE VENCIMIENTO
# ============================================================

async def enviar_recordatorio(
    chat_id,
    fila
):

    try:

        await application.bot.send_message(
            chat_id=chat_id,
            text="🚨 El registro vence mañana."
        )

    except Exception as error:

        print(
            "❌ Error enviando recordatorio:",
            repr(error)
        )


def revisar_vencimientos():

    while True:

        try:

            hoja = conectar_google_sheets()

            datos = hoja.get_all_values()

            hoy = date.today()

            for numero_fila, fila in enumerate(
                datos[FILA_INICIAL - 1:],
                start=FILA_INICIAL
            ):

                # Necesitamos llegar hasta
                # la columna S.
                if len(fila) < 19:
                    continue

                # La columna S es el índice 18.
                fecha_texto = fila[18].strip()

                if not fecha_texto:
                    continue

                try:

                    fecha_vencimiento = (
                        datetime.strptime(
                            fecha_texto,
                            "%d/%m/%Y"
                        ).date()
                    )

                except ValueError:

                    print(
                        f"⚠️ Fecha inválida "
                        f"en fila {numero_fila}: "
                        f"{fecha_texto}"
                    )

                    continue

                diferencia = (
                    fecha_vencimiento - hoy
                ).days

                # SOLO un día antes.
                if diferencia == 1:

                    for chat_id in usuarios_activos:

                        clave = (
                            chat_id,
                            numero_fila
                        )

                        if (
                            clave
                            not in recordatorios_enviados
                        ):

                            asyncio.run(
                                enviar_recordatorio(
                                    chat_id,
                                    numero_fila
                                )
                            )

                            recordatorios_enviados.add(
                                clave
                            )

        except Exception as error:

            print(
                "❌ ERROR REVISANDO VENCIMIENTOS:",
                repr(error)
            )

            traceback.print_exc()

        # Revisar cada hora.
        threading.Event().wait(3600)


# ============================================================
# APLICACIÓN TELEGRAM
# ============================================================

application = Application.builder().token(
    TOKEN
).build()


# ============================================================
# CONVERSACIÓN /REGISTRAR
# ============================================================

conversacion_registro = ConversationHandler(

    entry_points=[

        CommandHandler(
            "registrar",
            registrar
        ),

        MessageHandler(
            filters.Regex(
                r"(?i)^\.?registrar$"
            ),
            registrar
        )
    ],

    states={

        CORREO: [

            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                recibir_correo
            )
        ],

        CONTRASENA: [

            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                recibir_contrasena
            )
        ],

        IP: [

            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                recibir_ip
            )
        ],

        PRIV: [

            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                recibir_priv
            )
        ],

        PLATAFORMA: [

            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                recibir_plataforma
            )
        ],

        ESTADO: [

            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                recibir_estado
            )
        ],

        BIN: [

            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                recibir_bin
            )
        ],

        TARJETA: [

            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                recibir_tarjeta
            )
        ],

        VENCIMIENTO: [

            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                recibir_vencimiento
            )
        ]
    },

    fallbacks=[

        CommandHandler(
            "cancelar",
            cancelar
        ),

        MessageHandler(
            filters.Regex(
                r"(?i)^\.?cancelar$"
            ),
            cancelar
        )
    ]
)


# ============================================================
# HANDLERS
# ============================================================

# /start
application.add_handler(
    CommandHandler(
        "start",
        start
    )
)

application.add_handler(
    MessageHandler(
        filters.Regex(
            r"(?i)^\.?start$"
        ),
        start
    )
)


# /registrar
application.add_handler(
    conversacion_registro
)


# /rapido
application.add_handler(
    CommandHandler(
        "rapido",
        rapido
    )
)

application.add_handler(
    MessageHandler(
        filters.Regex(
            r"(?i)^\.?rapido$"
        ),
        rapido
    )
)


# Botón de copiar
application.add_handler(
    CallbackQueryHandler(
        copiar_plantilla,
        pattern="^copiar_plantilla$"
    )
)


# /cancelar
application.add_handler(
    CommandHandler(
        "cancelar",
        cancelar
    )
)

application.add_handler(
    MessageHandler(
        filters.Regex(
            r"(?i)^\.?cancelar$"
        ),
        cancelar
    )
)


# Plantilla rápida
application.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        recibir_plantilla_rapida
    )
)


# ============================================================
# INICIO
# ============================================================

if __name__ == "__main__":

    print(
        "==================================="
    )

    print(
        "🥭 BOT MANGO INICIANDO..."
    )

    print(
        "==================================="
    )

    # --------------------------------------------------------
    # Flask para Render
    # --------------------------------------------------------

    hilo_flask = threading.Thread(
        target=iniciar_servidor,
        daemon=True
    )

    hilo_flask.start()

    print(
        "🌐 Servidor Flask iniciado."
    )

    # --------------------------------------------------------
    # Recordatorios
    # --------------------------------------------------------

    hilo_recordatorios = threading.Thread(
        target=revisar_vencimientos,
        daemon=True
    )

    hilo_recordatorios.start()

    print(
        "⏰ Sistema de recordatorios iniciado."
    )

    print(
        "🤖 Bot iniciado correctamente."
    )

    # --------------------------------------------------------
    # Telegram
    # --------------------------------------------------------

    application.run_polling()
