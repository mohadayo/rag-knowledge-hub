"use client";

import { useCallback, useEffect, useState } from "react";
import FileUpload from "@/components/FileUpload";
import DocumentList from "@/components/DocumentList";
import StatsCards from "@/components/StatsCards";
import {
  listDocuments,
  fetchDocumentStats,
  type DocumentInfo,
  type DocumentStats,
} from "@/lib/api";

export default function AdminPage() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [stats, setStats] = useState<DocumentStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchAll = useCallback(async () => {
    try {
      const [docs, s] = await Promise.all([
        listDocuments(),
        fetchDocumentStats(),
      ]);
      setDocuments(docs);
      setStats(s);
    } catch {
      console.error("データの取得に失敗しました");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-6">文書管理</h1>

      {stats && <StatsCards stats={stats} />}

      <FileUpload onUploadComplete={fetchAll} />

      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">
          登録済み文書一覧
          <span className="text-sm font-normal text-gray-400 ml-2">
            ({documents.length}件)
          </span>
        </h2>
        {loading ? (
          <p className="text-center py-8 text-gray-400 animate-pulse">
            読み込み中...
          </p>
        ) : (
          <DocumentList documents={documents} onDelete={fetchAll} />
        )}
      </div>
    </div>
  );
}
