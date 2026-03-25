import { useState } from 'react'

interface Props {
  consultantText: string
  softwareText: string
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)
  const copy = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    })
  }
  return (
    <button
      onClick={copy}
      className="text-xs text-gray-400 hover:text-gray-600 border border-gray-200 rounded px-2 py-0.5"
    >
      {copied ? '已複製' : '複製'}
    </button>
  )
}

export default function RawTextPanel({ consultantText, softwareText }: Props) {
  const [open, setOpen] = useState(false)

  return (
    <div className="border border-gray-200 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors text-left"
      >
        <span className="font-medium text-gray-700 text-sm">原始完整文字（PDF 擷取）</span>
        <span className="text-gray-400 text-xs">{open ? '▲ 收起' : '▼ 展開'}</span>
      </button>
      {open && (
        <div className="grid grid-cols-2 divide-x divide-gray-200">
          {[
            { label: '人工顧問', badgeClass: 'bg-blue-100 text-blue-700', text: consultantText },
            { label: '軟體系統', badgeClass: 'bg-green-100 text-green-700', text: softwareText },
          ].map(({ label, badgeClass, text }) => (
            <div key={label} className="flex flex-col">
              <div className="flex items-center justify-between px-3 py-2 bg-gray-50 border-b border-gray-200">
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${badgeClass}`}>
                  {label}
                </span>
                <CopyButton text={text} />
              </div>
              <pre className="text-xs text-gray-700 p-3 overflow-y-scroll h-64 whitespace-pre-wrap break-words font-mono leading-relaxed">
                {text || '（無文字內容）'}
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
