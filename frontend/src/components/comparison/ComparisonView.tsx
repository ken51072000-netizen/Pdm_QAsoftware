import type { ComparisonResult } from '../../types/report'
import SectionDiff from './SectionDiff'
import RawTextPanel from './RawTextPanel'
import WarningBanner from '../common/WarningBanner'

interface Props {
  result: ComparisonResult
  onReset: () => void
}

function OverallScore({ score }: { score: number }) {
  const pct = Math.round(score * 100)
  const color =
    pct >= 80 ? 'text-green-600' :
    pct >= 50 ? 'text-yellow-600' :
    'text-red-600'
  return (
    <div className="flex items-center gap-2">
      <span className="text-gray-600 text-sm">整體相似度</span>
      <span className={`text-2xl font-bold ${color}`}>{pct}%</span>
    </div>
  )
}

export default function ComparisonView({ result, onReset }: Props) {
  const { consultant_report, software_report, field_comparisons, overall_similarity } = result

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header bar */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-gray-800 mb-1">頻譜分析報告比對結果</h1>
          <div className="flex items-center gap-4 text-xs text-gray-500">
            <span>
              <span className="inline-block w-2 h-2 rounded-full bg-blue-500 mr-1" />
              人工顧問（{consultant_report.page_count} 頁）
            </span>
            <span>
              <span className="inline-block w-2 h-2 rounded-full bg-green-500 mr-1" />
              軟體系統（{software_report.page_count} 頁）
            </span>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <OverallScore score={overall_similarity} />
          <button
            onClick={onReset}
            className="text-sm text-blue-600 hover:text-blue-800 underline"
          >
            重新上傳
          </button>
        </div>
      </div>

      {/* Extraction warnings */}
      {consultant_report.extraction_warning && (
        <div className="mb-4">
          <WarningBanner message={`人工顧問：${consultant_report.extraction_warning}`} />
        </div>
      )}
      {software_report.extraction_warning && (
        <div className="mb-4">
          <WarningBanner message={`軟體系統：${software_report.extraction_warning}`} />
        </div>
      )}

      {/* Confidence info */}
      {(consultant_report.extraction_confidence > 0 || software_report.extraction_confidence > 0) && (
        <div className="mb-4 flex gap-4 text-xs text-gray-400">
          <span>人工顧問擷取信心度：{Math.round(consultant_report.extraction_confidence * 100)}%</span>
          <span>軟體系統擷取信心度：{Math.round(software_report.extraction_confidence * 100)}%</span>
        </div>
      )}

      {/* Section comparisons */}
      <div className="flex flex-col gap-4 mb-6">
        {field_comparisons.map((fc, i) => (
          <SectionDiff key={fc.field_name} comparison={fc} defaultOpen={i === 0} />
        ))}
      </div>

      {/* Raw text panels */}
      <RawTextPanel
        consultantText={consultant_report.raw_text}
        softwareText={software_report.raw_text}
      />
    </div>
  )
}
