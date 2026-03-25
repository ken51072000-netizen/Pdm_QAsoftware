import type { ComparisonResult } from '../../types/report'
import SectionDiff from './SectionDiff'
import RawTextPanel from './RawTextPanel'
import WarningBanner from '../common/WarningBanner'

interface Props {
  result: ComparisonResult
  onReset: () => void
}

export default function ComparisonView({ result, onReset }: Props) {
  const { consultant_report, software_report, field_comparisons } = result

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
        <button
          onClick={onReset}
          className="text-sm text-blue-600 hover:text-blue-800 underline"
        >
          重新上傳
        </button>
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
