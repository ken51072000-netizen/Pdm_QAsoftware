import type { ComparisonResult, UploadResponse } from '../types/report'

const BASE = '/api'

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let message = `HTTP ${res.status}`
    try {
      const body = await res.json()
      message = body.detail ?? message
    } catch {
      // ignore JSON parse errors
    }
    throw new ApiError(res.status, message)
  }
  return res.json() as Promise<T>
}

export async function uploadPdfs(
  consultantFile: File,
  softwareFile: File,
): Promise<UploadResponse> {
  const form = new FormData()
  form.append('consultant_pdf', consultantFile)
  form.append('software_pdf', softwareFile)
  const res = await fetch(`${BASE}/upload`, { method: 'POST', body: form })
  return handleResponse<UploadResponse>(res)
}

export async function runComparison(sessionId: string): Promise<ComparisonResult> {
  const res = await fetch(`${BASE}/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId }),
  })
  return handleResponse<ComparisonResult>(res)
}

export async function getApiKeyStatus(): Promise<{ configured: boolean; preview: string }> {
  const res = await fetch(`${BASE}/settings/api-key`)
  return handleResponse(res)
}

export async function saveApiKey(key: string): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${BASE}/settings/api-key`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ key }),
  })
  return handleResponse(res)
}

export async function deleteApiKey(): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${BASE}/settings/api-key`, { method: 'DELETE' })
  return handleResponse(res)
}
