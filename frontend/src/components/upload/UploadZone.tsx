import { useRef, useState, DragEvent, ChangeEvent } from 'react'

interface Props {
  label: string
  badgeColor: string
  file: File | null
  onFile: (f: File) => void
}

export default function UploadZone({ label, badgeColor, file, onFile }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  const handleDrop = (e: DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped?.name.toLowerCase().endsWith('.pdf')) {
      onFile(dropped)
    }
  }

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const picked = e.target.files?.[0]
    if (picked) onFile(picked)
  }

  return (
    <div
      className={`flex flex-col items-center justify-center border-2 border-dashed rounded-xl p-6 cursor-pointer transition-colors
        ${dragging ? 'border-blue-400 bg-blue-50' : 'border-gray-300 bg-gray-50 hover:bg-gray-100'}
        ${file ? 'border-green-400 bg-green-50' : ''}
      `}
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        className="hidden"
        onChange={handleChange}
      />
      <span className={`text-xs font-semibold px-2 py-0.5 rounded-full mb-3 ${badgeColor}`}>
        {label}
      </span>
      {file ? (
        <div className="text-center">
          <div className="text-green-600 text-2xl mb-1">✓</div>
          <p className="text-sm font-medium text-gray-800 break-all">{file.name}</p>
          <p className="text-xs text-gray-500 mt-1">{(file.size / 1024).toFixed(0)} KB</p>
          <p className="text-xs text-blue-500 mt-2 underline">點擊更換檔案</p>
        </div>
      ) : (
        <div className="text-center">
          <div className="text-gray-400 text-3xl mb-2">📄</div>
          <p className="text-sm text-gray-600">拖曳 PDF 至此</p>
          <p className="text-xs text-gray-400 mt-1">或點擊選擇檔案</p>
        </div>
      )}
    </div>
  )
}
