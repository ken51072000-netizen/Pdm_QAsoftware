import type { DiffSegment } from '../../types/report'

interface Props {
  segments: DiffSegment[]
}

export default function DiffHighlight({ segments }: Props) {
  if (segments.length === 0) {
    return <p className="text-sm text-gray-400 italic">（無內容）</p>
  }

  return (
    <div className="text-sm leading-relaxed whitespace-pre-wrap break-words">
      {segments.map((seg, i) => {
        if (seg.type === 'equal') {
          return <span key={i}>{seg.text}</span>
        }
        if (seg.type === 'delete') {
          return (
            <span
              key={i}
              className="bg-red-100 text-red-700 line-through"
              title="僅出現於人工顧問報告"
            >
              {seg.text}
            </span>
          )
        }
        // insert
        return (
          <span
            key={i}
            className="bg-green-100 text-green-800"
            title="僅出現於軟體系統報告"
          >
            {seg.text}
          </span>
        )
      })}
    </div>
  )
}
