"""온톨로지 문서를 Chroma 에 인덱싱.

프로젝트 1의 셀 8과 같은 일입니다. 두 가지 교훈을 그대로 적용하세요.
    - ids 를 명시해 멱등하게 (재실행해도 중복 안 쌓이게)
    - 문서 형식을 바꾸면 컬렉션 이름도 바꾸기 (stale index 방지)

실행:
    ..\\.venv\\Scripts\\python.exe -m src.retrieval.index
"""

from __future__ import annotations

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings

from src.config import (
    CHROMA_COLLECTION,
    CHROMA_DIR,
    EMBEDDING_MODEL,
    OLLAMA_BASE_URL,
)
from src.ontology.compiler import to_documents
from src.ontology.loader import load_ontology


def get_embeddings() -> OllamaEmbeddings:
    return OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)


def get_vectorstore() -> Chroma:
    """기존 컬렉션에 '연결만' 한다. 인덱싱은 build_index() 가 담당."""
    # TODO 1:
    #   return Chroma(
    #       collection_name=CHROMA_COLLECTION,
    #       embedding_function=get_embeddings(),
    #       persist_directory=CHROMA_DIR,
    #   )
    #   주의: 생성자 파라미터는 embedding 이 아니라 embedding_function 입니다.
    raise NotImplementedError


def build_index(force: bool = False) -> Chroma:
    """온톨로지를 읽어 벡터 스토어를 채운다.

    TODO 2:
      onto = load_ontology()
      docs = to_documents(onto)

      vs = get_vectorstore()
      if force:
          vs.reset_collection()

      vs.add_documents(
          [Document(page_content=d["text"],
                    metadata={"kind": d["kind"], "name": d["name"]}) for d in docs],
          ids=[d["id"] for d in docs],      # <- 멱등성의 핵심
      )
      return vs

    metadata 에 kind 를 넣는 이유:
      검색할 때 "지표만 5개", "엔티티만 3개" 처럼 종류별로 뽑고 싶기 때문입니다.
      한 덩어리로 top-k 를 뽑으면 지표 문서가 엔티티 문서에 밀려 안 나옵니다.
      이걸 metadata 필터라고 하고, search.py 에서 씁니다.
    """
    raise NotImplementedError


if __name__ == "__main__":
    vs = build_index(force=True)
    print("인덱싱 완료:", vs._collection.count(), "개 문서")
