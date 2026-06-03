# ⚽ WC2026 Injury Tracker

Tracker en tiempo real de lesiones en convocatorias oficiales del Mundial 2026.  
Solo jugadores que estaban en las listas oficiales enviadas a FIFA (1–2 junio 2026).

## Despliegue en Vercel (recomendado — 2 minutos)

### Opción A: sin código (la más fácil)

1. Sube esta carpeta a [github.com](https://github.com) (crea un repo nuevo, arrastra los archivos)
2. Ve a [vercel.com](https://vercel.com) → **Add New Project**
3. Conecta tu repo de GitHub
4. Vercel detecta Vite automáticamente → click **Deploy**
5. ¡Listo! Tendrás una URL pública como `wc2026-injuries.vercel.app`

### Opción B: con CLI

```bash
# Instalar Vercel CLI (solo una vez)
npm i -g vercel

# Desde la carpeta del proyecto
cd wc2026-injuries
npm install
vercel --prod
```

### Opción C: Netlify (igual de fácil)

1. Ve a [netlify.com](https://netlify.com) → **Add new site** → **Deploy manually**
2. Arrastra la carpeta entera al navegador
3. Netlify la despliega automáticamente

---

## Desarrollo local

```bash
npm install
npm run dev
# Abre http://localhost:5173
```

## Build para producción

```bash
npm run build
# Genera /dist listo para subir a cualquier hosting
```

---

## ¿Qué hace la app?

- Muestra los jugadores **oficialmente convocados** al Mundial 2026 que tienen lesiones
- Se actualiza cada **60 minutos** usando la API de Claude para buscar noticias frescas
- Cada jugador tiene un link a la fuente periodística más relevante
- Filtros por estado: Bajas confirmadas / En duda / Recuperados
- Botón de actualización manual

## Jugadores monitoreados

| Jugador | País | Estado |
|---------|------|--------|
| Billy Gilmour | Escocia 🏴󠁧󠁢󠁳󠁣󠁴󠁿 | ❌ Baja confirmada |
| Cho Yumin | Corea del Sur 🇰🇷 | ❌ Baja confirmada |
| Christoph Baumgartner | Austria 🇦🇹 | ❌ Baja confirmada |
| Marcelo Flores | Canadá 🇨🇦 | ❌ Baja confirmada |
| Neymar Jr | Brasil 🇧🇷 | ⚠️ En duda |
| Lionel Messi | Argentina 🇦🇷 | ⚠️ En duda |
| Alphonso Davies | Canadá 🇨🇦 | ⚠️ En duda |
| Lamine Yamal | España 🇪🇸 | ⚠️ En duda |
| William Saliba | Francia 🇫🇷 | ⚠️ En duda |
| Chris Richards | EE.UU. 🇺🇸 | ⚠️ En duda |
| Arda Güler | Turquía 🇹🇷 | ⚠️ En duda |
| Emiliano Martínez | Argentina 🇦🇷 | ⚠️ En duda |

---

Fuentes: ESPN · Al Jazeera · beIN Sports · Olympics.com · Yahoo Sports · Sky Sports · Infobae
