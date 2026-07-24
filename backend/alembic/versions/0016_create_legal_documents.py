"""Create legal_documents and legal_consents tables; seed v1.0 drafts.

Revision ID: 0016_create_legal_documents
Revises: 0015_create_budgets_and_cash_planning
Create Date: 2026-07-24
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0016_create_legal_documents"
down_revision: str | None = "0015_create_budgets_and_cash_planning"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "legal_documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("document_type", sa.String(length=40), nullable=False),
        sa.Column("version", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content_url", sa.String(length=255), nullable=False),
        sa.Column("content_markdown", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("effective_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("requires_reacceptance", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_type", "version", name="uq_legal_documents_type_version"),
    )
    op.create_index(
        "uq_legal_documents_one_active_per_type",
        "legal_documents",
        ["document_type"],
        unique=True,
        postgresql_where=sa.text("is_active IS TRUE"),
    )

    op.create_table(
        "legal_consents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=True),
        sa.Column("legal_document_id", sa.Uuid(), nullable=False),
        sa.Column("consent_type", sa.String(length=40), nullable=False),
        sa.Column("accepted", sa.Boolean(), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("source", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["legal_document_id"], ["legal_documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_legal_consents_user_document_type",
        "legal_consents",
        ["user_id", "legal_document_id", "consent_type"],
    )

    op.execute(
        sa.text(
            """
            INSERT INTO legal_documents (
                id, document_type, version, title, content_url, content_markdown,
                content_hash, effective_at, published_at, is_active,
                requires_reacceptance, change_summary, created_at
            ) VALUES (
                '40d88749-2e28-4f11-9f0a-1bd6461143d4',
                'terms_of_service',
                '1.0',
                'Términos de servicio',
                '/legal/terms',
                '# Términos de servicio

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
',
                '83365e3873fcf0ceb3bbe8d422a83b3497f925b99b9bb8cb1613f9b85fd09ed8',
                '2026-07-24T00:00:00+00:00',
                '2026-07-24T00:00:00+00:00',
                true,
                false,
                'Versión inicial (borrador).',
                '2026-07-24T00:00:00+00:00'
            )
            """
        )
    )
    op.execute(
        sa.text(
            """
            INSERT INTO legal_documents (
                id, document_type, version, title, content_url, content_markdown,
                content_hash, effective_at, published_at, is_active,
                requires_reacceptance, change_summary, created_at
            ) VALUES (
                '61db71ad-45b4-424e-b0b4-452e6b79aa16',
                'privacy_notice',
                '1.0',
                'Aviso de privacidad',
                '/legal/privacy',
                '# Aviso de privacidad

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
',
                '0d7e0606755d9496c9b4908f5431034a8fef30989b67f342dfc43c6f9486ac98',
                '2026-07-24T00:00:00+00:00',
                '2026-07-24T00:00:00+00:00',
                true,
                false,
                'Versión inicial (borrador).',
                '2026-07-24T00:00:00+00:00'
            )
            """
        )
    )
    op.execute(
        sa.text(
            """
            INSERT INTO legal_documents (
                id, document_type, version, title, content_url, content_markdown,
                content_hash, effective_at, published_at, is_active,
                requires_reacceptance, change_summary, created_at
            ) VALUES (
                '6612b117-f886-4ab9-a9f3-0bcebd97a4f1',
                'cookie_policy',
                '1.0',
                'Política de cookies',
                '/legal/cookies',
                '# Política de cookies

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
',
                '6afb28f468f975fe0ae5eb70b7911da0707b7fc427adde0681950478e973754d',
                '2026-07-24T00:00:00+00:00',
                '2026-07-24T00:00:00+00:00',
                true,
                false,
                'Versión inicial (borrador).',
                '2026-07-24T00:00:00+00:00'
            )
            """
        )
    )


def downgrade() -> None:
    op.drop_index("ix_legal_consents_user_document_type", table_name="legal_consents")
    op.drop_table("legal_consents")
    op.drop_index(
        "uq_legal_documents_one_active_per_type",
        table_name="legal_documents",
        postgresql_where=sa.text("is_active IS TRUE"),
    )
    op.drop_table("legal_documents")
