from langchain.docstore.document import Document
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings import OpenAIEmbeddings
import datetime, os, json
from collections import defaultdict

class LongTermMemory:
    def __init__(self, store_path="rag_vector_store"):
        self.store_path = store_path
        self.embedding_model = OpenAIEmbeddings()
        self.keyword_strength = defaultdict(int)

        if os.path.exists(store_path):
            self.vector_store = FAISS.load_local(store_path, self.embedding_model)
            self._load_keyword_strength()
        else:
            self.vector_store = FAISS.from_documents([], self.embedding_model)
            self._save_keyword_strength()
            self.vector_store.save_local(store_path)

    def _to_document(self, node_type, description, created, keywords=None,
                     importance=0.5, freshness=1.0, time_id=None, moccupying=1):
        keywords = keywords or []
        for kw in keywords:
            self.keyword_strength[kw] += 1

        metadata = {
            "type": node_type,
            "created": created.strftime("%Y-%m-%d %H:%M:%S"),
            "importance": importance,
            "freshness": freshness,
            "keywords": keywords,
            "time_id": time_id,
            "moccupying": moccupying
        }
        return Document(page_content=description, metadata=metadata)

    def _save_keyword_strength(self):
        path = os.path.join(self.store_path, "keyword_strength.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.keyword_strength, f, ensure_ascii=False, indent=2)

    def _load_keyword_strength(self):
        path = os.path.join(self.store_path, "keyword_strength.json")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                self.keyword_strength = defaultdict(int, json.load(f))

    def add_event(self, created, description, keywords=None, importance=0.5, freshness=1.0, time_id=None, moccupying=1):
        doc = self._to_document("event", description, created, keywords, importance, freshness, time_id, moccupying)
        self.vector_store.add_documents([doc])
        self.vector_store.save_local(self.store_path)
        self._save_keyword_strength()

    def add_thought(self, created, description, keywords=None, importance=0.5, freshness=1.0, time_id=None, moccupying=1):
        doc = self._to_document("thought", description, created, keywords, importance, freshness, time_id, moccupying)
        self.vector_store.add_documents([doc])
        self.vector_store.save_local(self.store_path)
        self._save_keyword_strength()

    def add_chat(self, created, description, keywords=None, importance=0.5, freshness=1.0, time_id=None, moccupying=1):
        doc = self._to_document("chat", description, created, keywords, importance, freshness, time_id, moccupying)
        self.vector_store.add_documents([doc])
        self.vector_store.save_local(self.store_path)
        self._save_keyword_strength()

    def update_all_freshness(self, current_time=None, decay_rate=0.95):
        docs = self.vector_store.similarity_search("all", k=1000)
        updated_docs = []
        for doc in docs:
            freshness = doc.metadata.get("freshness", 1.0)
            freshness *= decay_rate
            doc.metadata["freshness"] = max(0.0, freshness)
            updated_docs.append(doc)

        self.vector_store = FAISS.from_documents(updated_docs, self.embedding_model)
        self.vector_store.save_local(self.store_path)

    def retrieve_relevant_thoughts(self, *args):
        return self._filter_by_type("thought", *args)

    def retrieve_relevant_events(self, *args):
        return self._filter_by_type("event", *args)

    def _filter_by_type(self, node_type, *args):
        keywords = [x.lower() for x in args if x]
        query = " ".join(keywords)
        results = self.vector_store.similarity_search(query, k=50)
        return [doc for doc in results if doc.metadata.get("type") == node_type]

    def retrieve_nodes_by_keywords(self, query_keywords, top_k=10, importance_threshold=0.5, freshness_threshold=0.5):
        if not isinstance(query_keywords, list):
            query_keywords = [query_keywords]
        query = " ".join(query_keywords)
        results = self.vector_store.similarity_search(query, k=100)
        filtered = [doc for doc in results if doc.metadata.get("freshness", 0) >= freshness_threshold and doc.metadata.get("importance", 0) >= importance_threshold]
        return filtered[:top_k]

    def get_summarized_latest_events(self, retention):
        all_docs = self.vector_store.similarity_search("all", k=1000)
        events = [
            doc for doc in all_docs
            if doc.metadata.get("type") == "event" and "created" in doc.metadata
        ]
        # 转换为 datetime 排序
        events.sort(
            key=lambda d: datetime.datetime.strptime(d.metadata["created"], "%Y-%m-%d %H:%M:%S"),
            reverse=True
        )
        return set([doc.page_content for doc in events[:retention]])


    def dump_all_documents(self):
        return self.vector_store.similarity_search("all", k=1000)

    def clear_memory(self):
        self.vector_store = FAISS.from_documents([], self.embedding_model)
        self.vector_store.save_local(self.store_path)
        self.keyword_strength = defaultdict(int)
        self._save_keyword_strength()
