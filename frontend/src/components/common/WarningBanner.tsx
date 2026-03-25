interface Props {
  message: string
}

export default function WarningBanner({ message }: Props) {
  return (
    <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-3 flex items-start gap-2">
      <span className="text-yellow-500">⚠</span>
      <p className="text-yellow-700 text-sm">{message}</p>
    </div>
  )
}
