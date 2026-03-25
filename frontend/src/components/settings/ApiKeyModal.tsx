import { useEffect, useState } from 'react'
import { getApiKeyStatus, saveApiKey, deleteApiKey } from '../../services/api'

interface Props {
  onClose: () => void
}

export default function ApiKeyModal({ onClose }: Props) {
  const [configured, setConfigured] = useState(false)
  const [preview, setPreview] = useState('')
  const [inputKey, setInputKey] = useState('')
  const [showInput, setShowInput] = useState(false)
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    getApiKeyStatus().then(({ configured, preview }) => {
      setConfigured(configured)
      setPreview(preview)
    })
  }, [])

  async function handleSave() {
    if (!inputKey.trim()) return
    setLoading(true)
    try {
      const res = await saveApiKey(inputKey.trim())
      setMessage(res.message)
      if (res.success) {
        setConfigured(true)
        setPreview(inputKey.trim().slice(0, 8) + '...' + inputKey.trim().slice(-4))
        setInputKey('')
        setShowInput(false)
      }
    } catch {
      setMessage('儲存失敗，請再試一次')
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete() {
    setLoading(true)
    try {
      const res = await deleteApiKey()
      setMessage(res.message)
      if (res.success) {
        setConfigured(false)
        setPreview('')
      }
    } catch {
      setMessage('移除失敗，請再試一次')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md mx-4 p-6" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold text-gray-800">Anthropic API Key 設定</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">✕</button>
        </div>

        <div className="mb-4 p-3 rounded-lg bg-gray-50 flex items-center gap-3">
          <span className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${configured ? 'bg-green-500' : 'bg-gray-300'}`} />
          <div>
            <p className="text-sm font-medium text-gray-700">
              {configured ? 'API Key 已設定' : '尚未設定 API Key'}
            </p>
            {configured && preview && (
              <p className="text-xs text-gray-400 font-mono mt-0.5">{preview}</p>
            )}
            {!configured && (
              <p className="text-xs text-gray-400 mt-0.5">設定後將使用 Claude AI 分析報告，準確度更高</p>
            )}
          </div>
        </div>

        {!showInput ? (
          <div className="flex gap-2">
            <button
              onClick={() => { setShowInput(true); setMessage('') }}
              className="flex-1 py-2 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors"
            >
              {configured ? '更換 API Key' : '輸入 API Key'}
            </button>
            {configured && (
              <button
                onClick={handleDelete}
                disabled={loading}
                className="py-2 px-4 rounded-lg border border-red-200 text-red-600 hover:bg-red-50 text-sm font-medium transition-colors disabled:opacity-50"
              >
                移除
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            <input
              type="password"
              value={inputKey}
              onChange={e => setInputKey(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSave()}
              placeholder="sk-ant-api03-..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
              autoFocus
            />
            <div className="flex gap-2">
              <button
                onClick={handleSave}
                disabled={loading || !inputKey.trim()}
                className="flex-1 py-2 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors disabled:opacity-50"
              >
                {loading ? '儲存中...' : '儲存'}
              </button>
              <button
                onClick={() => { setShowInput(false); setInputKey(''); setMessage('') }}
                className="py-2 px-4 rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 text-sm font-medium transition-colors"
              >
                取消
              </button>
            </div>
          </div>
        )}

        {message && (
          <p className="mt-3 text-sm text-center text-gray-500">{message}</p>
        )}

        <p className="mt-4 text-xs text-gray-400 text-center">
          Key 儲存於本機 .env 檔案，不會上傳至任何伺服器
        </p>
      </div>
    </div>
  )
}
