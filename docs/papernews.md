# MOA MODULE: PAPERNEWS (Ver. 1.0)

## 1. PROPÓSITO
Automatizar la lectura de periódicos digitales y el envío de resúmenes por correo electrónico a las 3:00 AM (Chile).

## 2. COMPONENTES
- `core/cron.py`: Gestiona el programador de tareas.
- `adapters/browser.py`: Utiliza Playwright para navegar por sitios de noticias.
- `adapters/email.py`: Conector SMTP para el envío de resultados.

## 3. CONFIGURACIÓN
Requiere las siguientes variables en `.env`:
- `SMTP_SERVER`: Servidor de correo.
- `SMTP_USER`: Usuario.
- `SMTP_PASS`: Contraseña.
- `RECIPIENT_EMAIL`: Destinatario.

## 4. FLUJO DE TRABAJO
1. **Trigger**: El cron activa la tarea a las 03:00.
2. **Scraping**: MOA abre un navegador headless y extrae titulares de El Mercurio, La Tercera, etc.
3. **Summarizing**: El Agente `analyst` procesa los datos brutos.
4. **Dispatch**: El Agente `writer` redacta el correo y lo envía.
