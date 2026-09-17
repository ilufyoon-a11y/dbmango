import os
import json
import threading

import gspread
from flask import Flask

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)


# =========================================================
# SERVIDOR PARA RENDER
# =========================================================

web_app = Flask(__name__)


@web_app.route("/")
def home():
    return "Bot funcionando correctamente."


def iniciar_servidor():
    port = int(os.environ.get("PORT", 10000))

    web_app.run(
        host="0.0.0.0",
        port=port
    )


# =========================================================
# CONEXIÓN CON GOOGLE SHEETS
# =========================================================

def conectar_google_sheets():
    # Obtiene las credenciales desde la variable de Render
    credenciales = json.loads(
        os.environ["GOOGLE_CREDS"]
    )

    # Crea la conexión con Google
    cliente = gspread.service_account_from_dict(
        credenciales
    )

    # Abre el archivo de Google Sheets mediante su ID
    archivo = cliente.open_by_key(
        "1FlYEJruBOy_l9Wqb09EFfapW3_DtrWABUUUrF68xJdU"
    )

    # Selecciona la pestaña llamada Main
    hoja = archivo.worksheet("Main")

    return hoja


# =========================================================
# ESTADOS DEL FORMULARIO
# =========================================================

CORREO, CONTRASENA, IP, PRIV, PLATAFORMA, ESTADO, BIN, TARJETA, VENCIMIENTO = range(9)


# =========================================================
# COMANDO /start
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Creamos un registro vacío
    context.user_data["registro"] = {}

    await update.message.reply_text(
        "🤖 ¡Hola! Vamos a registrar un nuevo dato.\n\n"
        "📧 Ingresa el correo de prueba:"
    )

    return CORREO


# =========================================================
# CORREO
# =========================================================

async def recibir_correo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["registro"]["CORREO"] = update.message.text

    await update.message.reply_text(
        "🔑 Ingresa la contraseña de prueba:"
    )

    return CONTRASENA


# =========================================================
# CONTRASEÑA
# =========================================================

async def recibir_contrasena(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["registro"]["CONTRASEÑA"] = update.message.text

    await update.message.reply_text(
        "🌐 Ingresa la IP de prueba:"
    )

    return IP


# =========================================================
# IP
# =========================================================

async def recibir_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["registro"]["IP"] = update.message.text

    await update.message.reply_text(
        "🌎 Ingresa el país/PRIV:"
    )

    return PRIV


# =========================================================
# PRIV
# =========================================================

async def recibir_priv(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["registro"]["PRIV"] = update.message.text

    await update.message.reply_text(
        "📱 Ingresa la plataforma:"
    )

    return PLATAFORMA


# =========================================================
# PLATAFORMA
# =========================================================

async def recibir_plataforma(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["registro"]["PLATAFORMAS"] = update.message.text

    await update.message.reply_text(
        "📌 Ingresa el estado:"
    )

    return ESTADO


# =========================================================
# ESTADO
# =========================================================

async def recibir_estado(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["registro"]["ESTADO"] = update.message.text

    await update.message.reply_text(
        "🔢 Ingresa el BIN ficticio:"
    )

    return BIN


# =========================================================
# BIN
# =========================================================

async def recibir_bin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["registro"]["BIN"] = update.message.text

    await update.message.reply_text(
        "💳 Ingresa el número de tarjeta enmascarado:"
    )

    return TARJETA


# =========================================================
# TARJETA
# =========================================================

async def recibir_tarjeta(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["registro"]["TARJETA"] = update.message.text

    await update.message.reply_text(
        "📅 Ingresa la fecha de vencimiento de prueba:"
    )

    return VENCIMIENTO


# =========================================================
# FECHA DE VENCIMIENTO
# =========================================================

async def recibir_vencimiento(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["registro"]["FECHA DE VENCIMIENTO"] = update.message.text

    try:

        # Conectamos con Google Sheets
        hoja = conectar_google_sheets()

        # Recuperamos los datos registrados
        registro = context.user_data["registro"]

        # Creamos la fila respetando el orden de las columnas
        fila = [
            registro["CORREO"],
            registro["CONTRASEÑA"],
            registro["IP"],
            registro["PRIV"],
            registro["PLATAFORMAS"],
            registro["ESTADO"],
            registro["BIN"],
            registro["TARJETA"],
            registro["FECHA DE VENCIMIENTO"]
        ]

        # Agregamos la fila a Google Sheets
        hoja.append_row(fila)

        await update.message.reply_text(
            "✅ Registro completado.\n\n"
            "📊 Los 9 campos fueron guardados correctamente "
            "en Google Sheets."
        )

        print("✅ Registro guardado en Google Sheets.")

    except Exception as error:

        print(
            "❌ ERROR GOOGLE SHEETS:",
            error
        )

        await update.message.reply_text(
            "⚠️ Los datos fueron recibidos, pero ocurrió "
            "un error al guardarlos en Google Sheets."
        )

    return ConversationHandler.END


# =========================================================
# CANCELAR
# =========================================================

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "❌ Registro cancelado."
    )

    return ConversationHandler.END


# =========================================================
# FUNCIÓN PRINCIPAL
# =========================================================

def main():

    # Obtenemos el token de Telegram desde Render
    token = os.getenv("TELEGRAM_TOKEN")

    if not token:

        print(
            "❌ ERROR: No se encontró TELEGRAM_TOKEN"
        )

        return

    # Iniciamos el servidor HTTP para Render
    threading.Thread(
        target=iniciar_servidor,
        daemon=True
    ).start()

    # Creamos la aplicación de Telegram
    app = Application.builder().token(token).build()

    # Creamos la conversación
    conversacion = ConversationHandler(

        entry_points=[
            CommandHandler(
                "start",
                start
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
            )
        ]
    )

    # Añadimos la conversación al bot
    app.add_handler(conversacion)

    print("🤖 Bot iniciado...")

    # Iniciamos Telegram
    app.run_polling()


# =========================================================
# EJECUTAR
# =========================================================

if __name__ == "__main__":
    main()
