# 🚀 Guía de Despliegue en Railway

## Archivos creados para Railway

1. ✅ `requirements.txt` - Dependencias de Python
2. ✅ `Procfile` - Comando para ejecutar la aplicación
3. ✅ `runtime.txt` - Versión de Python
4. ✅ `.gitignore` - Archivos a ignorar en Git

## 📋 Pasos para desplegar (SIN GitHub)

### ⚠️ IMPORTANTE: Para cuentas con plan limitado, debes crear el proyecto primero desde el dashboard web

### 1. Crear proyecto desde el Dashboard Web
1. Ve a: https://railway.app/dashboard
2. Click en **"New Project"**
3. Selecciona **"Empty Project"** (Proyecto vacío)
4. Railway creará un proyecto nuevo

### 2. Vincular tu proyecto local al de Railway
Desde la terminal en tu carpeta del proyecto:
```bash
railway link
```
Te pedirá seleccionar el proyecto que acabas de crear.

### 3. Configurar variable de entorno (TOKEN)
```bash
railway variables set TELEGRAM_BOT_TOKEN=8203432554:AAGAZjEgMjAIkUAMP-LJoYMobooz6N0Y4ug
```
O desde el dashboard web:
- Ve a tu proyecto → **Variables**
- Click en **"New Variable"**
- Nombre: `TELEGRAM_BOT_TOKEN`
- Valor: `8203432554:AAGAZjEgMjAIkUAMP-LJoYMobooz6N0Y4ug`
- Click en **"Add"**

### 4. Subir el proyecto
```bash
railway up
```
Este comando subirá todos los archivos a Railway y desplegará tu bot.

### Alternativa: Usar Render (más fácil)
Si Railway sigue dando problemas, usa Render (ver `DEPLOY_RENDER.md`)

### 6. (Opcional) Ver los logs
```bash
railway logs
```

### 7. (Opcional) Abrir el dashboard
```bash
railway open
```

## 🔐 Seguridad

⚠️ **IMPORTANTE**: El token del bot ahora se lee desde la variable de entorno `TELEGRAM_BOT_TOKEN`. Asegúrate de configurarla en Railway antes de desplegar.

Si no configuras la variable, el bot usará el token por defecto (no recomendado para producción).

## 📝 Notas

- Los archivos JSON (usuarios.json, grupos.json, etc.) se guardarán en el sistema de archivos de Railway, pero se perderán si el servicio se reinicia.
- Para persistencia de datos, considera usar una base de datos como PostgreSQL o MongoDB.
- Railway ofrece 500 horas gratis al mes para proyectos personales.

