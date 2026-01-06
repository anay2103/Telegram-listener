from typing import NotRequired, TypedDict

from chromadb import GetResult
from chromadb.api.types import Document, Embedding, Metadata


class ChromaResult(TypedDict):
    id: str
    embeddings: NotRequired[Embedding]
    document: NotRequired[Document]
    metadatas: NotRequired[Metadata]


class GetResultProxy(TypedDict):
    ids: list[str]
    embeddings: NotRequired[list[Embedding]]
    documents: list[Document]
    metadatas: list[Metadata]


def convert_from_get_result(result: GetResult) -> list[ChromaResult]:
    return [
        ChromaResult(id=id_, document=doc, metadatas=meta)
        for id_, doc, meta in zip(result['ids'], result['documents'], result['metadatas'])
    ]


def convert_to_get_result(result: list[ChromaResult]) -> GetResultProxy:
    ids, documents, metadatas = [], [], []
    for r in result:
        ids.append(r['id'])
        documents.append(r['document'])
        metadatas.append(r['metadatas'])
    return GetResultProxy(ids=ids, documents=documents, metadatas=metadatas)
