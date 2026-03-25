interface Props {
  message?: string
}

export default function LoadingSpinner({ message = '處理中...' }: Props) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-20">
      <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
      <p className="text-gray-600 text-sm">{message}</p>
    </div>
  )
}
