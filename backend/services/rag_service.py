import logging

from openai import OpenAI

from config import settings
from schemas import ChatResponse, SourceInfo
from services.embedding_service import generate_embedding
from services.vector_store import search

logger = logging.getLogger(__name__)

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


SYSTEM_PROMPT = """あなたは社内ナレッジ検索AIアシスタントです。
以下のルールに従って回答してください：

1. 提供されたコンテキスト（社内文書の抜粋）のみを根拠に回答すること
2. コンテキストに含まれない情報で推測・創作しないこと
3. 根拠が不十分な場合は「提供された文書からは十分な情報が見つかりませんでした」と正直に回答すること
4. 回答は日本語で、簡潔かつ分かりやすく記述すること
5. 箇条書きや見出しを適切に使い、読みやすくすること"""


def ask(question: str) -> ChatResponse:
    """RAGパイプラインで質問に回答する"""
    logger.info("RAGパイプライン開始: question_length=%d", len(question))

    # 1. 質問をEmbeddingに変換
    query_embedding = generate_embedding(question)
    logger.info("クエリEmbedding生成完了")

    # 2. ベクトル検索
    results = search(query_embedding, n_results=settings.max_retrieval_results)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    # 3. 類似度フィルタ (cosine distanceなので小さいほど類似)
    threshold = settings.similarity_threshold
    filtered = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        similarity = 1 - dist  # cosine distance → similarity
        if similarity >= threshold:
            filtered.append((doc, meta, similarity))

    logger.info(
        "類似度フィルタ: threshold=%.2f, 候補=%d件, フィルタ後=%d件",
        threshold, len(documents), len(filtered),
    )

    # 根拠が見つからない場合
    if not filtered:
        logger.info("根拠なし: 文書が見つかりませんでした")
        return ChatResponse(
            answer="申し訳ありませんが、登録された文書からはご質問に関する十分な情報が見つかりませんでした。質問を変えてお試しいただくか、関連する文書が登録されているかご確認ください。",
            sources=[],
            confidence="unknown",
        )

    # 4. コンテキスト構築
    context_parts = []
    sources: list[SourceInfo] = []
    for i, (doc, meta, sim) in enumerate(filtered):
        context_parts.append(f"[文書{i + 1}: {meta['filename']}]\n{doc}")
        sources.append(
            SourceInfo(
                filename=meta["filename"],
                excerpt=doc[:200] + ("..." if len(doc) > 200 else ""),
                score=round(sim, 3),
            )
        )

    context = "\n\n---\n\n".join(context_parts)
    logger.info("コンテキスト構築完了: %d件の参照文書", len(sources))

    # 5. LLMで回答生成
    client = _get_client()
    logger.info("LLM回答生成開始: model=%s", settings.openai_chat_model)
    response = client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"## 参照コンテキスト\n{context}\n\n## 質問\n{question}",
            },
        ],
        temperature=0.1,
        max_tokens=1024,
    )

    answer = response.choices[0].message.content or ""
    logger.info(
        "LLM回答生成完了: answer_length=%d, usage=%s",
        len(answer), response.usage,
    )

    # 6. 信頼度判定
    avg_similarity = sum(s.score for s in sources) / len(sources)
    if avg_similarity >= 0.7:
        confidence = "high"
    elif avg_similarity >= 0.5:
        confidence = "medium"
    else:
        confidence = "low"

    logger.info("RAGパイプライン完了: confidence=%s, avg_similarity=%.3f", confidence, avg_similarity)
    return ChatResponse(answer=answer, sources=sources, confidence=confidence)
