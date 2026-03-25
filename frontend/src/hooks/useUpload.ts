import { useState } from 'react'
import { uploadPdfs, runComparison, ApiError } from '../services/api'
import type { ComparisonResult } from '../types/report'

type Phase = 'idle' | 'uploading' | 'analyzing' | 'done' | 'error'

interface UploadState {
  phase: Phase
  error: string | null
  result: ComparisonResult | null
  uploadAndCompare: (consultant: File, software: File) => Promise<void>
  reset: () => void
}

export function useUpload(): UploadState {
  const [phase, setPhase] = useState<Phase>('idle')
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<ComparisonResult | null>(null)

  const uploadAndCompare = async (consultant: File, software: File) => {
    setPhase('uploading')
    setError(null)
    setResult(null)
    try {
      const { session_id } = await uploadPdfs(consultant, software)
      setPhase('analyzing')
      const comparison = await runComparison(session_id)
      setResult(comparison)
      setPhase('done')
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : '發生未知錯誤，請重試。'
      setError(msg)
      setPhase('error')
    }
  }

  const reset = () => {
    setPhase('idle')
    setError(null)
    setResult(null)
  }

  return { phase, error, result, uploadAndCompare, reset }
}
