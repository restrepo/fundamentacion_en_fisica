# Verificación en Chromium

```bash
cd /home/claude/out && (setsid python3 -m http.server 8765 >/tmp/srv.log 2>&1 &)
```
Chromium: `/opt/pw-browsers/chromium-*/chrome-linux/chrome` (Playwright).
Espera `document.documentElement.dataset.mathjax === 'ok'` (lo pone
`__leccionTypeset`) antes de medir o capturar.

Comprobar, con `page.on('pageerror')` y la consola abiertas:
1. `document.querySelectorAll('[data-mjx-error]').length === 0`.
2. Recorrido → por todas las diapositivas con capturas y hoja de contactos;
   revisar desbordes, textos cortados, colores fuera de rol.
3. En una diapositiva con fragmentos: ↓ dos veces ⇒ sigue en la misma y
   `.frag-on` = 2; en la hero ↓ no cambia de diapositiva.
4. Ventana emergente (`.prop`): se abre dentro de la diapositiva activa, con
   la matemática en línea.
5. Práctica: opción correcta ⇒ marcador sube; entrada + Enter corrige.
6. Deslizador/selector: cambiar valor dispara la figura (si no se mueve, un
   `value` quedó controlado).
7. Juego: marcar puntos + Comprobar produce retroalimentación.
Tras escribir en un input, hacer `blur()` antes de navegar con teclado
(deck-stage ignora teclas con el foco en campos).
