import { useState } from 'react'
import UploadZone from './UploadZone'

interface Props {
  onCompare: (consultant: File, software: File) => void
  loading: boolean
}

export default function UploadPanel({ onCompare, loading }: Props) {
  const [consultantFile, setConsultantFile] = useState<File | null>(null)
  const [softwareFile, setSoftwareFile] = useState<File | null>(null)

  const canCompare = consultantFile !== null && softwareFile !== null && !loading

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">設備頻譜分析報告比對系統</h1>
        <p className="text-gray-500 text-sm">
          分別上傳人工顧問與軟體系統所產出的 PDF 報告，系統將自動比對
          <span className="font-medium text-gray-700">設備閾值/健康度、診斷說明、改善建議</span>
          三個欄位的差異。
        </p>
      </div>

      <div className="grid grid-cols-2 gap-6 mb-6">
        <div>
          <p className="text-sm font-medium text-gray-600 mb-2">人工顧問報告</p>
          <UploadZone
            label="人工顧問"
            badgeColor="bg-blue-100 text-blue-700"
            file={consultantFile}
            onFile={setConsultantFile}
          />
        </div>
        <div>
          <p className="text-sm font-medium text-gray-600 mb-2">軟體系統報告</p>
          <UploadZone
            label="軟體系統"
            badgeColor="bg-green-100 text-green-700"
            file={softwareFile}
            onFile={setSoftwareFile}
          />
        </div>
      </div>

      <div className="flex justify-center">
        <button
          disabled={!canCompare}
          onClick={() => consultantFile && softwareFile && onCompare(consultantFile, softwareFile)}
          className={`px-8 py-3 rounded-lg font-semibold text-white transition-colors
            ${canCompare
              ? 'bg-blue-600 hover:bg-blue-700 cursor-pointer'
              : 'bg-gray-300 cursor-not-allowed'
            }`}
        >
          {loading ? '分析中...' : '開始比對'}
        </button>
      </div>

      {!consultantFile || !softwareFile ? (
        <p className="text-center text-xs text-gray-400 mt-3">請上傳兩份 PDF 後才可開始比對</p>
      ) : null}
    </div>
  )
}
