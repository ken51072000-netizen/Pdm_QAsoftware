export type ReportSource = 'consultant' | 'software'
export type DiffType = 'equal' | 'insert' | 'delete'

export interface DiffSegment {
  type: DiffType
  text: string
}

export interface ExtractedReport {
  source: ReportSource
  raw_text: string
  equipment_threshold: string
  diagnostic_description: string
  improvement_suggestions: string
  page_count: number
  extraction_confidence: number
  extraction_warning: string
}

export interface FieldComparison {
  field_name: string
  field_label_zh: string
  consultant_text: string
  software_text: string
  diff_segments: DiffSegment[]
  similarity_score: number
}

export interface ComparisonResult {
  id: string
  consultant_report: ExtractedReport
  software_report: ExtractedReport
  field_comparisons: FieldComparison[]
  overall_similarity: number
  created_at: string
}

export interface UploadResponse {
  session_id: string
  consultant_page_count: number
  software_page_count: number
}
