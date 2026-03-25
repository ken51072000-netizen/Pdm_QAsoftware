interface Props {
  message: string
  onRetry?: () => void
}

export default function ErrorBanner({ message, onRetry }: Props) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4 flex items-start gap-3">
      <span className="text-red-500 text-xl">⚠️</span>
      <div className="flex-1">
        <p className="text-red-700 text-sm font-medium">發生錯誤</p>
        <p className="text-red-600 text-sm mt-1">{message}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-sm text-red-600 underline hover:text-red-800"
        >
          重試
        </button>
      )}
    </div>
  )
}
