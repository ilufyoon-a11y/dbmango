import os
import json
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
from oauth2client.service_account import ServiceAccountCredentials
import gspread

app = Flask(__name__)

# Configuración inicial
TOKEN = os.getenv("TOKEN_TELEGRAM", "8791305594:AAFg09Zo3XGtLTUPziRf0kUQJDYHnBHGZuE")
bot = Bot(token=TOKEN)

dispatcher = Dispatcher(bot, None, use_context=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
def conectar_google():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        creds_json = os.getenv("GOOGLE_CREDS")
        if not creds_json:
            print("🚨 No se encontró GOOGLE_CREDS en las variables de entorno.")
            return None
        info = json.loads(creds_json)
        if 'private_key' in info:
            info['private_key'] = info['private_key'].replace('\\n', '\n')
        creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
        client = gspread.authorize(creds)
        
        # Archivo "Huerto de Mango", pestaña "Main"
        sheet = client.open("Huerto de Mango").worksheet("Main")
        print("✅ CONECTADO A GOOGLE SHEETS CORRECTAMENTE 💜")
        return sheet
    except Exception as e:
        print(f"🚨 ERROR DE CONEXIÓN: {e}")
        return None

# --- COMANDO /rapido ---
def rapido_command(update: Update, context: CallbackContext):
    texto = update.message.text
    
    try:
        lineas = texto.split('\n')[1:]
        datos = {}
        for linea in lineas:
            if ':' in linea:
                partes = linea.split(':', 1)
                datos[partes[0].strip().lower()] = partes[1].strip()

        # Mapeo de columnas K a S (Fila 15 en adelante)
        correo = datos.get('correo', '')
        clave = datos.get('clave', '')
        ip = datos.get('ip', '')
        priv = datos.get('priv', '')
        plataforma = datos.get('plataforma', '')
        estado = datos.get('estado', '')
        bin_val = datos.get('bin', '')
        tarjeta = datos.get('tarjeta', '')
        vencimiento = datos.get('vencimiento', '')

        sheet = conectar_google()
        if not sheet:
            update.message.reply_text("❌ Error: No se pudo conectar a Google Sheets.")
            return

        fila_datos = [correo, clave, ip, priv, plataforma, estado, bin_val, tarjeta, vencimiento]
        
        # Buscar siguiente fila libre en la columna K (columna 11)
        columna_k = sheet.col_values(11)
        siguiente_fila = max(15, len(columna_k) + 1)
        
        sheet.update(f'K{siguiente_fila}:S{siguiente_fila}', [fila_datos])

        update.message.reply_text(f"✅ ¡Guardado exitosamente en la fila {siguiente_fila}!")
    except Exception as e:
        update.message.reply_text(f"❌ Error al guardar en Sheets: {e}")

dispatcher.add_handler(CommandHandler("rapido", rapido_command))

# --- RUTAS DE FLASK ---
@app.route('/')
def home():
    return "🥭 Sistema MANGO en línea y operando perfectamente."

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

@app.route('/set_webhook')
def set_webhook():
    url_render = request.host_url.strip('/')
    webhook_url = f"{url_render}/{TOKEN}"
    s = bot.set_webhook(url=webhook_url)
    if s:
        return f"✅ Webhook configurado exitosamente en: {webhook_url}"
    else:
        return "❌ Error al configurar el webhook."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
