"use client";

import { useCallback, useState } from "react";
import { uploadDocument } from "@/lib/api";

interface FileUploadProps {
  onUploadComplete: () => void;
}

export default function FileUpload({ onUploadComplete }: FileUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleFiles = useCallback(
    async (files: FileList | null) => {
      if (!files || files.length === 0) return;
      setError("");
      setSuccess("");
      setUploading(true);

      try {
        for (const file of Array.from(files)) {
          await uploadDocument(file);
        }
        setSuccess(
          `${files.length}件のファイルをアップロードしました`
        );
        onUploadComplete();
      } catch (e) {
        setError(e instanceof Error ? e.message : "アップロードに失敗しました");
      } finally {
        setUploading(false);
      }
    },
    [onUploadComplete]
  );

  return (
    <div className="mb-6">
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${
          dragOver
            ? "border-blue-500 bg-blue-50"
            : "border-gray-300 hover:border-gray-400"
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          handleFiles(e.dataTransfer.files);
        }}
        onClick={() => {
          const input = document.createElement("input");
          input.type = "file";
          input.multiple = true;
          input.accept = ".pdf,.csv,.txt,.md,.markdown";
          input.onchange = () => handleFiles(input.files);
          input.click();
        }}
      >
        {uploading ? (
          <p className="text-gray-500 animate-pulse">アップロード中...</p>
        ) : (
          <>
            <p className="text-gray-600 font-medium">
              ファイルをドラッグ＆ドロップ、またはクリックして選択
            </p>
            <p className="text-sm text-gray-400 mt-1">
              対応形式: PDF, CSV, TXT, Markdown
            </p>
          </>
        )}
      </div>
      {error && (
        <p className="mt-2 text-sm text-red-600">{error}</p>
      )}
      {success && (
        <p className="mt-2 text-sm text-green-600">{success}</p>
      )}
    </div>
  );
}
