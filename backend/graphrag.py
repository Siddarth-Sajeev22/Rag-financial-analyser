from chat_completion_operations import ChatCompletion
from db_service import DatabaseService
import networkx as nx 
from pyvis.network import Network

db = DatabaseService(db_name = "standard_glass_lining", collection_name="drhp")
ch = ChatCompletion()

def split_doc_into_chunks():
    docs = db.get_all_data()
    chunk_size = 600
    overlap_size = 100
    chunks = []
    for doc in docs[:2] : 
        for i in range(0, len(doc), chunk_size-overlap_size):
            chunks.append(doc[i: i+chunk_size])
    return chunks

def extract_entitites_and_relationships(chunks): 
    entities_and_relations = []
    for chunk in chunks : 
        response = ch.get_entities_and_relationships_from_chunk(chunk)
        entities_and_relations.append(response)
    with open("result1.md", "w", encoding="utf-8") as f: 
        for a in entities_and_relations:
            f.write(a)
            f.write("End of one iteration")
    return entities_and_relations

def summarize_relationships(entities_and_relations): 
    summarized_relationships = []
    for node in entities_and_relations: 
        response = ch.summarize_relationships(node)
        summarized_relationships.append(response)
    with open("result2.md", "w", encoding="utf-8") as f: 
        for a in summarized_relationships:
            f.write(a)
            f.write("End of one iteration")
    return summarized_relationships

def build_graph(summaries):
    G = nx.Graph()
    for node in summaries :
        lines = node.split("\n") 
        entities_section = False 
        relationship_section = False 
        for line in lines : 
            if "summary" in line.lower() or line.strip()=="":
                continue 
            if line.strip().startswith("**Key Entities:**"): 
                entities_section = True 
                relationship_section = False 
                continue 
            elif line.strip().startswith("**Key Relationships:**"): 
                relationship_section = True 
                entities_section = False
                continue 
            elif entities_section == True : 
                line = line.strip()
                label_index = line.find("**:")
                label = line[label_index+3:]
                entity = line[2:label_index]
                entity = entity.replace("**", "").strip()
                label = label.strip()
                G.add_node(entity, label=label)
            elif relationship_section == True and line.strip(): 
                parts = line.split("->")
                for i in range(len(parts)) : 
                    part = parts[i]
                    part = part.replace("-", "").strip()
                    colon_index = part.find(":")    
                    if colon_index != -1 : 
                        part = part[:colon_index]
                    parts[i] = part
                if len(parts) < 3: 
                    continue 
                start_node = None 
                label = None 
                for i in range(len(parts)): 
                    part = parts[i].strip()
                    if (i%2 == 0) : 
                        entity = part.replace("**", "").strip()
                        if start_node is None : 
                            start_node = entity 
                        else : 
                            end_node = entity 
                            if start_node not in G:
                                G.add_node(start_node)
                            if end_node not in G:
                                G.add_node(end_node)
                            if label:  # If a label is present, create the edge
                                G.add_edge(start_node, end_node, label=label)
                            start_node = end_node
                    else : 
                        label = part.strip()
                
# chunks = split_doc_into_chunks()
# entities_and_relations = extract_entitites_and_relationships(chunks)
# summaries = summarize_relationships(entities_and_relations)
# build_graph(summaries)
