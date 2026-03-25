import { useState } from 'react'
import type { FieldComparison } from '../../types/report'
import DiffHighlight from './DiffHighlight'

interface Props {
  comparison: FieldComparison
  defaultOpen?: boolean
}

export default function SectionDiff({ comparison, defaultOpen = false }: Props) {
  const [open, setOpen] = useState(defaultOpen)

  return (
    <div className="border border-gray-200 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-4 py-3 bg-white hover:bg-gray-50 transition-colors text-left"
      >
        <span className="font-semibold text-gray-800">{comparison.field_label_zh}</span>
        <span className="text-gray-400 text-xs">{open ? '▲ 收起' : '▼ 展開'}</span>
      </button>

      {open && (
        <div className="border-t border-gray-100">
          {/* Side-by-side original text */}
          <div className="grid grid-cols-2 divide-x divide-gray-200 border-b border-gray-100">
            {[
              { label: '人工顧問', badgeClass: 'bg-blue-100 text-blue-700', text: comparison.consultant_text },
              { label: '軟體系統', badgeClass: 'bg-green-100 text-green-700', text: comparison.software_text },
            ].map(({ label, badgeClass, text }) => (
              <div key={label} className="p-4">
                <span className={`inline-block text-xs font-semibold px-2 py-0.5 rounded-full mb-2 ${badgeClass}`}>
                  {label}
                </span>
                <p className="text-sm text-gray-700 whitespace-pre-wrap break-words leading-relaxed">
                  {text || <span className="text-gray-400 italic">（未擷取到內容）</span>}
                </p>
              </div>
            ))}
          </div>

          {/* Inline diff */}
          <div className="p-4 bg-gray-50">
            <p className="text-xs text-gray-400 mb-2 flex items-center gap-3">
              差異標示：
              <span className="bg-red-100 text-red-700 line-through px-1 rounded">人工顧問獨有</span>
              <span className="bg-green-100 text-green-800 px-1 rounded">軟體系統獨有</span>
              <span className="text-gray-600">兩者相同</span>
            </p>
            <DiffHighlight segments={comparison.diff_segments} />
          </div>
        </div>
      )}
    </div>
  )
}
