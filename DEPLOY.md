# Deploy de Finderz

Esta demo se despliega con:

- Backend FastAPI en Render Web Service
- Frontend Ionic/Vite en Vercel

## 1. Subir el repo a GitHub

Render y Vercel despliegan desde Git. Subi el proyecto completo `Finderz` a GitHub.

## 2. Backend en Render

Opcion recomendada: usar el archivo `render.yaml` del repo.

1. En Render, crea un `Blueprint`.
2. Conecta el repo de GitHub.
3. Render va a leer `render.yaml` y crear el servicio `finderz-api`.
4. Cuando termine, copia la URL publica, por ejemplo:

```txt
https://finderz-api.onrender.com
```

Si lo creas manualmente como Web Service:

```txt
Root Directory: Back
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Health Check Path: /health
```

Para una demo se deja `CORS_ORIGINS=*`. Si queres cerrarlo al dominio de Vercel, cambia esa variable en Render por la URL del front.

## 3. Frontend en Vercel

1. En Vercel, importa el mismo repo.
2. Configura el proyecto con:

```txt
Root Directory: Front/finderz
Framework Preset: Vite
Build Command: npm run build
Output Directory: dist
```

3. En Environment Variables agrega:

```txt
VITE_API_URL=https://finderz-api.onrender.com
```

Usa la URL real que te dio Render.

4. Desplega. Vercel va a publicar el front y la app va a consumir el backend de Render.

## 4. Orden importante

Primero desplega Render, porque Vercel necesita conocer la URL del backend para `VITE_API_URL`.

## Nota

El backend usa memoria en `Back/app/bd.py`. Si Render reinicia el servicio, se restauran los datos iniciales de la demo.
