interface SuggestedQuestionsProps {
  onSelect: (question: string) => void;
}

const SUGGESTIONS = [
  "有給休暇の申請方法を教えてください",
  "リモートワークのルールは？",
  "経費精算の手順を教えてください",
  "パスワードを忘れた場合はどうすればいい？",
  "VPN接続ができないときの対処法は？",
  "通勤手当の上限はいくらですか？",
];

export default function SuggestedQuestions({
  onSelect,
}: SuggestedQuestionsProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-6">
      <div className="text-center">
        <p className="text-gray-400 mb-1">
          質問を入力すると、社内文書から根拠付きで回答します
        </p>
        <p className="text-sm text-gray-300">
          または以下のサンプル質問をお試しください
        </p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-lg w-full">
        {SUGGESTIONS.map((q) => (
          <button
            key={q}
            onClick={() => onSelect(q)}
            className="text-left px-3 py-2 text-sm text-gray-600 bg-gray-50 border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 hover:text-blue-700 transition-colors"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
