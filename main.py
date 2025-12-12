import json, os, requests, base64
from io import BytesIO
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ==============================
# CONFIGURACIÓN
# ==============================

TOKEN = "8203432554:AAGAZjEgMjAIkUAMP-LJoYMobooz6N0Y4ug"

OWNERS = [6251510385, 8257283392,8306043445]  # AGREGA TUS IDS

USERS_FILE = "usuarios.json"
REV_FILE = "revendedores.json"


# ==============================
# JSON HELPERS
# ==============================

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def es_revendedor(uid):
    return str(uid) in load_json(REV_FILE)

def es_owner(uid):
    return uid in OWNERS

def esta_registrado(uid):
    return str(uid) in load_json(USERS_FILE)

GRUPOS_FILE = "grupos.json"

def load_grupos():
    try:
        with open(GRUPOS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_grupos(data):
    with open(GRUPOS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

MENUS_FILE = "menus.json"

def load_menus():
    try:
        with open(MENUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_menus(data):
    with open(MENUS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
# ==============================
# AutoRegistro de Grupos
# ==============================

async def auto_register_group(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat = update.effective_chat

    # Solo registrar grupos
    if chat.type not in ["group", "supergroup"]:
        return

    grupos = load_grupos()

    gid = str(chat.id)

    if gid not in grupos:
        grupos[gid] = {
            "title": chat.title,
            "id": chat.id
        }
        save_grupos(grupos)
        print(f"📌 Grupo registrado automáticamente: {chat.title} ({chat.id})")
        
async def auto_register_group_on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat = update.effective_chat

    if chat.type not in ["group", "supergroup"]:
        return

    grupos = load_grupos()
    gid = str(chat.id)

    if gid not in grupos:
        grupos[gid] = {
            "title": chat.title,
            "id": chat.id
        }
        save_grupos(grupos)
        print(f"📌 Grupo registrado desde mensaje: {chat.title} ({chat.id})")


# ==============================
# CHECK DE REGISTRO
# ==============================

async def check_registro(update: Update):
    msg = update.message
    if not msg:
        return False

    uid = msg.from_user.id

    if msg.text.startswith("/start") or msg.text.startswith("/register"):
        return True

    if not esta_registrado(uid):
        await msg.reply_text("❌ Debes registrarte con /register")
        return False

    return True



# ==============================
# /START
# ==============================

async def start(update, context):

    base = os.path.dirname(os.path.abspath(__file__))
    img = os.path.join(base, "Bienvenida.jpeg")

    caption = (
        "<b>✨ BIENVENIDO A BUDA MARKET ✨</b>\n\n"
        "Sistema profesional de gestión para comisionistas y vendedores.\n\n"
        "📌 Comandos:\n"
        "• /register – Registrar usuario\n"
        "• /servicios – Menú principal\n"
        "• /me – Mi información\n"
        "• /referencias – Canal oficial\n"
    )

    with open(img, "rb") as f:
        await update.message.reply_photo(photo=f, caption=caption, parse_mode="HTML")



# ==============================
# /REGISTER
# ==============================

async def register(update, context):

    user = update.effective_user
    uid = str(user.id)
    data = load_json(USERS_FILE)

    # 🛑 Si ya está registrado
    if uid in data:
        await update.message.reply_text(
            f"❌ Ya estás registrado, <b>{user.first_name}</b>.",
            parse_mode="HTML"
        )
        return

    # ✔ Registrar nuevo usuario
    rol = "owner" if es_owner(user.id) else "usuario"

    data[uid] = {
        "nombre": user.first_name,
        "username": user.username,
        "rol": rol
    }

    save_json(USERS_FILE, data)

    await update.message.reply_text(
        f"✅ Registro completado correctamente, <b>{user.first_name}</b>.",
        parse_mode="HTML"
    )


# ==============================
# /ME — Info del usuario (MEJORADO)
# ==============================

async def me(update, context):

    if not await check_registro(update):
        return

    user = update.effective_user
    uid = str(user.id)
    data = load_json(USERS_FILE).get(uid, {})

    # Rol y Verificación
    if es_owner(user.id):
        rol = "👑 <b>Owner</b>"
        verificado = "🟩 <b>Verificado</b> ✔️"
    elif es_revendedor(uid):
        rol = "🟦 <b>Revendedor</b>"
        verificado = "🟩 <b>Verificado</b> ✔️"
    else:
        rol = "👤 <b>Usuario</b>"
        verificado = "🟥 <b>No verificado</b> ❌"

    # Mensaje elegante
    msg = (
        "📌 <b>PERFIL DEL USUARIO</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>Nombre:</b> {data.get('nombre')}\n"
        f"💬 <b>Usuario:</b> @{data.get('username')}\n"
        f"🏷 <b>Rol:</b> {rol}\n"
        f"{verificado}\n"
        f"🆔 <b>ID:</b> <code>{uid}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✨ Gracias por ser parte de <b>BUDA MARKET</b>"
    )

    # Intentar enviar la imagen
    base = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base, "me.jpg")

    try:
        with open(img_path, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=msg,
                parse_mode="HTML"
            )
    except:
        # Si la imagen falla, enviar solo el texto
        await update.message.reply_text(msg, parse_mode="HTML")

# ==============================
# /INFO — Consultar info de otro usuario
# ==============================

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Verificar registro del que ejecuta el comando
    if not await check_registro(update):
        return

    message = update.message

    # 1️⃣ SI RESPONDE A UN MENSAJE → obtener ID del usuario respondido
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        target_id = str(target_user.id)

    # 2️⃣ SI ENVÍA UN ID COMO ARGUMENTO
    elif context.args:
        target_id = context.args[0].strip()

        # Validar que sea numérico
        if not target_id.isdigit():
            return await message.reply_text("❌ Debes ingresar un ID válido.")
        
        # Para mostrar nombre/username si existen
        target_user = None  

    else:
        return await message.reply_text(
            "❗ Uso correcto:\n"
            "• <code>/info &lt;id_usuario&gt;</code>\n"
            "• Responde a un mensaje y usa /info",
            parse_mode="HTML"
        )

    # ==============================
    # Buscar datos del usuario en usuarios.json
    # ==============================
    usuarios = load_json(USERS_FILE)

    if target_id not in usuarios:
        return await message.reply_text(
            f"❌ El usuario con ID <code>{target_id}</code> no está registrado.",
            parse_mode="HTML"
        )

    data = usuarios[target_id]

    nombre = data.get("nombre", "Sin nombre")
    username = data.get("username", None)

    # ==============================
    # Determinar rol y verificación
    # ==============================
    if es_owner(int(target_id)):
        rol = "👑 <b>Owner</b>"
        verificado = "🟩 <b>Verificado</b> ✔️"
    elif es_revendedor(target_id):
        rol = "🟦 <b>Revendedor</b>"
        verificado = "🟩 <b>Verificado</b> ✔️"
    else:
        rol = "👤 <b>Usuario</b>"
        verificado = "🟥 <b>No verificado</b> ❌"

    # ==============================
    # Armar mensaje elegante
    # ==============================
    msg = (
        "📌 <b>INFORMACIÓN DEL USUARIO</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>Nombre:</b> {nombre}\n"
        f"💬 <b>Usuario:</b> @{username}\n"
        f"🏷 <b>Rol:</b> {rol}\n"
        f"{verificado}\n"
        f"🆔 <b>ID:</b> <code>{target_id}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✨ Consulta realizada en <b>BUDA MARKET</b>"
    )

    # ==============================
    # Intentar enviar la imagen me.jpg
    # ==============================
    base = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base, "me.jpg")

    try:
        with open(img_path, "rb") as photo:
            await message.reply_photo(
                photo=photo,
                caption=msg,
                parse_mode="HTML"
            )
    except:
        await message.reply_text(msg, parse_mode="HTML")
                

# ==============================
# /ANUNCIO — SOLO OWNERS
# ==============================

async def anuncio(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    # Solo owners
    if user.id not in OWNERS:
        await update.message.reply_text("❌ No tienes permisos para usar este comando.")
        return

    # No mensaje
    if not context.args:
        await update.message.reply_text("❗ Uso:\n/anuncio <mensaje>")
        return

    mensaje = " ".join(context.args)

    usuarios = load_json(USERS_FILE)
    grupos = load_grupos()

    enviados = 0
    fallidos = []

    # Imagen del anuncio
    base = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base, "Anuncio.jpeg")

    # 📤 ENVIAR A USUARIOS
    for uid in usuarios.keys():
        try:
            with open(img_path, "rb") as f:
                await context.bot.send_photo(
                    chat_id=int(uid),
                    photo=f,
                    caption=f"📢 <b>ANUNCIO IMPORTANTE</b>\n\n{mensaje}",
                    parse_mode="HTML"
                )
            enviados += 1
        except Exception as e:
            fallidos.append(f"Usuario {uid}: {e}")

    # 📤 ENVIAR A GRUPOS
    for gid, data in grupos.items():
        try:
            with open(img_path, "rb") as f:
                await context.bot.send_photo(
                    chat_id=int(gid),
                    photo=f,
                    caption=f"📣 <b>ANUNCIO GLOBAL</b>\n\n{mensaje}",
                    parse_mode="HTML"
                )
            enviados += 1
        except Exception as e:
            fallidos.append(f"Grupo {gid}: {e}")

    # 📌 Resumen
    final = f"✅ Anuncio enviado.\n📤 Total enviados: {enviados}\n"

    if fallidos:
        final += "⚠️ Fallidos:\n" + "\n".join(fallidos)

    await update.message.reply_text(final, parse_mode="HTML")

# ==============================
# /ANUNCIOCHIP — OWNER o REVENDEDOR
# ==============================

async def anunciochip(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    uid = str(user.id)
    uid_int = user.id

    # 🔒 SOLO OWNERS O REVENDEDORES
    if not (es_owner(uid_int) or es_revendedor(uid)):
        await update.message.reply_text(
            "⛔ No tienes permisos para usar este comando.\n\n"
            "Este anuncio solo puede ser enviado por revendedores verificados o owners.\n\n"
            "Para convertirte en revendedor contacta:\n"
            "• @budaoficial2008\n"
            "• @ElRealCheffcito",
            parse_mode="HTML"
        )
        return

    # 📌 SOLO se envía al usuario que lo invoca
    chat_id = user.id

    base = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base, "chip.jpeg")

    texto = (
        "🚀𝐕𝐄𝐍𝐓𝐀 𝐃𝐄 𝐂𝐇𝐈𝐏𝐒 𝐀𝐂𝐓𝐈𝐕𝐀𝐃𝐎𝐒 🚀\n\n"
        "📌𝗢𝗣𝗘𝗥𝗔𝗗𝗢𝗥𝗘𝗦 𝗗𝗜𝗦𝗣𝗢𝗡𝗜𝗕𝗟𝗘𝗦:\n"
        "✅Claro\n"
        "✅Movistar\n"
        "✅Entel\n"
        "✅Bitel\n\n"
        "💰Precio: S/6,50 cada chip\n"
        "📦Pedido mínimo: 20 unidades\n"
        "🚚Envíos por SHALOM\n"
        "📌Despacho INMEDIATO a cualquier parte del Perú\n\n"
        "🔐Chips registrados, seguros y listos para usar\n"
        "📲Ideal para uso personal, negocios y reventa\n\n"
        "💬Pedidos al inbox\n"
        "🆘Envíos a todo el Perú🆘"
    )

    try:
        with open(img_path, "rb") as img:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=img,
                caption=texto,
                parse_mode="HTML"
            )

        await update.message.reply_text(
            "📨 Tu anuncio de *chips activados* fue enviado a tu bandeja privada.",
            parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error enviando el anuncio: {e}")

# ==============================
# /ANUNCIOG5 — OWNER o REVENDEDOR
# ==============================

async def anunciog5(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    uid = str(user.id)
    uid_int = user.id

    # 🔒 SOLO OWNERS O REVENDEDORES
    if not (es_owner(uid_int) or es_revendedor(uid)):
        await update.message.reply_text(
            "⛔ No tienes permisos para usar este comando.\n\n"
            "Este anuncio solo puede ser enviado por revendedores verificados o owners.\n\n"
            "Para convertirte en revendedor contacta:\n"
            "• @budaoficial2008\n"
            "• @ElRealCheffcito",
            parse_mode="HTML"
        )
        return

    # 📌 SOLO se envía al usuario que lo invoca
    chat_id = user.id

    base = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base, "billetes.jpeg")

    texto = (
        "🔥 <b>𝐁𝐈𝐋𝐋𝐄𝐓𝐄𝐒 𝐆5️⃣</b> 🔥\n\n"
        "✅ Calidad <b>10/10</b> ultra realista\n"
        "✅ Papel <b>100% algodón</b>\n"
        "✅ Marca de agua\n"
        "✅ Sellos y firmas originales\n\n"
        "📦 Envíos a todo el Perú\n"
        "🚚 Despacho rápido por <b>SHALOM</b>\n\n"
        "📌 <b>Stock limitado</b>\n\n"
        "🏅 <b>CERTIFICADO EN RDB</b>"
    )

    try:
        with open(img_path, "rb") as img:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=img,
                caption=texto,
                parse_mode="HTML"
            )

        await update.message.reply_text(
            "📨 Tu anuncio de *Billetes G5* fue enviado a tu bandeja privada.",
            parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error enviando el anuncio: {e}")

# ==============================
# MENÚ PRINCIPAL (FOTO + CAPTION + BOTONES)
# ==============================

def menu_principal_keyboard():

    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💻 DNI", callback_data="dni"),
         InlineKeyboardButton("🤵 Universitario", callback_data="uni")],

        [InlineKeyboardButton("🚗 Vehículos", callback_data="lic"),
         InlineKeyboardButton("♿ CONADIS", callback_data="conadis")],

        [InlineKeyboardButton("🏛 Institucional", callback_data="inst"),
         InlineKeyboardButton("🆕 Nuevos", callback_data="new")],
        
        [InlineKeyboardButton("💸 Billetes", callback_data="bill")]
    ])


async def servicios(update, context):

    if not await check_registro(update):
        return

    uid = str(update.effective_user.id)
    uid_int = update.effective_user.id  # ← para owners

    # 🔒 SOLO OWNERS Y REVENDEDORES
    if not (es_owner(uid_int) or es_revendedor(uid)):
        await update.message.reply_text(
            "⛔ No puedes usar este comando porque no eres revendedor.\n\n"
            "Para convertirte en revendedor verificado contacta con:\n"
            "• @budaoficial2008\n"
            "• @ElRealCheffcito",
            parse_mode="HTML"
        )
        return

    base = os.path.dirname(os.path.abspath(__file__))
    menu_path = os.path.join(base, "Menu.jpeg")

    caption = (
        "<b>💼 LISTA DE PRECIOS ACTUALIZADOS</b>\n\n"
        "Seleccione una categoría:"
    )

    with open(menu_path, "rb") as f:
        msg = await update.message.reply_photo(
            photo=f,
            caption=caption,
            parse_mode="HTML",
            reply_markup=menu_principal_keyboard()
        )

    # 🔒 GUARDAR PROPIETARIO DEL MENÚ
    menus = load_menus()
    menus[str(msg.message_id)] = uid  # guardar como string
    save_menus(menus)



# ==============================
# SUBMENÚS — CONTENIDO
# ==============================

SERVICIOS = {

    "dni": (
        "💻 <b>DOCUMENTOS DE IDENTIDAD – DNI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🟡 <b>DNI Amarillo</b>\n"
        "   ▸ Vender: <b>S/75</b>\n"
        "   ▸ Comisionista: <b>S/55</b>\n\n"
        "🔵 <b>DNI Azul (sin QR)</b>\n"
        "   ▸ Vender: <b>S/75</b>\n"
        "   ▸ Comisionista: <b>S/50</b>\n\n"
        "🟦 <b>DNI con QR</b>\n"
        "   ▸ Vender: <b>S/85</b>\n"
        "   ▸ Comisionista: <b>S/55</b>\n\n"
        "💳 <b>DNI Electrónico V2</b>\n"
        "   ▸ Vender: <b>S/125</b>\n"
        "   ▸ Comisionista: <b>S/75</b>\n\n"
        "💳 <b>DNI Electrónico V4</b>\n"
        "   ▸ Vender: <b>S/125</b>\n"
        "   ▸ Comisionista: <b>S/75</b>"
    ),


    "uni": (
        "🎓 <b>CÉDULAS UNIVERSITARIAS</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎫 <b>Carnet Universitario (válido hasta 12/2026)</b>\n"
        "   ▸ Vender: <b>S/55+</b>\n"
        "   ▸ Comisionista: <b>S/45</b>"
    ),


    "lic": (
        "🚗 <b>LICENCIAS Y DOCUMENTOS VEHICULARES</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🪪 <b>Licencia de Conducir (3D impreso)</b>\n"
        "   ▸ Vender: <b>S/85</b>\n"
        "   ▸ Comisionista: <b>S/55</b>\n\n"
        "📄 <b>Tarjeta de Propiedad Física</b>\n"
        "   ▸ Vender: <b>S/55</b>\n"
        "   ▸ Comisionista: <b>S/35</b>"
    ),


    "conadis": (
        "♿ <b>CÉDULAS CONADIS</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🟡 <b>CONADIS Amarillo</b>\n"
        "   ▸ Vender: <b>S/125</b>\n"
        "   ▸ Comisionista: <b>S/75</b>\n\n"
        "🔵 <b>CONADIS Azul</b>\n"
        "   ▸ Vender: <b>S/125</b>\n"
        "   ▸ Comisionista: <b>S/75</b>\n\n"
        "📌 <i>Subido a sistema · Verificado con QR · Sin recojo en municipalidad</i>"
    ),


    "inst": (
        "🏛 <b>CÉDULAS INSTITUCIONALES (A/P)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "👮 <b>Carnet PNP 2025 (CIP)</b>\n"
        "   ▸ Vender: <b>S/95</b>\n"
        "   ▸ Comisionista: <b>S/55</b>\n\n"
        "🚒 <b>Carnet Bombero</b>\n"
        "   ▸ Vender: <b>S/125</b>\n"
        "   ▸ Comisionista: <b>S/75</b>\n\n"
        "🛂 <b>Carnet de Extranjería</b>\n"
        "   ▸ Vender: <b>S/95</b>\n"
        "   ▸ Comisionista: <b>S/55</b>"
    ),


    "bill": (
        "💸 <b>PAQUETES DE BILLETES</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"

        "📦 <b>PAQUETE 1️⃣</b>\n"
        "💵 5 Billetes de 100\n"
        "   ▸ Precio revendedor: <b>S/190</b>\n"
        "   ▸ Precio para vender: <b>S/200</b>\n\n"
        "⸻\n\n"

        "📦 <b>PAQUETE 2️⃣</b>\n"
        "💵 10 Billetes de 100\n"
        "   ▸ Precio revendedor: <b>S/380</b>\n"
        "   ▸ Precio para vender: <b>S/400</b>"
    ),
}


# ==============================
# BOTÓN VOLVER AL MENÚ
# ==============================

def volver_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Volver al menú", callback_data="volver_menu")]
    ])


async def volver_menu(update, context):

    q = update.callback_query

    caption = (
        "<b>💼 LISTA DE PRECIOS ACTUALIZADOS</b>\n\n"
        "Seleccione una categoría:"
    )

    await q.edit_message_caption(
        caption=caption,
        parse_mode="HTML",
        reply_markup=menu_principal_keyboard()
    )



# ==============================
# CALLBACK CENTRAL
# ==============================

async def callback_handler(update, context):

    q = update.callback_query
    data = q.data
    uid = str(q.from_user.id)

    # ============================
    # 🔐 VALIDAR PROPIETARIO DEL MENÚ
    # ============================
    menus = load_menus()
    message_id = str(q.message.message_id)
    owner_uid = menus.get(message_id)

    # BLOQUEAR ACCESO A MENÚ AJENO
    if owner_uid is not None and owner_uid != uid:
        return await q.answer(
            "⛔ Este menú no te pertenece.\n"
            "Solo puedes interactuar con el menú que tú ejecutaste.",
            show_alert=True
        )

    # ============================
    # ✔ ACCIONES PERMITIDAS
    # ============================
    await q.answer()  # ← AHORA SÍ PUEDE ESTAR AQUÍ

    if data in SERVICIOS:
        return await q.edit_message_caption(
            caption=SERVICIOS[data],
            parse_mode="HTML",
            reply_markup=volver_keyboard()
        )

    if data == "volver_menu":
        return await volver_menu(update, context)

# ==============================
# /REFERENCIAS
# ==============================

async def referencias(update, context):

    msg = (
    "<b>📢 Canal Oficial de Referencias RDB</b>\n"
    "https://t.me/referenciasRdb\n\n"

    "<b>En este canal podrá:</b>\n"
    "• Ver referencias reales y verificadas\n"
    "• Confirmar que trabajas como revendedor certificado\n"
    "• Comprobar que el proyecto opera de forma legal y organizada\n"
    "• Revisar el staff de vendedores certificados y autorizados\n\n"

    "<i>Este canal existe para brindar transparencia, confianza y respaldo a cada venta realizada.</i>\n\n"

    "🛡 <b>RDB</b> es un proyecto verificado, operado bajo el mandato y supervisión de <b>Buda</b>.\n\n"

    "👑 <b>Proyecto autorizado por:</b>\n"
    "➤ @budaoficial2008\n\n"

    "<b>Invitar a tus clientes a este canal fortalece tu credibilidad y ayuda a cerrar ventas de manera segura.</b>"
)


    await update.message.reply_text(msg, parse_mode="HTML")

# ==============================
# /VERIFICAR — SOLO OWNERS
# ==============================

async def verificar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    # Solo owners pueden verificar
    if not es_owner(user.id):
        await update.message.reply_text("❌ No tienes permisos para usar este comando.")
        return

    # Validar argumento
    if not context.args:
        await update.message.reply_text("❗ Uso correcto:\n/verificar <id_usuario>")
        return

    target_id = context.args[0].strip()
    usuarios = load_json(USERS_FILE)

    # Verificar que el usuario exista
    if target_id not in usuarios:
        await update.message.reply_text(
            f"❌ El usuario con ID <code>{target_id}</code> no está registrado.",
            parse_mode="HTML"
        )
        return

    # Datos del usuario
    nombre = usuarios[target_id].get("nombre", "Desconocido")
    username = usuarios[target_id].get("username", None)

    # Cargar archivo de revendedores
    revs = load_json(REV_FILE)

    # Guardar info completa
    revs[target_id] = {
        "nombre": nombre,
        "username": username,
        "verificado": True
    }

    save_json(REV_FILE, revs)

    # Respuesta bonita
    await update.message.reply_text(
        f"✅ <b>Revendedor Verificado</b>\n"
        f"• 👤 <b>Nombre:</b> {nombre}\n"
        f"• 💬 <b>Usuario:</b> @{username}\n"
        f"• 🆔 <b>ID:</b> <code>{target_id}</code>\n\n"
        f"✨ Ahora está marcado como <b>VERIFICADO</b>.",
        parse_mode="HTML"
    )

# ==============================
# /REVVENDEDORES — Lista de verificados
# ==============================

async def revendedores(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Solo owners pueden ver lista completa
    user = update.effective_user
    if not es_owner(user.id):
        await update.message.reply_text("❌ No tienes permisos para usar este comando.")
        return

    revs = load_json(REV_FILE)

    # Si no hay revendedores registrados
    if not revs:
        await update.message.reply_text(
            "📭 <b>No hay revendedores verificados aún.</b>",
            parse_mode="HTML"
        )
        return

    msg = (
        "🟦 <b>LISTA DE REVENDEDORES VERIFICADOS</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    # Recorrer todos los revendedores
    for uid, data in revs.items():

        nombre = data.get("nombre", "Sin nombre")
        username = data.get("username", None)

        msg += (
            f"👤 <b>Nombre:</b> {nombre}\n"
            f"💬 <b>Usuario:</b> @{username}\n"
            f"🆔 <b>ID:</b> <code>{uid}</code>\n"
            f"✔ <b>Verificado</b>\n"
            "────────────────────\n"
        )

    await update.message.reply_text(msg, parse_mode="HTML")

# ==============================
# /DELREVENDEDOR — Quitar verificación
# ==============================

# ==============================
# /DELREVENDEDOR — Quitar verificación y rol
# ==============================

async def delrevendedor(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    # Solo owners pueden quitar verificados
    if not es_owner(user.id):
        await update.message.reply_text("❌ No tienes permisos para usar este comando.")
        return

    # Debe enviar un ID
    if not context.args:
        await update.message.reply_text("❗ Uso: /delrevendedor <id_usuario>")
        return

    target_id = context.args[0].strip()

    # ==============================
    # 1. Cargar archivos
    # ==============================
    revs = load_json(REV_FILE)
    users = load_json(USERS_FILE)

    # ==============================
    # 2. Validar existencia en revendedores.json
    # ==============================
    if target_id not in revs:
        await update.message.reply_text(
            f"⚠️ El usuario con ID <code>{target_id}</code> <b>NO está registrado como revendedor.</b>",
            parse_mode="HTML"
        )
        return

    # ==============================
    # 3. Eliminar de revendedores.json
    # ==============================
    del revs[target_id]
    save_json(REV_FILE, revs)

    # ==============================
    # 4. Actualizar usuarios.json → cambiar rol a usuario
    # ==============================
    if target_id in users:
        users[target_id]["rol"] = "usuario"
        save_json(USERS_FILE, users)

        nombre = users[target_id].get("nombre", "Desconocido")
        username = users[target_id].get("username", "Sin username")

        info_extra = (
            f"👤 <b>Nombre:</b> {nombre}\n"
            f"💬 <b>Usuario:</b> @{username}\n"
        )
    else:
        info_extra = "⚠️ <i>Usuario no encontrado en usuarios.json</i>\n"

    # ==============================
    # 5. Mensaje final elegante
    # ==============================

    await update.message.reply_text(
        "🗑️ <b>Revendedor eliminado correctamente</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{info_extra}"
        f"🆔 <b>ID:</b> <code>{target_id}</code>\n"
        "❌ Ya no figura como revendedor verificado.\n"
        "🔄 Rol cambiado a: <b>Usuario</b>",
        parse_mode="HTML"
    )
# ==============================
# Lista de Comandos
# ==============================
async def listacomandos(update, context):

    uid = update.effective_user.id
    uid_str = str(uid)

    esOwner = es_owner(uid)
    esRev = es_revendedor(uid_str)

    # === COMMANDS LISTS ===

    comandos_generales = (
        "👤 <b>Comandos generales</b>\n"
        "• /start – Iniciar bot y ver bienvenida\n"
        "• /register – Registrar usuario\n"
        "• /me – Ver tu información\n"
        "• /info – Ver información de otro usuario\n"
        "• /referencias – Canal oficial de referencias\n\n"
    )

    comandos_rev = (
        "💼 <b>Comandos para revendedores</b>\n"
        "• /servicios – Ver lista de precios\n"
        "• /anunciochip – Mostrar anuncio privado de chips\n"
        "• /anunciog5 – Mostrar anuncio privado de g5\n"
        "• /dnis <numero_dni> – Mostrar Informacion de Dni\n\n"
    )

    comandos_owner = (
        "👑 <b>Comandos exclusivos de Owner</b>\n"
        "• /verificar – Verificar revendedor\n"
        "• /revendedores – Ver lista de revendedores\n"
        "• /delrevendedor – Eliminar verificación\n"
        "• /anuncio – Enviar anuncio global\n"
        "• /listacomandos – Ver este menú\n"
        "• /dnis <numero_dni> – Mostrar Informacion de Dni\n\n"
    )

    # === WHO SEES WHAT ===

    if esOwner:
        msg = (
            "📜 <b>LISTA COMPLETA DE COMANDOS</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{comandos_generales}"
            f"{comandos_rev}"
            f"{comandos_owner}"
        )

    elif esRev:
        msg = (
            "📜 <b>COMANDOS DISPONIBLES</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{comandos_generales}"
            f"{comandos_rev}"
        )

    else:
        msg = (
            "📜 <b>COMANDOS DISPONIBLES</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{comandos_generales}"
        )

    return await update.message.reply_text(msg, parse_mode="HTML")

# ==============================
# soporte
# ==============================
async def soporte(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = (
        "🛠 <b>SOPORTE ⚙️</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "✅ @EmperadorQin\n"
        "✅ @budaoficial2008\n"
        "✅ @ElRealCheffcito\n\n"
        "📌 <i>Contacta a cualquiera de ellos para soporte oficial.</i>"
    )

    await update.message.reply_text(msg, parse_mode="HTML")

# ==============================
# Info DNI
# ==============================
async def dnis(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("❗ Uso correcto:\n/dnis <dni>")
        return

    dni = context.args[0].strip()

    if not dni.isdigit() or len(dni) != 8:
        await update.message.reply_text("❌ DNI inválido.")
        return

    url = "https://web-production-da283.up.railway.app/dni"
    params = {
        "dni": dni,
        "key": "DJjcSK2nXTEIpexi"
    }

    try:
        r = requests.get(url, params=params, timeout=15)
        res = r.json()
    except Exception:
        await update.message.reply_text("❌ Error al conectar con la API.")
        return

    if not res.get("success"):
        await update.message.reply_text("❌ No se pudo obtener información.")
        return

    data = res.get("data", {})
    datos = data.get("datos", {})

    # 📄 MENSAJE
    msg = (
        "🪪 <b>CONSULTA DNI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>Nombre:</b> {data.get('nombre')}\n"
        f"🆔 <b>DNI:</b> <code>{data.get('dni')}</code>\n\n"
        f"🎂 <b>Fecha Nac.:</b> {datos.get('Fecha de Nacimiento')}\n"
        f"📊 <b>Edad:</b> {datos.get('Edad')}\n"
        f"⚧ <b>Sexo:</b> {datos.get('Sexo')}\n"
        f"💍 <b>Estado Civil:</b> {datos.get('Estado')}\n\n"
        f"👨 <b>Padre:</b> {datos.get('Padre')}\n"
        f"👩 <b>Madre:</b> {datos.get('Madre')}\n\n"
        f"📍 <b>Ubicación:</b>\n"
        f"{datos.get('Ubicación')}\n"
        f"{datos.get('Dirección')}\n\n"
        f"🗂 <b>Ubigeo Nac.:</b> {datos.get('Ubigeo Nacimiento')}\n"
        f"⚰ <b>Fallecido:</b> {datos.get('Fecha de Fallecimiento')}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔐 <i>Uso interno - BUDA MARKET</i>"
    )

    # 📸 FOTO
    foto = data.get("foto")

    if foto and foto.startswith("data:image"):
        try:
            base64_img = foto.split(",")[1]
            img_bytes = base64.b64decode(base64_img)

            bio = BytesIO(img_bytes)
            bio.name = "dni.jpg"

            await update.message.reply_photo(
                photo=bio,
                caption=msg,
                parse_mode="HTML"
            )
            return
        except Exception:
            pass

    await update.message.reply_text(msg, parse_mode="HTML")


# ==============================
# MAIN
# ==============================

def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(CommandHandler("me", me))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("dnis", dnis))
    app.add_handler(CommandHandler("soporte", soporte))
    app.add_handler(CommandHandler("verificar", verificar))
    app.add_handler(CommandHandler("listacomandos", listacomandos))
    app.add_handler(CommandHandler("revendedores", revendedores))
    app.add_handler(CommandHandler("delrevendedor", delrevendedor))
    app.add_handler(CommandHandler("anuncio", anuncio))
    app.add_handler(CommandHandler("anunciochip", anunciochip))
    app.add_handler(CommandHandler("anunciog5", anunciog5))
    app.add_handler(CommandHandler("servicios", servicios))
    app.add_handler(CommandHandler("referencias", referencias))

    app.add_handler(CallbackQueryHandler(callback_handler))
    # --- AUTO REGISTRO DE GRUPOS ---
    from telegram.ext import ChatMemberHandler, MessageHandler, filters

    # Detecta cuando el bot es agregado o expulsado de un grupo
    app.add_handler(ChatMemberHandler(auto_register_group, ChatMemberHandler.MY_CHAT_MEMBER))

    # Detecta grupos antiguos cuando alguien escribe un mensaje
    app.add_handler(MessageHandler(filters.ALL, auto_register_group_on_message))

    print("🔥 BUDA MARKET BOT INICIADO…")
    app.run_polling()


if __name__ == "__main__":
    main()
