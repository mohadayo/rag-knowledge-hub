import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] text-center">
      <h1 className="text-4xl font-bold text-gray-800 mb-4">
        社内ナレッジ検索AI
      </h1>
      <p className="text-lg text-gray-600 mb-8 max-w-xl">
        社内マニュアル・FAQ・議事録・業務手順書などをアップロードして、
        自然文で質問すると根拠付きで回答します。
      </p>
      <div className="flex gap-4">
        <Link
          href="/chat"
          className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          質問する
        </Link>
        <Link
          href="/admin"
          className="px-6 py-3 bg-white text-gray-700 border border-gray-300 rounded-lg font-medium hover:bg-gray-50 transition-colors"
        >
          文書管理
        </Link>
      </div>
      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl">
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100">
          <div className="text-2xl mb-2">1</div>
          <h3 className="font-semibold text-gray-800 mb-1">文書をアップロード</h3>
          <p className="text-sm text-gray-500">
            PDF・CSV・TXT・Markdownに対応
          </p>
        </div>
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100">
          <div className="text-2xl mb-2">2</div>
          <h3 className="font-semibold text-gray-800 mb-1">自然文で質問</h3>
          <p className="text-sm text-gray-500">
            チャット形式で気軽に質問できます
          </p>
        </div>
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100">
          <div className="text-2xl mb-2">3</div>
          <h3 className="font-semibold text-gray-800 mb-1">根拠付き回答</h3>
          <p className="text-sm text-gray-500">
            参照元の文書名と抜粋を表示します
          </p>
        </div>
      </div>
    </div>
  );
}
