from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2') 

def get_embedding(text):
    return model.encode(text, convert_to_numpy=True)

def is_semantically_similar(emb1, emb2, threshold=0.8):
    sim = cosine_similarity([emb1], [emb2])[0][0]
    return sim > threshold

def compress_semantic_memories(memories, threshold=0.8):
    compressed = []
    temp_group = []
    temp_embeddings = []

    def add_group_to_compressed(group, embeddings):
        if not group:
            return
        start_time = group[0]['time']
        end_time = group[-1]['time']
        summary = group[0]['description'] 
        avg_emotion = [round(sum(e) / len(e), 2) for e in zip(*[m['emotion'] for m in group if 'emotion' in m])]
        last_needs = group[-1].get('basic_needs')

        compressed.append({
            "time_start": start_time,
            "time_end": end_time,
            "description": summary,
            "emotion": avg_emotion,
            "final_basic_needs": last_needs
        })

    for mem in memories:
        desc = mem.get('description', '').strip()
        if not desc:
            continue
        emb = get_embedding(desc)
        if not temp_group:
            temp_group.append(mem)
            temp_embeddings.append(emb)
        else:
            last_emb = temp_embeddings[-1]
            if is_semantically_similar(last_emb, emb, threshold=threshold):
                temp_group.append(mem)
                temp_embeddings.append(emb)
            else:
                add_group_to_compressed(temp_group, temp_embeddings)
                temp_group = [mem]
                temp_embeddings = [emb]
    add_group_to_compressed(temp_group, temp_embeddings)
    return compressed
