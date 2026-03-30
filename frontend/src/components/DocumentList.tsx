"use client";

import { deleteDocument, type DocumentInfo } from "@/lib/api";
import { useState } from "react";

interface DocumentListProps {
  documents: DocumentInfo[];
  onDelete: () => void;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString("ja-JP", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

const statusLabel: Record<string, { text: string; color: string }> = {
  ready: { text: "完了", color: "bg-green-100 text-green-700" },
  processing: { text: "処理中", color: "bg-yellow-100 text-yellow-700" },
  error: { text: "エラー", color: "bg-red-100 text-red-700" },
};

export default function DocumentList({ documents, onDelete }: DocumentListProps) {
  const [deleting, setDeleting] = useState<number | null>(null);

  const handleDelete = async (id: number) => {
    if (!confirm("この文書を削除しますか？")) return;
    setDeleting(id);
    try {
      await deleteDocument(id);
      onDelete();
    } catch {
      alert("削除に失敗しました");
    } finally {
      setDeleting(null);
    }
  };

  if (documents.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        <p>登録された文書はまだありません</p>
        <p className="text-sm mt-1">上のエリアからファイルをアップロードしてください</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 text-left text-gray-500">
            <th className="py-3 px-2">ファイル名</th>
            <th className="py-3 px-2">形式</th>
            <th className="py-3 px-2">サイズ</th>
            <th className="py-3 px-2">チャンク数</th>
            <th className="py-3 px-2">ステータス</th>
            <th className="py-3 px-2">登録日時</th>
            <th className="py-3 px-2"></th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => {
            const status = statusLabel[doc.status] ?? statusLabel.error;
            return (
              <tr key={doc.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="py-3 px-2 font-medium text-gray-800">
                  {doc.filename}
                </td>
                <td className="py-3 px-2 text-gray-500 uppercase">
                  {doc.file_type}
                </td>
                <td className="py-3 px-2 text-gray-500">
                  {formatFileSize(doc.file_size)}
                </td>
                <td className="py-3 px-2 text-gray-500">{doc.chunk_count}</td>
                <td className="py-3 px-2">
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-medium ${status.color}`}
                  >
                    {status.text}
                  </span>
                </td>
                <td className="py-3 px-2 text-gray-500">
                  {formatDate(doc.uploaded_at)}
                </td>
                <td className="py-3 px-2">
                  <button
                    onClick={() => handleDelete(doc.id)}
                    disabled={deleting === doc.id}
                    className="text-red-500 hover:text-red-700 text-xs font-medium disabled:opacity-50"
                  >
                    {deleting === doc.id ? "削除中..." : "削除"}
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
