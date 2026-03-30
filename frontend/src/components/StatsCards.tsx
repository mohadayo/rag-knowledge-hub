import type { DocumentStats } from "@/lib/api";

interface StatsCardsProps {
  stats: DocumentStats;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function StatsCards({ stats }: StatsCardsProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <p className="text-sm text-gray-500">登録文書数</p>
        <p className="text-2xl font-bold text-gray-800">
          {stats.total_documents}
        </p>
      </div>
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <p className="text-sm text-gray-500">総チャンク数</p>
        <p className="text-2xl font-bold text-gray-800">
          {stats.total_chunks}
        </p>
      </div>
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <p className="text-sm text-gray-500">総データ量</p>
        <p className="text-2xl font-bold text-gray-800">
          {formatSize(stats.total_size)}
        </p>
      </div>
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <p className="text-sm text-gray-500">ファイル種別</p>
        <div className="flex flex-wrap gap-1 mt-1">
          {stats.file_type_breakdown.length === 0 ? (
            <span className="text-sm text-gray-400">-</span>
          ) : (
            stats.file_type_breakdown.map((ft) => (
              <span
                key={ft.file_type}
                className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs font-medium uppercase"
              >
                {ft.file_type}: {ft.count}
              </span>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
