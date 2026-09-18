import os
import json
import traceback
import time
import asyncio

from datetime import datetime, date

import gspread

from flask import Flask
from threading import Thread

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)


# =========================================================
# CONFIGURACIÓN
# =========================================================

TOKEN = os.environ["TELEGRAM_TOKEN"]

SHEET_ID = "1FlYEJruBOy_l9Wqb09EFfapW3_DtrWABUUUrF68xJdU"
WORKSHEET_NAME = "Main"

# Los registros nuevos comienzan desde la fila 41
FILA_INICIAL = 41

# Chats que utilizaron el bot
usuarios_activos = set()

# Evita mandar varias veces el mismo recordatorio
recordatorios_enviados = set()


# =========================================================
# FLASK PARA RENDER
# =========================================================

app = Flask(__name__)


@app.route("/")
def inicio():
    return "🤖 Bot funcionando correctamente"


def ejecutar_servidor():
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

    # -----------------------------------------------------
    # ABRIR GOOGLE SHEET
    # -----------------------------------------------------

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

        print("===================================")
        print("❌ ERROR AL ABRIR GOOGLE SHEET")
        print(
            "TIPO:",
            type(error).__name__
        )
        print(
            "DETALLE:",
            repr(error)
        )
        print("----- TRACEBACK -----")

        traceback.print_exc()

        print("===================================")

        raise

    # -----------------------------------------------------
    # ABRIR PESTAÑA
    # -----------------------------------------------------

    try:

        print(
            "🔎 Intentando abrir pestaña:",
            WORKSHEET_NAME
        )

        hoja = archivo.worksheet(
            WORKSHEET_NAME
        )

        print(
            f"✅ Pestaña '{WORKSHEET_NAME}' encontrada."
        )

    except Exception as error:

        print("===================================")
        print("❌ ERROR AL ABRIR LA PESTAÑA")
        print(
            "TIPO:",
            type(error).__name__
        )
        print(
            "DETALLE:",
            repr(error)
        )
        print("----- TRACEBACK -----")

        traceback.print_exc()

        print("===================================")

        raise

    return hoja


# =========================================================
# BUSCAR SIGUIENTE FILA
# =========================================================

def obtener_siguiente_fila(hoja):

    valores = hoja.get_all_values()

    # Si todavía no llegamos a la fila 41
    if len(valores) < FILA_INICIAL - 1:
        return FILA_INICIAL

    ultima_fila = FILA_INICIAL - 1

    for numero_fila, fila in enumerate(
        valores,
        start=1
    ):

        if numero_fila < FILA_INICIAL:
            continue

        if any(
            str(celda).strip()
            for celda in fila
        ):

            ultima_fila = numero_fila

    return ultima_fila + 1


# =========================================================
# ESTADOS DEL REGISTRO NORMAL
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
# /START
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_chat:

        usuarios_activos.add(
            update.effective_chat.id
        )

    await update.message.reply_text(
        "🤖 ¡Hola!\n\n"
        "Puedes usar /registrar para ingresar "
        "un registro campo por campo.\n\n"
        "También puedes usar /rapido o .rapido "
        "para completar una plantilla de una sola vez."
    )


# =========================================================
# REGISTRO NORMAL
# =========================================================

async def registrar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_chat:

        usuarios_activos.add(
            update.effective_chat.id
        )

    context.user_data["registro"] = {}

    await update.message.reply_text(
        "📝 REGISTRO\n\n"
        "Ingresa el CORREO de prueba:"
    )

    return CORREO


async def recibir_correo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data[
        "registro"
    ]["CORREO"] = update.message.text

    await update.message.reply_text(
        "Ingresa la CONTRASEÑA DE PRUEBA:"
    )

    return CONTRASENA


async def recibir_contrasena(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data[
        "registro"
    ]["CONTRASEÑA"] = update.message.text

    await update.message.reply_text(
        "Ingresa la IP:"
    )

    return IP


async def recibir_ip(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data[
        "registro"
    ]["IP"] = update.message.text

    await update.message.reply_text(
        "Ingresa PRIV:"
    )

    return PRIV


async def recibir_priv(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data[
        "registro"
    ]["PRIV"] = update.message.text

    await update.message.reply_text(
        "Ingresa PLATAFORMAS:"
    )

    return PLATAFORMA


async def recibir_plataforma(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data[
        "registro"
    ]["PLATAFORMAS"] = update.message.text

    await update.message.reply_text(
        "Ingresa ESTADO:"
    )

    return ESTADO


async def recibir_estado(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data[
        "registro"
    ]["ESTADO"] = update.message.text

    await update.message.reply_text(
        "Ingresa BIN DE PRUEBA:"
    )

    return BIN


async def recibir_bin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data[
        "registro"
    ]["BIN"] = update.message.text

    await update.message.reply_text(
        "Ingresa TARJETA DE PRUEBA ENMASCARADA:"
    )

    return TARJETA


async def recibir_tarjeta(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data[
        "registro"
    ]["TARJETA"] = update.message.text

    await update.message.reply_text(
        "📅 Ingresa la FECHA DE VENCIMIENTO.\n"
        "Formato: DD/MM/AAAA"
    )

    return VENCIMIENTO


async def recibir_vencimiento(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    fecha = update.message.text.strip()

    # -----------------------------------------------------
    # VALIDAR FECHA
    # -----------------------------------------------------

    try:

        datetime.strptime(
            fecha,
            "%d/%m/%Y"
        )

    except ValueError:

        await update.message.reply_text(
            "❌ Fecha incorrecta.\n\n"
            "Usa el formato DD/MM/AAAA."
        )

        return VENCIMIENTO

    context.user_data[
        "registro"
    ]["FECHA DE VENCIMIENTO"] = fecha

    registro = context.user_data[
        "registro"
    ]

    # -----------------------------------------------------
    # ORDEN DE COLUMNAS
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # GUARDAR
    # -----------------------------------------------------

    try:

        hoja = conectar_google_sheets()

        fila_destino = obtener_siguiente_fila(
            hoja
        )

        print(
            f"📊 Guardando registro en fila "
            f"{fila_destino}..."
        )

        hoja.update(
            f"A{fila_destino}:I{fila_destino}",
            [fila]
        )

        print(
            "✅ FILA GUARDADA CORRECTAMENTE."
        )

        await update.message.reply_text(
            "✅ Registro guardado correctamente.\n\n"
            f"📊 Fila: {fila_destino}"
        )

    except Exception as error:

        print(
            "❌ ERROR GOOGLE SHEETS:"
        )

        print(
            type(error).__name__
        )

        print(
            repr(error)
        )

        traceback.print_exc()

        await update.message.reply_text(
            "❌ Ocurrió un error al guardar "
            "el registro."
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
# REGISTRO RÁPIDO
# =========================================================

async def rapido(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_chat:

        usuarios_activos.add(
            update.effective_chat.id
        )

    await update.message.reply_text(
        "⚡ REGISTRO RÁPIDO\n\n"
        "Copia esta plantilla, completa los "
        "datos de prueba y envíamela completa:\n\n"

        "CORREO: usuario_prueba@ejemplo.test\n"
        "CONTRASEÑA: XXXXXXXX\n"
        "IP: 192.0.2.10\n"
        "PRIV: normal\n"
        "PLATAFORMAS: plataforma_prueba\n"
        "ESTADO: activo\n"
        "BIN: XXXXXX\n"
        "TARJETA: XXXX-XXXX-XXXX-1234\n"
        "FECHA DE VENCIMIENTO: 25/09/2026"
    )


# =========================================================
# PROCESAR PLANTILLA RÁPIDA
# =========================================================

def procesar_plantilla(texto):

    campos = {
        "CORREO": None,
        "CONTRASEÑA": None,
        "IP": None,
        "PRIV": None,
        "PLATAFORMAS": None,
        "ESTADO": None,
        "BIN": None,
        "TARJETA": None,
        "FECHA DE VENCIMIENTO": None
    }

    for linea in texto.splitlines():

        if ":" not in linea:
            continue

        clave, valor = linea.split(
            ":",
            1
        )

        clave = clave.strip().upper()
        valor = valor.strip()

        if clave in campos:

            campos[clave] = valor

    faltantes = [
        campo
        for campo, valor in campos.items()
        if not valor
    ]

    return campos, faltantes


async def recibir_plantilla_rapida(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    texto = update.message.text

    registro, faltantes = procesar_plantilla(
        texto
    )

    # -----------------------------------------------------
    # COMPROBAR CAMPOS
    # -----------------------------------------------------

    if faltantes:

        await update.message.reply_text(
            "❌ Faltan estos campos:\n\n"
            + "\n".join(
                f"• {campo}"
                for campo in faltantes
            )
        )

        return

    # -----------------------------------------------------
    # VALIDAR FECHA
    # -----------------------------------------------------

    try:

        datetime.strptime(
            registro["FECHA DE VENCIMIENTO"],
            "%d/%m/%Y"
        )

    except ValueError:

        await update.message.reply_text(
            "❌ La fecha de vencimiento no tiene "
            "el formato correcto.\n\n"
            "Usa DD/MM/AAAA."
        )

        return

    # -----------------------------------------------------
    # ORDEN DE COLUMNAS
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # GUARDAR EN SHEETS
    # -----------------------------------------------------

    try:

        hoja = conectar_google_sheets()

        fila_destino = obtener_siguiente_fila(
            hoja
        )

        print(
            f"⚡ Guardando registro rápido "
            f"en fila {fila_destino}..."
        )

        hoja.update(
            f"A{fila_destino}:I{fila_destino}",
            [fila]
        )

        print(
            "✅ REGISTRO RÁPIDO GUARDADO."
        )

        await update.message.reply_text(
            "⚡ ¡Registro rápido guardado!\n\n"
            f"📊 Fila: {fila_destino}"
        )

    except Exception as error:

        print(
            "❌ ERROR AL GUARDAR "
            "REGISTRO RÁPIDO:"
        )

        print(
            type(error).__name__
        )

        print(
            repr(error)
        )

        traceback.print_exc()

        await update.message.reply_text(
            "❌ Ocurrió un error al guardar "
            "el registro."
        )


# =========================================================
# RECORDATORIOS
# =========================================================

async def enviar_recordatorio(
    chat_id,
    mensaje
):

    if application:

        await application.bot.send_message(
            chat_id=chat_id,
            text=mensaje
        )


def revisar_vencimientos():

    while True:

        try:

            print(
                "🔎 Revisando fechas "
                "de vencimiento..."
            )

            hoja = conectar_google_sheets()

            filas = hoja.get_all_values()

            hoy = date.today()

            for numero_fila, fila in enumerate(
                filas,
                start=1
            ):

                # Solo revisar desde fila 41
                if numero_fila < FILA_INICIAL:
                    continue

                # Necesitamos las 9 columnas
                if len(fila) < 9:
                    continue

                # La fecha está en la columna I
                fecha_texto = fila[8].strip()

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

                dias_restantes = (
                    fecha_vencimiento - hoy
                ).days

                # -------------------------------------------------
                # SOLO 1 DÍA ANTES
                # -------------------------------------------------

                if dias_restantes == 1:

                    for chat_id in list(
                        usuarios_activos
                    ):

                        clave = (
                            chat_id,
                            numero_fila,
                            fecha_texto
                        )

                        # Evitar repetir
                        if clave in recordatorios_enviados:
                            continue

                        mensaje = (
                            "🔴 🚨 El registro de "
                            f"la fila {numero_fila} "
                            "vence mañana."
                        )

                        try:

                            # Ejecutar envío
                            asyncio.run(
                                enviar_recordatorio(
                                    chat_id,
                                    mensaje
                                )
                            )

                            recordatorios_enviados.add(
                                clave
                            )

                            print(
                                f"🚨 Recordatorio enviado "
                                f"a {chat_id}"
                            )

                        except Exception as error:

                            print(
                                "❌ Error enviando "
                                "recordatorio:",
                                repr(error)
                            )

        except Exception as error:

            print(
                "❌ ERROR REVISANDO "
                "VENCIMIENTOS:"
            )

            print(
                type(error).__name__,
                repr(error)
            )

            traceback.print_exc()

        # Revisar cada hora
        time.sleep(3600)


# =========================================================
# APLICACIÓN
# =========================================================

application = None


# =========================================================
# MAIN
# =========================================================

def main():

    global application

    # -----------------------------------------------------
    # FLASK
    # -----------------------------------------------------

    Thread(
        target=ejecutar_servidor,
        daemon=True
    ).start()

    print(
        "🌐 Servidor Flask iniciado."
    )

    # -----------------------------------------------------
    # TELEGRAM
    # -----------------------------------------------------

    application = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    # =====================================================
    # CONVERSACIÓN NORMAL
    # =====================================================

    conversacion = ConversationHandler(

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

    # =====================================================
    # START
    # =====================================================

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

    # =====================================================
    # CONVERSACIÓN
    # =====================================================

    application.add_handler(
        conversacion
    )

    # =====================================================
    # RAPIDO
    # =====================================================

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

    # =====================================================
    # PLANTILLA RÁPIDA
    # =====================================================

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            recibir_plantilla_rapida
        )
    )

    # =====================================================
    # RECORDATORIOS
    # =====================================================

    Thread(
        target=revisar_vencimientos,
        daemon=True
    ).start()

    print(
        "⏰ Sistema de recordatorios iniciado."
    )

    print(
        "🤖 Bot iniciado..."
    )

    # =====================================================
    # INICIAR BOT
    # =====================================================

    application.run_polling()


# =========================================================
# EJECUCIÓN
# =========================================================

if __name__ == "__main__":
    main()
