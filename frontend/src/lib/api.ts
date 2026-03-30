const API_BASE = "/api";
const DEFAULT_TIMEOUT_MS = 30_000;
const CHAT_TIMEOUT_MS = 60_000;

function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeoutMs: number = DEFAULT_TIMEOUT_MS,
): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  return fetch(url, { ...options, signal: controller.signal }).finally(() =>
    clearTimeout(id),
  );
}

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
  const res = await fetchWithTimeout(`${API_BASE}/documents/upload`, {
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
  const res = await fetchWithTimeout(`${API_BASE}/documents`);
  if (!res.ok) throw new Error("文書一覧の取得に失敗しました");
  return res.json();
}

export async function deleteDocument(id: number): Promise<void> {
  const res = await fetchWithTimeout(`${API_BASE}/documents/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("削除に失敗しました");
}

export interface FileTypeCount {
  file_type: string;
  count: number;
}

export interface DocumentStats {
  total_documents: number;
  total_chunks: number;
  total_size: number;
  file_type_breakdown: FileTypeCount[];
}

export async function fetchDocumentStats(): Promise<DocumentStats> {
  const res = await fetchWithTimeout(`${API_BASE}/documents/stats`);
  if (!res.ok) throw new Error("統計情報の取得に失敗しました");
  return res.json();
}

export async function sendChat(question: string): Promise<ChatResponse> {
  const res = await fetchWithTimeout(
    `${API_BASE}/chat`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    },
    CHAT_TIMEOUT_MS,
  );
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(err?.detail || "回答の取得に失敗しました");
  }
  return res.json();
}
