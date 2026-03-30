const API_BASE = "/api";

export interface DocumentInfo {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  chunk_count: number;
  status: string;
  uploaded_at: string;
}

export interface SourceInfo {
  filename: string;
  excerpt: string;
  score: number;
}

export interface ChatResponse {
  answer: string;
  sources: SourceInfo[];
  confidence: string;
}

export async function uploadDocument(file: File): Promise<DocumentInfo> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "アップロードに失敗しました");
  }
  return res.json();
}

export async function listDocuments(): Promise<DocumentInfo[]> {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error("文書一覧の取得に失敗しました");
  return res.json();
}

export async function deleteDocument(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/documents/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("削除に失敗しました");
}

export async function sendChat(question: string): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error("回答の取得に失敗しました");
  return res.json();
}
