import type { ApiClient } from '~/lib/api/types'

export interface RegistrationDocumentRequirement {
  type: string
  version: string
  title: string
  url: string
  acceptance_required?: boolean
  acknowledgement_required?: boolean
}

export interface RegistrationRequirements {
  documents: RegistrationDocumentRequirement[]
  marketingConsent: {
    available: boolean
    required: boolean
  }
}

export interface LegalDocument {
  type: string
  version: string
  title: string
  url: string
  contentMarkdown: string
  effectiveAt: string
  publishedAt: string
  requiresReacceptance: boolean
  changeSummary: string | null
}

export interface PendingLegalDocument {
  type: string
  version: string
  title: string
  url: string
}

export interface LegalComplianceStatus {
  isCompliant: boolean
  pendingDocuments: PendingLegalDocument[]
}

export interface UserLegalDocuments {
  documents: Array<{
    type: string
    version: string
    title: string
    url: string
    acceptedAt: string
    consentType: string
  }>
  marketingConsent: {
    optedIn: boolean
    updatedAt: string | null
  }
}

export interface LegalAcceptanceInput {
  documentType: string
  version: string
  accepted?: boolean
  acknowledged?: boolean
}

interface RegistrationRequirementsDto {
  documents: Array<{
    type: string
    version: string
    title: string
    url: string
    acceptance_required?: boolean
    acknowledgement_required?: boolean
  }>
  marketing_consent: { available: boolean, required: boolean }
}

interface LegalDocumentDto {
  type: string
  version: string
  title: string
  url: string
  content_markdown: string
  effective_at: string
  published_at: string
  requires_reacceptance: boolean
  change_summary: string | null
}

interface ComplianceStatusDto {
  is_compliant: boolean
  pending_documents: Array<{
    type: string
    version: string
    title: string
    url: string
  }>
}

interface UserDocumentsDto {
  documents: Array<{
    type: string
    version: string
    title: string
    url: string
    accepted_at: string
    consent_type: string
  }>
  marketing_consent: {
    opted_in: boolean
    updated_at: string | null
  }
}

export function createLegalRepository(api: ApiClient) {
  return {
    async getRegistrationRequirements(): Promise<RegistrationRequirements> {
      const dto = await api.get<RegistrationRequirementsDto>(
        '/legal/registration-requirements',
        { skipAuth: true },
      )
      return {
        documents: dto.documents,
        marketingConsent: {
          available: dto.marketing_consent.available,
          required: dto.marketing_consent.required,
        },
      }
    },

    async getDocument(documentType: string): Promise<LegalDocument> {
      const dto = await api.get<LegalDocumentDto>(
        `/legal/documents/${documentType}`,
        { skipAuth: true },
      )
      return {
        type: dto.type,
        version: dto.version,
        title: dto.title,
        url: dto.url,
        contentMarkdown: dto.content_markdown,
        effectiveAt: dto.effective_at,
        publishedAt: dto.published_at,
        requiresReacceptance: dto.requires_reacceptance,
        changeSummary: dto.change_summary,
      }
    },

    async getStatus(): Promise<LegalComplianceStatus> {
      const dto = await api.get<ComplianceStatusDto>('/legal/me/status')
      return {
        isCompliant: dto.is_compliant,
        pendingDocuments: dto.pending_documents.map(p => ({
          type: p.type,
          version: p.version,
          title: p.title,
          url: p.url,
        })),
      }
    },

    async acceptDocuments(acceptances: LegalAcceptanceInput[]): Promise<LegalComplianceStatus> {
      const dto = await api.post<ComplianceStatusDto>('/legal/me/acceptances', {
        acceptances: acceptances.map(a => ({
          document_type: a.documentType,
          version: a.version,
          accepted: a.accepted,
          acknowledged: a.acknowledged,
        })),
      })
      return {
        isCompliant: dto.is_compliant,
        pendingDocuments: dto.pending_documents.map(p => ({
          type: p.type,
          version: p.version,
          title: p.title,
          url: p.url,
        })),
      }
    },

    async getMyDocuments(): Promise<UserLegalDocuments> {
      const dto = await api.get<UserDocumentsDto>('/legal/me/documents')
      return {
        documents: dto.documents.map(d => ({
          type: d.type,
          version: d.version,
          title: d.title,
          url: d.url,
          acceptedAt: d.accepted_at,
          consentType: d.consent_type,
        })),
        marketingConsent: {
          optedIn: dto.marketing_consent.opted_in,
          updatedAt: dto.marketing_consent.updated_at,
        },
      }
    },

    async setMarketingConsent(accepted: boolean): Promise<{ optedIn: boolean, updatedAt: string | null }> {
      const dto = await api.post<{ opted_in: boolean, updated_at: string | null }>(
        '/legal/me/marketing-consent',
        { accepted },
      )
      return {
        optedIn: dto.opted_in,
        updatedAt: dto.updated_at,
      }
    },
  }
}

export type LegalRepository = ReturnType<typeof createLegalRepository>
