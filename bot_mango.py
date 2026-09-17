import os
import json
import threading
import traceback

import gspread
from flask import Flask

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


# =========================================================
# CONFIGURACIÓN
# =========================================================

TOKEN = os.environ["TELEGRAM_TOKEN"]

SHEET_ID = "1FlYEJruBOy_l9Wqb09EFfapW3_DtrWABUUUrF68xJdU"
WORKSHEET_NAME = "Main"


# =========================================================
# SERVIDOR PARA RENDER
# =========================================================

app = Flask(__name__)


@app.route("/")
def inicio():
    return "Bot funcionando correctamente."


def iniciar_servidor():
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )


# =========================================================
# GOOGLE SHEETS
# =========================================================

def conectar_google_sheets():

    print("🔄 Intentando conectar con Google Sheets...")

    credenciales_json = os.environ.get("GOOGLE_CREDS")

    if not credenciales_json:
        raise PermissionError(
            "La variable GOOGLE_CREDS no existe en Render."
        )

    print("✅ GOOGLE_CREDS encontrada.")

    # Convertir el contenido de GOOGLE_CREDS a JSON
    credenciales = json.loads(credenciales_json)

    print(
        "📧 Cuenta de servicio:",
        credenciales.get("client_email")
    )

    print(
        "🆔 ID de la hoja:",
        SHEET_ID
    )

    # Autenticación
    cliente = gspread.service_account_from_dict(
        credenciales
    )

    print("✅ Autenticación con Google realizada.")

    # -----------------------------------------------------
    # Intentar abrir la hoja
    # -----------------------------------------------------

    try:

        print("🔎 Intentando abrir Google Sheet...")

        archivo = cliente.open_by_key(SHEET_ID)

        print("✅ Google Sheet encontrado.")

    except Exception as error:

        print("===================================")
        print("❌ ERROR AL ABRIR GOOGLE SHEET")
        print("TIPO:", type(error).__name__)
        print("DETALLE:", repr(error))
        print("----- TRACEBACK -----")

        traceback.print_exc()

        print("===================================")

        raise

    # -----------------------------------------------------
    # Intentar abrir la pestaña Main
    # -----------------------------------------------------

    try:

        print(
            "🔎 Intentando abrir pestaña:",
            WORKSHEET_NAME
        )

        hoja = archivo.worksheet(WORKSHEET_NAME)

        print(
            "✅ Pestaña 'Main' encontrada."
        )

    except Exception as error:

        print("===================================")
        print("❌ ERROR AL ABRIR LA PESTAÑA")
        print("TIPO:", type(error).__name__)
        print("DETALLE:", repr(error))
        print("----- TRACEBACK -----")

        traceback.print_exc()

        print("===================================")

        raise

    return hoja


# =========================================================
# ESTADOS DE LA CONVERSACIÓN
# =========================================================

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


# =========================================================
# START
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["registro"] = {}

    await update.message.reply_text(
        "🤖 ¡Hola! Vamos a registrar los datos.\n\n"
        "Escribe el CORREO de prueba:"
    )

    return CORREO


# =========================================================
# CORREO
# =========================================================

async def recibir_correo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["registro"]["CORREO"] = (
        update.message.text
    )

    await update.message.reply_text(
        "🔐 Escribe la CONTRASEÑA de prueba:"
    )

    return CONTRASENA


# =========================================================
# CONTRASEÑA
# =========================================================

async def recibir_contrasena(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["registro"]["CONTRASEÑA"] = (
        update.message.text
    )

    await update.message.reply_text(
        "🌐 Escribe la IP de prueba:"
    )

    return IP


# =========================================================
# IP
# =========================================================

async def recibir_ip(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["registro"]["IP"] = (
        update.message.text
    )

    await update.message.reply_text(
        "🔑 Escribe el nivel PRIV de prueba:"
    )

    return PRIV


# =========================================================
# PRIV
# =========================================================

async def recibir_priv(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["registro"]["PRIV"] = (
        update.message.text
    )

    await update.message.reply_text(
        "📱 Escribe la PLATAFORMA de prueba:"
    )

    return PLATAFORMA


# =========================================================
# PLATAFORMA
# =========================================================

async def recibir_plataforma(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["registro"]["PLATAFORMAS"] = (
        update.message.text
    )

    await update.message.reply_text(
        "📌 Escribe el ESTADO de prueba:"
    )

    return ESTADO


# =========================================================
# ESTADO
# =========================================================

async def recibir_estado(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["registro"]["ESTADO"] = (
        update.message.text
    )

    await update.message.reply_text(
        "🔢 Escribe el BIN de prueba:"
    )

    return BIN


# =========================================================
# BIN
# =========================================================

async def recibir_bin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["registro"]["BIN"] = (
        update.message.text
    )

    await update.message.reply_text(
        "💳 Escribe el número de TARJETA ficticio:"
    )

    return TARJETA


# =========================================================
# TARJETA
# =========================================================

async def recibir_tarjeta(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["registro"]["TARJETA"] = (
        update.message.text
    )

    await update.message.reply_text(
        "📅 Escribe la FECHA DE VENCIMIENTO ficticia:"
    )

    return VENCIMIENTO


# =========================================================
# VENCIMIENTO
# =========================================================

async def recibir_vencimiento(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["registro"][
        "FECHA DE VENCIMIENTO"
    ] = update.message.text

    registro = context.user_data["registro"]

    print("===================================")
    print("📥 Se recibieron los 9 campos.")
    print("🔄 Intentando conectar con Google Sheets...")

    try:

        # Conectar con Google Sheets
        hoja = conectar_google_sheets()

        # Orden de las columnas
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

        # Guardar información
        hoja.append_row(fila)

        print("✅ FILA GUARDADA CORRECTAMENTE.")
        print("===================================")

        await update.message.reply_text(
            "✅ ¡Registro guardado correctamente "
            "en Google Sheets!"
        )

    except Exception as error:

        print("===================================")
        print("❌ ERROR GOOGLE SHEETS")
        print("TIPO:", type(error).__name__)
        print("DETALLE:", repr(error))
        print("----- TRACEBACK COMPLETO -----")

        traceback.print_exc()

        print("===================================")

        await update.message.reply_text(
            "⚠️ Ocurrió un error al guardar "
            "los datos en Google Sheets.\n\n"
            f"Tipo de error: {type(error).__name__}"
        )

    context.user_data.clear()

    return ConversationHandler.END


# =========================================================
# CANCELAR
# =========================================================

async def cancelar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()

    await update.message.reply_text(
        "❌ Registro cancelado."
    )

    return ConversationHandler.END


# =========================================================
# MAIN
# =========================================================

def main():

    # Iniciar servidor Flask
    threading.Thread(
        target=iniciar_servidor,
        daemon=True
    ).start()

    print("🤖 Bot iniciado...")

    # Crear aplicación de Telegram
    application = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    # Crear conversación
    conversacion = ConversationHandler(

        entry_points=[
            CommandHandler("start", start)
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
            ],
        },

        fallbacks=[
            CommandHandler(
                "cancelar",
                cancelar
            )
        ]
    )

    application.add_handler(conversacion)

    # Ejecutar bot
    application.run_polling()


# =========================================================
# EJECUCIÓN
# =========================================================

if __name__ == "__main__":
    main()
