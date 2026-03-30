import ReactMarkdown from "react-markdown";
import type { ChatResponse } from "@/lib/api";
import SourceCard from "./SourceCard";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  response?: ChatResponse;
}

const confidenceLabel: Record<string, { text: string; color: string }> = {
  high: { text: "信頼度: 高", color: "bg-green-100 text-green-700" },
  medium: { text: "信頼度: 中", color: "bg-yellow-100 text-yellow-700" },
  low: { text: "信頼度: 低", color: "bg-red-100 text-red-700" },
  unknown: { text: "根拠不十分", color: "bg-gray-100 text-gray-600" },
};

export default function ChatMessage({
  role,
  content,
  response,
}: ChatMessageProps) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-3 ${
          isUser
            ? "bg-blue-600 text-white"
            : "bg-white border border-gray-200 text-gray-800"
        }`}
      >
        {isUser ? (
          <p>{content}</p>
        ) : (
          <div>
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown>{content}</ReactMarkdown>
            </div>

            {response && response.confidence && (
              <span
                className={`inline-block mt-2 px-2 py-0.5 rounded text-xs font-medium ${
                  confidenceLabel[response.confidence]?.color ?? "bg-gray-100 text-gray-600"
                }`}
              >
                {confidenceLabel[response.confidence]?.text ?? response.confidence}
              </span>
            )}

            {response && response.sources.length > 0 && (
              <div className="mt-4 space-y-2">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  参照ソース
                </p>
                {response.sources.map((source, i) => (
                  <SourceCard key={i} source={source} index={i} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
