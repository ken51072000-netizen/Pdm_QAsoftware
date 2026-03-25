import UploadPanel from './components/upload/UploadPanel'
import ComparisonView from './components/comparison/ComparisonView'
import LoadingSpinner from './components/common/LoadingSpinner'
import ErrorBanner from './components/common/ErrorBanner'
import { useUpload } from './hooks/useUpload'

export default function App() {
  const { phase, error, result, uploadAndCompare, reset } = useUpload()

  const isLoading = phase === 'uploading' || phase === 'analyzing'
  const loadingMessage =
    phase === 'uploading' ? '正在上傳 PDF 檔案...' :
    phase === 'analyzing' ? '正在使用 AI 分析報告內容，請稍候（約 10-20 秒）...' :
    '處理中...'

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center gap-3">
          <span className="text-xl">📊</span>
          <span className="font-bold text-gray-800">設備頻譜分析報告比對系統</span>
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
    </div>
  )
}
