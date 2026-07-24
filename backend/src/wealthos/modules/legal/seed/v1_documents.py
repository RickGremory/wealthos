"""Active v1.0 Spanish draft legal documents (pending legal review)."""

from __future__ import annotations

import hashlib
from typing import TypedDict


class SeedDocument(TypedDict):
    document_type: str
    version: str
    title: str
    content_url: str
    content_markdown: str
    content_hash: str
    requires_reacceptance: bool
    change_summary: str | None


def _hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


TERMS_MARKDOWN = """# Términos de servicio

> **Borrador — pendiente de revisión jurídica**

## 1. Identidad del responsable

WealthOS ("nosotros") opera la plataforma de gestión patrimonial personal disponible en la aplicación web. Para consultas legales o de privacidad: privacy@wealthos.app.

## 2. Aceptación

Al crear una cuenta o usar WealthOS aceptas estos Términos en la versión vigente publicada. Si no estás de acuerdo, no utilices el servicio.

## 3. Descripción del servicio

WealthOS permite registrar cuentas financieras, movimientos, categorías, metas, deudas y herramientas de planificación. El servicio se ofrece "tal cual" para uso personal o de pequeñas organizaciones, sin constituir asesoría financiera, fiscal, contable o de inversión.

## 4. Cuenta y seguridad

Eres responsable de la confidencialidad de tus credenciales y de la exactitud de la información que capturas. Debes notificarnos de uso no autorizado. Podemos suspender cuentas que vulneren estos términos o la ley aplicable.

## 5. Uso permitido

No debes: (a) usar el servicio para actividades ilícitas; (b) intentar vulnerar la seguridad o disponibilidad; (c) revender el acceso sin autorización; (d) cargar contenido que infrinja derechos de terceros.

## 6. Datos y disponibilidad

Procesamos datos conforme al Aviso de privacidad. Nos esforzamos por mantener disponibilidad razonable, pero pueden ocurrir interrupciones por mantenimiento o causas ajenas. No garantizamos resultados financieros ni exactitud absoluta de proyecciones.

## 7. Propiedad intelectual

La marca, interfaz y código de WealthOS son de nuestra titularidad o de licenciantes. Conservas la titularidad de tus datos de cuenta. Nos otorgas una licencia limitada para operar el servicio.

## 8. Limitación de responsabilidad

En la medida permitida por la ley, WealthOS no responde por daños indirectos, lucro cesante o decisiones tomadas con base en la información de la plataforma. La responsabilidad total, si aplica, se limita a lo que hayas pagado por el servicio en los 12 meses previos (o cero si es gratuito).

## 9. Terminación

Puedes dejar de usar el servicio en cualquier momento. Podemos dar de baja cuentas por incumplimiento. Al cierre, aplicaremos el proceso de eliminación descrito en el Aviso de privacidad.

## 10. Cambios

Podemos actualizar estos Términos. Si el cambio requiere nueva aceptación, te lo pediremos en la aplicación. El uso continuado tras cambios no sustanciales implica aceptación cuando la ley lo permita.

## 11. Contacto

privacy@wealthos.app
"""

PRIVACY_MARKDOWN = """# Aviso de privacidad

> **Borrador — pendiente de revisión jurídica**

## 1. Responsable

WealthOS es el responsable del tratamiento de datos personales. Contacto ARCO y privacidad: privacy@wealthos.app.

## 2. Datos que tratamos

Podemos tratar: (a) identidad y contacto (nombre, correo); (b) datos de cuenta (organización, preferencias, zona horaria); (c) datos financieros que tú capturas (saldos, movimientos, categorías, metas, deudas); (d) datos técnicos (IP, user-agent, registros de consentimiento); (e) preferencias de cookies no esenciales si las habilitas.

No solicitamos por defecto datos de salud ni biometría. La IA no está habilitada por defecto; si en el futuro se ofrecen funciones de IA, se pedirá consentimiento específico.

## 3. Finalidades primarias

(a) Crear y administrar tu cuenta; (b) prestar las funciones del producto; (c) autenticación y seguridad; (d) cumplir obligaciones legales; (e) atender derechos ARCO y soporte.

## 4. Finalidades secundarias

Con tu consentimiento opcional: enviar comunicaciones de producto o marketing. Puedes retirar este consentimiento en Ajustes > Privacidad.

## 5. Transferencias

Podemos usar proveedores de infraestructura (hosting, correo, monitoreo) bajo contratos de confidencialidad. No vendemos tus datos personales.

## 6. Derechos ARCO

Puedes solicitar acceso, rectificación, cancelación u oposición, así como limitación o revocación de consentimiento, escribiendo a privacy@wealthos.app. Responderemos conforme a la normativa aplicable (incluida la LFPDPPP en México cuando corresponda).

## 7. Conservación y eliminación

Conservamos datos mientras la cuenta esté activa y el tiempo necesario para obligaciones legales. Al solicitar eliminación de cuenta, borraremos o anonimizaremos datos personales en un plazo razonable, salvo retención legal obligatoria. El flujo completo de borrado vía API se documentará en una versión posterior.

## 8. Seguridad

Aplicamos medidas técnicas y organizativas razonables (control de acceso, cifrado en tránsito, hashing de contraseñas). Ningún sistema es infalible; te pedimos usar contraseñas fuertes y no compartir acceso.

## 9. Menores

El servicio no está dirigido a menores de 18 años.

## 10. Cambios

Publicaremos versiones actualizadas en /legal/privacy. Si requieren nueva aceptación, te lo solicitaremos en la app.

## 11. Contacto

privacy@wealthos.app
"""

COOKIES_MARKDOWN = """# Política de cookies

> **Borrador — pendiente de revisión jurídica**

## 1. Qué son las cookies

Las cookies y tecnologías similares (almacenamiento local) permiten recordar preferencias y mantener la sesión. WealthOS usa principalmente almacenamiento necesario para el funcionamiento del producto.

## 2. Responsable

WealthOS. Consultas: privacy@wealthos.app.

## 3. Cookies esenciales

Siempre activas. Incluyen sesión/autenticación, preferencias de seguridad básicas y elementos técnicos sin los cuales la app no funciona. No requieren consentimiento adicional más allá del uso del servicio.

## 4. Preferencias

Podemos guardar en el dispositivo preferencias de interfaz (idioma, ocultar saldos) y preferencias de cookies no esenciales cuando las configures.

## 5. Analítica y marketing

Por defecto, analítica y marketing están **desactivados**. Si en el futuro se habilitan, pediremos consentimiento explícito y podrás cambiarlo. Esta política describe el marco; no hay banner complejo mientras esas categorías permanezcan deshabilitadas.

## 6. Gestión

Puedes revisar el enlace "Cookies" en la aplicación y borrar datos del navegador. Bloquear cookies esenciales puede impedir el inicio de sesión.

## 7. Datos asociados

Las preferencias de cookies no esenciales, si las activas, se tratan conforme al Aviso de privacidad.

## 8. Cambios

Actualizaremos esta política en /legal/cookies. Uso continuado tras cambios informativos implica conocimiento de la versión publicada.

## 9. Contacto

privacy@wealthos.app
"""

SEED_DOCUMENTS: list[SeedDocument] = [
    {
        "document_type": "terms_of_service",
        "version": "1.0",
        "title": "Términos de servicio",
        "content_url": "/legal/terms",
        "content_markdown": TERMS_MARKDOWN,
        "content_hash": _hash(TERMS_MARKDOWN),
        "requires_reacceptance": False,
        "change_summary": "Versión inicial (borrador).",
    },
    {
        "document_type": "privacy_notice",
        "version": "1.0",
        "title": "Aviso de privacidad",
        "content_url": "/legal/privacy",
        "content_markdown": PRIVACY_MARKDOWN,
        "content_hash": _hash(PRIVACY_MARKDOWN),
        "requires_reacceptance": False,
        "change_summary": "Versión inicial (borrador).",
    },
    {
        "document_type": "cookie_policy",
        "version": "1.0",
        "title": "Política de cookies",
        "content_url": "/legal/cookies",
        "content_markdown": COOKIES_MARKDOWN,
        "content_hash": _hash(COOKIES_MARKDOWN),
        "requires_reacceptance": False,
        "change_summary": "Versión inicial (borrador).",
    },
]
