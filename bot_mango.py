import os
import threading

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


# -------------------------
# Servidor para Render
# -------------------------

web_app = Flask(__name__)


@web_app.route("/")
def home():
    return "Bot funcionando correctamente."


def iniciar_servidor():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)


# -------------------------
# Estados del formulario
# -------------------------

CORREO, CONTRASENA, IP, PRIV, PLATAFORMA, ESTADO, BIN, TARJETA, VENCIMIENTO = range(9)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["registro"] = {}

    await update.message.reply_text(
        "🤖 ¡Hola! Vamos a registrar un nuevo dato.\n\n"
        "📧 Ingresa el correo de prueba:"
    )

    return CORREO


async def recibir_correo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["registro"]["CORREO"] = update.message.text

    await update.message.reply_text(
        "🔑 Ingresa la contraseña de prueba:"
    )

    return CONTRASENA


async def recibir_contrasena(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["registro"]["CONTRASEÑA"] = update.message.text

    await update.message.reply_text(
        "🌐 Ingresa la IP de prueba:"
    )

    return IP


async def recibir_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["registro"]["IP"] = update.message.text

    await update.message.reply_text(
        "🌎 Ingresa el país/PRIV:"
    )

    return PRIV


async def recibir_priv(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["registro"]["PRIV"] = update.message.text

    await update.message.reply_text(
        "📱 Ingresa la plataforma:"
    )

    return PLATAFORMA


async def recibir_plataforma(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["registro"]["PLATAFORMAS"] = update.message.text

    await update.message.reply_text(
        "📌 Ingresa el estado:"
    )

    return ESTADO


async def recibir_estado(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["registro"]["ESTADO"] = update.message.text

    await update.message.reply_text(
        "🔢 Ingresa el BIN ficticio:"
    )

    return BIN


async def recibir_bin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["registro"]["BIN"] = update.message.text

    await update.message.reply_text(
        "💳 Ingresa el número de tarjeta enmascarado:"
    )

    return TARJETA


async def recibir_tarjeta(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["registro"]["TARJETA"] = update.message.text

    await update.message.reply_text(
        "📅 Ingresa la fecha de vencimiento de prueba:"
    )

    return VENCIMIENTO


async def recibir_vencimiento(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["registro"]["FECHA DE VENCIMIENTO"] = update.message.text

    await update.message.reply_text(
        "✅ Registro completado.\n\n"
        "Los 9 campos fueron identificados correctamente."
    )

    return ConversationHandler.END


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "❌ Registro cancelado."
    )

    return ConversationHandler.END


# -------------------------
# Programa principal
# -------------------------

def main():

    token = os.getenv("TELEGRAM_TOKEN")

    if not token:
        print("ERROR: No se encontró TELEGRAM_TOKEN")
        return

    # Iniciar servidor HTTP para Render
    threading.Thread(
        target=iniciar_servidor,
        daemon=True
    ).start()

    app = Application.builder().token(token).build()

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
            ]
        },

        fallbacks=[
            CommandHandler("cancelar", cancelar)
        ]
    )

    app.add_handler(conversacion)

    print("🤖 Bot iniciado...")

    app.run_polling()


if __name__ == "__main__":
    main()
