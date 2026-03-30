import type { SourceInfo } from "@/lib/api";

interface SourceCardProps {
  source: SourceInfo;
  index: number;
}

export default function SourceCard({ source, index }: SourceCardProps) {
  const scorePercent = Math.round(source.score * 100);
  const scoreColor =
    scorePercent >= 70
      ? "text-green-600"
      : scorePercent >= 50
        ? "text-yellow-600"
        : "text-red-500";

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-700">
          [{index + 1}] {source.filename}
        </span>
        <span className={`text-xs font-medium ${scoreColor}`}>
          関連度: {scorePercent}%
        </span>
      </div>
      <p className="text-sm text-gray-600 leading-relaxed">{source.excerpt}</p>
    </div>
  );
}
