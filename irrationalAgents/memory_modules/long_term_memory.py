import json
import datetime
import math
from functools import lru_cache
class TimeNode:
    def __init__(self, time_id, timestamp):
        self.time_id = time_id
        self.timestamp = timestamp


class ConceptNode: 
    def __init__(self,
                 node_id, node_count, type_count, node_type, depth,
                 created, 
                 description, 
                 keywords,
                 importance=0.0, freshness=1.0, time_id=None): 
        self.node_id = node_id
        self.node_count = node_count
        self.type_count = type_count
        self.type = node_type # thought / event / chat
        self.depth = depth

        self.created = created
        self.last_accessed = self.created

        self.description = description
        self.keywords = keywords

        self.importance = importance
        self.freshness = freshness
        self.time_id = time_id

    def update_freshness(self, current_time):
        """
        経過時間に応じてfreshnessを減衰させる
        """
        time_diff = (current_time - self.last_accessed).total_seconds() / 3600.0
        decay_factor = 0.95 ** time_diff
        self.freshness = max(0.0, self.freshness * decay_factor)

    def accessed(self, current_time):
        """
        ノード参照時freshnessリフレッシュ
        """
        self.last_accessed = current_time
        self.freshness = min(1.0, self.freshness + 0.2)


class LongTermMemory: 
    def __init__(self, long_memory_path): 
        self.id_to_node = dict()

        self.seq_event = []
        self.seq_thought = []
        self.seq_chat = []

        self.kw_to_event = dict()
        self.kw_to_thought = dict()
        self.kw_to_chat = dict()

        self.kw_strength_event = dict()
        self.kw_strength_thought = dict()

        # TimeNode管理辞書
        self.time_nodes = dict()

        nodes_load = json.load(open(long_memory_path + "/nodes.json"))

        for count in range(len(nodes_load.keys())): 
            node_id = f"node_{str(count+1)}"
            node_details = nodes_load[node_id]

            node_count = node_details["node_count"]
            type_count = node_details["type_count"]
            node_type = node_details["type"]
            depth = node_details["depth"]

            created = datetime.datetime.strptime(node_details["created"], '%Y-%m-%d %H:%M:%S')

            description = node_details["description"]
            keywords = set(node_details["keywords"])

            importance = node_details.get("importance", 0.0)
            freshness = node_details.get("freshness", 1.0)
            time_id = node_details.get("time_id", None)
            timestamp = node_details.get("timestamp", None)
            if timestamp:
                timestamp_dt = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                if time_id is None:
                    time_id = f"time_{node_id}"
                self.time_nodes[time_id] = TimeNode(time_id, timestamp_dt)

            if node_type == "event": 
                self.add_event(created, description, keywords, importance=importance, freshness=freshness, time_id=time_id)
            elif node_type == "chat": 
                self.add_chat(created, description, keywords, importance=importance, freshness=freshness, time_id=time_id)
            elif node_type == "thought": 
                self.add_thought(created, description, keywords, importance=importance, freshness=freshness, time_id=time_id)

        kw_strength_load = json.load(open(long_memory_path + "/kw_strength.json"))
        if kw_strength_load["kw_strength_event"]: 
            self.kw_strength_event = kw_strength_load["kw_strength_event"]
        if kw_strength_load["kw_strength_thought"]: 
            self.kw_strength_thought = kw_strength_load["kw_strength_thought"]

    def save(self, out_json): 
        r = dict()
        for count in range(len(self.id_to_node.keys()), 0, -1): 
            node_id = f"node_{str(count)}"
            node = self.id_to_node[node_id]

            r[node_id] = dict()
            r[node_id]["node_count"] = node.node_count
            r[node_id]["type_count"] = node.type_count
            r[node_id]["type"] = node.type
            r[node_id]["depth"] = node.depth
            r[node_id]["created"] = node.created.strftime('%Y-%m-%d %H:%M:%S')

            r[node_id]["description"] = node.description
            r[node_id]["keywords"] = list(node.keywords)

            r[node_id]["importance"] = node.importance
            r[node_id]["freshness"] = node.freshness
            r[node_id]["time_id"] = node.time_id

            if node.time_id and node.time_id in self.time_nodes:
                time_node = self.time_nodes[node.time_id]
                r[node_id]["timestamp"] = time_node.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            else:
                r[node_id]["timestamp"] = None

        with open(out_json+"/nodes.json", "w") as outfile:
            json.dump(r, outfile)

        r = dict()
        r["kw_strength_event"] = self.kw_strength_event
        r["kw_strength_thought"] = self.kw_strength_thought
        with open(out_json+"/kw_strength.json", "w") as outfile:
            json.dump(r, outfile)


    def add_event(self, created, description, keywords, importance=0.0, freshness=1.0, time_id=None):
        node_count = len(self.id_to_node.keys()) + 1
        type_count = len(self.seq_event) + 1
        node_type = "event"
        node_id = f"node_{str(node_count)}"
        depth = 0

        node = ConceptNode(node_id, node_count, type_count, node_type, depth,
                           created, description, keywords,
                           importance=importance, freshness=freshness, time_id=time_id)

        self.seq_event.insert(0, node)
        kw_lower = [i.lower() for i in keywords]
        for kw in kw_lower: 
            if kw in self.kw_to_event: 
                self.kw_to_event[kw].insert(0, node)
            else: 
                self.kw_to_event[kw] = [node]
        self.id_to_node[node_id] = node 

        for kw in kw_lower: 
            if kw in self.kw_strength_event: 
                self.kw_strength_event[kw] += 1
            else: 
                self.kw_strength_event[kw] = 1

        return node

    def add_thought(self, created, description, keywords, importance=0.0, freshness=1.0, time_id=None):
        node_count = len(self.id_to_node.keys()) + 1
        type_count = len(self.seq_thought) + 1
        node_type = "thought"
        node_id = f"node_{str(node_count)}"
        depth = 1

        node = ConceptNode(node_id, node_count, type_count, node_type, depth,
                           created, description, keywords,
                           importance=importance, freshness=freshness, time_id=time_id)

        self.seq_thought.insert(0, node)
        kw_lower = [i.lower() for i in keywords]
        for kw in kw_lower: 
            if kw in self.kw_to_thought: 
                self.kw_to_thought[kw].insert(0, node)
            else: 
                self.kw_to_thought[kw] = [node]
        self.id_to_node[node_id] = node 

        for kw in kw_lower: 
            if kw in self.kw_strength_thought: 
                self.kw_strength_thought[kw] += 1
            else: 
                self.kw_strength_thought[kw] = 1

        return node

    def add_chat(self, created, description, keywords, importance=0.0, freshness=1.0, time_id=None): 
        node_count = len(self.id_to_node.keys()) + 1
        type_count = len(self.seq_chat) + 1
        node_type = "chat"
        node_id = f"node_{str(node_count)}"
        depth = 0

        node = ConceptNode(node_id, node_count, type_count, node_type, depth,
                           created, description, keywords,
                           importance=importance, freshness=freshness, time_id=time_id)

        self.seq_chat.insert(0, node)
        kw_lower = [i.lower() for i in keywords]
        for kw in kw_lower: 
            if kw in self.kw_to_chat: 
                self.kw_to_chat[kw].insert(0, node)
            else: 
                self.kw_to_chat[kw] = [node]
        self.id_to_node[node_id] = node 

        return node

    def get_summarized_latest_events(self, retention): 
        ret_set = set()
        # SPO削除したため、説明テキストなどを用いる場合は適宜修正
        # ここではdescriptionをまとめることにするか、あるいはそのままret_setに入れないか検討
        # もともとspo_summaryしていたがS,P,O削除に伴いdescriptionなどで代替
        # とりあえずdescriptionでセットを作る
        for e_node in self.seq_event[:retention]: 
            ret_set.add(e_node.description)
        return ret_set

    def retrieve_relevant_thoughts(self, *args):
        # キーワード辞書検索機能はそのまま
        contents = [c.lower() for c in args if c]
        ret = []
        for i in contents:
            if i in self.kw_to_thought:
                ret += self.kw_to_thought[i]
        return set(ret)

    def retrieve_relevant_events(self, *args):
        contents = [c.lower() for c in args if c]
        ret = []
        for i in contents:
            if i in self.kw_to_event:
                ret += self.kw_to_event[i]
        return set(ret)

    def get_last_chat(self, target_persona_name): 
        if target_persona_name.lower() in self.kw_to_chat: 
            return self.kw_to_chat[target_persona_name.lower()][0]
        else: 
            return False

    @lru_cache(maxsize=1000)
    def retrieve_nodes_by_keywords(self, query_keywords, top_k=10, importance_threshold=0.5, freshness_threshold=0.5):
        if not isinstance(query_keywords, list):
            query_keywords = [query_keywords]
        query_keywords = [q.lower() for q in query_keywords]

        candidate_nodes = set()
        for q in query_keywords:
            if q in self.kw_to_event:
                candidate_nodes.update(self.kw_to_event[q])
            if q in self.kw_to_thought:
                candidate_nodes.update(self.kw_to_thought[q])
            if q in self.kw_to_chat:
                candidate_nodes.update(self.kw_to_chat[q])

        related_keywords = self._find_related_keywords(query_keywords, top_k=5)
        for rk in related_keywords:
            if rk in self.kw_to_event:
                candidate_nodes.update(self.kw_to_event[rk])
            if rk in self.kw_to_thought:
                candidate_nodes.update(self.kw_to_thought[rk])
            if rk in self.kw_to_chat:
                candidate_nodes.update(self.kw_to_chat[rk])

        filtered_nodes = []
        for node in candidate_nodes:
            if node.importance >= importance_threshold and node.freshness >= freshness_threshold:
                filtered_nodes.append(node)

        filtered_nodes.sort(key=lambda x: (x.importance, x.freshness), reverse=True)
        return filtered_nodes[:top_k]

    def update_all_freshness(self, current_time):
        for node_id, node in self.id_to_node.items():
            node.update_freshness(current_time)

    def _find_related_keywords(self, query_keywords, top_k=5):
        related = set()
        all_keywords = set(list(self.kw_to_event.keys()) + list(self.kw_to_thought.keys()) + list(self.kw_to_chat.keys()))
        for q in query_keywords:
            for kw in all_keywords:
                if q in kw and kw != q:
                    related.add(kw)
        return list(related)[:top_k]