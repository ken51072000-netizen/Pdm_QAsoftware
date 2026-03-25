import { useState } from 'react'
import UploadPanel from './components/upload/UploadPanel'
import ComparisonView from './components/comparison/ComparisonView'
import LoadingSpinner from './components/common/LoadingSpinner'
import ErrorBanner from './components/common/ErrorBanner'
import ApiKeyModal from './components/settings/ApiKeyModal'
import { useUpload } from './hooks/useUpload'

export default function App() {
  const { phase, error, result, uploadAndCompare, reset } = useUpload()
  const [showSettings, setShowSettings] = useState(false)

  const isLoading = phase === 'uploading' || phase === 'analyzing'
  const loadingMessage =
    phase === 'uploading' ? '正在上傳 PDF 檔案...' :
    phase === 'analyzing' ? '正在使用 AI 分析報告內容，請稍候（約 10-20 秒）...' :
    '處理中...'

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xl">📊</span>
            <span className="font-bold text-gray-800">設備頻譜分析報告比對系統</span>
          </div>
          <button
            onClick={() => setShowSettings(true)}
            title="API Key 設定"
            className="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
          >
            ⚙️
          </button>
        </div>
      </header>

      <main className="px-6 py-8">
        {phase === 'error' && error && (
          <div className="max-w-3xl mx-auto mb-6">
            <ErrorBanner message={error} onRetry={reset} />
          </div>
        )}

        {(phase === 'idle' || phase === 'error') && (
          <UploadPanel onCompare={uploadAndCompare} loading={false} />
        )}

        {isLoading && (
          <LoadingSpinner message={loadingMessage} />
        )}

        {phase === 'done' && result && (
          <ComparisonView result={result} onReset={reset} />
        )}
      </main>

      {showSettings && <ApiKeyModal onClose={() => setShowSettings(false)} />}
    </div>
  )
}
