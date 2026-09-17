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

    print("🔄 Intentando conectar con Google Sheets...")

    # Comprobar que exista la variable
    if "GOOGLE_CREDS" not in os.environ:
        raise Exception(
            "No existe la variable GOOGLE_CREDS en Render."
        )

    # Obtener las credenciales desde Render
    credenciales = json.loads(
        os.environ["GOOGLE_CREDS"]
    )

    print("✅ GOOGLE_CREDS encontrada.")

    # Crear cliente de Google
    cliente = gspread.service_account_from_dict(
        credenciales
    )

    print("✅ Autenticación con Google realizada.")

    # Abrir el archivo mediante su ID
    archivo = cliente.open_by_key(
        "1FlYEJruBOy_l9Wqb09EFfapW3_DtrWABUUUrF68xJdU"
    )

    print("✅ Google Sheet encontrado.")

    # Abrir la pestaña Main
    hoja = archivo.worksheet("Main")

    print("✅ Pestaña 'Main' encontrada.")

    return hoja


# =========================================================
# ESTADOS DEL FORMULARIO
# =========================================================

CORREO, CONTRASENA, IP, PRIV, PLATAFORMA, ESTADO, BIN, TARJETA, VENCIMIENTO = range(9)


# =========================================================
# COMANDO /start
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

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

async def recibir_vencimiento(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["registro"]["FECHA DE VENCIMIENTO"] = (
        update.message.text
    )

    print("📥 Se recibieron los 9 campos.")

    try:

        # ---------------------------------------------
        # Conectar con Google Sheets
        # ---------------------------------------------

        hoja = conectar_google_sheets()

        # ---------------------------------------------
        # Obtener registro
        # ---------------------------------------------

        registro = context.user_data["registro"]

        print("📝 Preparando fila para Google Sheets...")

        # ---------------------------------------------
        # Crear fila
        # ---------------------------------------------

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

        print("📊 Enviando fila a Google Sheets...")

        # ---------------------------------------------
        # Agregar fila
        # ---------------------------------------------

        hoja.append_row(fila)

        print("✅ FILA GUARDADA CORRECTAMENTE.")

        await update.message.reply_text(
            "✅ Registro completado.\n\n"
            "📊 Los 9 campos fueron guardados "
            "correctamente en Google Sheets."
        )

    except Exception as error:

        print("===================================")
        print("❌ ERROR GOOGLE SHEETS")
        print("TIPO:", type(error).__name__)
        print("DETALLE:", repr(error))
        print("===================================")

        await update.message.reply_text(
            "⚠️ Ocurrió un error al guardar "
            "los datos en Google Sheets.\n\n"
            f"Tipo de error: {type(error).__name__}"
        )

    return ConversationHandler.END


# =========================================================
# CANCELAR
# =========================================================

async def cancelar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "❌ Registro cancelado."
    )

    return ConversationHandler.END


# =========================================================
# FUNCIÓN PRINCIPAL
# =========================================================

def main():

    # ---------------------------------------------
    # Obtener token de Telegram
    # ---------------------------------------------

    token = os.getenv("TELEGRAM_TOKEN")

    if not token:

        print(
            "❌ ERROR: No se encontró TELEGRAM_TOKEN."
        )

        return

    # ---------------------------------------------
    # Iniciar servidor para Render
    # ---------------------------------------------

    threading.Thread(
        target=iniciar_servidor,
        daemon=True
    ).start()

    # ---------------------------------------------
    # Crear aplicación de Telegram
    # ---------------------------------------------

    app = Application.builder().token(token).build()

    # ---------------------------------------------
    # Crear conversación
    # ---------------------------------------------

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

    # ---------------------------------------------
    # Añadir conversación
    # ---------------------------------------------

    app.add_handler(conversacion)

    print("🤖 Bot iniciado...")

    # ---------------------------------------------
    # Iniciar bot
    # ---------------------------------------------

    app.run_polling()


# =========================================================
# EJECUTAR
# =========================================================

if __name__ == "__main__":
    main()
