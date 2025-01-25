import asyncio
from chat_completion_operations import ChatCompletion
from db_service import DatabaseService
import networkx as nx 
from cdlib import algorithms
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphRag: 
    def __init__(self, db_name, collection_name):
        self.db = DatabaseService(db_name = db_name, collection_name= collection_name)
        self.ch = ChatCompletion()

    async def split_doc_into_chunks(self):
        logger.info("Fetching all documents from the database.")
        docs = await self.db.get_all_data()
        logger.info(f"Retrieved {len(docs)} documents.")

        chunk_size = 600
        overlap_size = 100
        chunks = []
        
        logger.info(f"Starting to split documents into chunks with chunk_size={chunk_size} and overlap_size={overlap_size}.")
        for doc_index, doc in enumerate(docs[:2], start=1):  # Limit to first 2 documents for now
            logger.info(f"Processing document {doc_index}/{min(2, len(docs))} with length={len(doc)}.")
            for i in range(0, len(doc), chunk_size - overlap_size):
                chunk = doc[i: i + chunk_size]
                chunks.append(chunk)
                logger.info(f"Created chunk from index {i} to {i + chunk_size}. Chunk length: {len(chunk)}.")

        logger.info(f"Chunking complete. Total chunks created: {len(chunks)}.")
        return chunks

    async def extract_entities_and_relationships(self, chunks): 
        logger.info("Starting extraction of entities and relationships from chunks.")
        entities_and_relations = []
        for idx, chunk in enumerate(chunks, start=1):
            logger.info(f"Processing chunk {idx}/{len(chunks)}. Chunk size: {len(chunk)}")
            try:
                response = await self.ch.get_entities_and_relationships_from_chunk(chunk)
                await asyncio.sleep(1.5)
                entities_and_relations.append(response)
                logger.info(f"Successfully processed chunk {idx}.")
            except Exception as e:
                logger.error(f"Error processing chunk {idx}: {e}")
        
        logger.info("Writing entities and relationships to result1.md.")
        try:
            with open("result1.md", "w", encoding="utf-8") as f: 
                for idx, a in enumerate(entities_and_relations, start=1):
                    f.write(a)
                    f.write("\nEnd of one iteration\n")
                    logger.info(f"Written entity and relationship {idx} to result1.md.")
        except Exception as e:
            logger.error(f"Error writing to result1.md: {e}")

        logger.info("Extraction complete.")
        return entities_and_relations

    async def summarize_relationships(self, entities_and_relations): 
        logger.info("Starting summarization of relationships.")
        summarized_relationships = []
        for idx, node in enumerate(entities_and_relations, start=1):
            logger.info(f"Summarizing relationships for entity {idx}/{len(entities_and_relations)}.")
            try:
                response = await self.ch.summarize_relationships(node)
                await asyncio.sleep(1.5)
                summarized_relationships.append(response)
                logger.info(f"Successfully summarized relationships for entity {idx}.")
            except Exception as e:
                logger.error(f"Error summarizing relationships for entity {idx}: {e}")

        logger.info("Writing summarized relationships to result2.md.")
        try:
            with open("result2.md", "w", encoding="utf-8") as f: 
                for idx, a in enumerate(summarized_relationships, start=1):
                    f.write(a)
                    f.write("\nEnd of one iteration\n")
                    logger.info(f"Written summarized relationship {idx} to result2.md.")
        except Exception as e:
            logger.error(f"Error writing to result2.md: {e}")

        logger.info("Summarization complete.")
        return summarized_relationships

    def build_graph(self, summaries):
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
        return G

    def create_communities(self, G):
        mapping = {node: idx for idx, node in enumerate(G.nodes())}
        reverse_mapping = {idx: node for node, idx in mapping.items()}
        graph = nx.relabel_nodes(G, mapping)
        communities = []
        components = nx.connected_components(graph)
        for comp in components : 
            subgraph = graph.subgraph(comp)
            if len(subgraph.nodes) > 1 : 
                result = algorithms.leiden(subgraph)
                sub_communities = result.communities
                for community in sub_communities: 
                    communities.append([reverse_mapping[node] for node in community])
            else : 
                communities.append([reverse_mapping[node] for node in list(subgraph.nodes())])
        with open("result3.md", "w", encoding="utf-8") as f: 
            for a in communities:
                for b in a: 
                    f.write(b)
                f.write("\n###\n")
        return communities 

    async def summarize_communities(self, communities, G: nx.Graph):
        logger.info("Starting community summarization process.")
        all_communities_summary = []
        
        for idx, community in enumerate(communities, start=1): 
            logger.info(f"Processing community {idx}/{len(communities)} with {len(community)} nodes.")
            subgraph = G.subgraph(community)
            nodes = subgraph.nodes(data=True)
            edges = subgraph.edges(data=True)
            
            # Construct the description
            description = "Entities:\n"
            for node in nodes: 
                label = node[1].get('label', '') if isinstance(node[1], dict) else ""
                description += f"{node[0]}: {label}\n"
            description += "Relationships: "
            for edge in edges: 
                label = edge[2].get('label', '') if isinstance(edge[2], dict) else ""
                description += f"{edge[0]} -> {label} -> {edge[1]}, "

            logger.info(f"Description for community {idx} created. Length: {len(description)} characters.")

            try:
                # Summarize the community
                community_summary = await self.ch.summarize_communites(description)
                await asyncio.sleep(1.5)
                all_communities_summary.append(community_summary)
                logger.info(f"Successfully summarized community {idx}.")
            except Exception as e:
                logger.error(f"Error summarizing community {idx}: {e}")

        # Write summaries to a file
        logger.info("Writing all community summaries to result4.md.")
        try:
            with open("result4.md", "w", encoding="utf-8") as f: 
                for idx, (description, summary) in enumerate(zip(communities, all_communities_summary), start=1):
                    f.write(f"This is description for community {idx}:\n{description}\n")
                    f.write(f"Summary:\n{summary}\n")
                    f.write("\n###\n")
                    logger.info(f"Written summary for community {idx} to result4.md.")
        except Exception as e:
            logger.error(f"Error writing to result4.md: {e}")

        # Save to database
        logger.info("Inserting community summaries into the database.")
        try:
            await self.db.insert_community_summary_into_database("community_data", all_communities_summary)
            logger.info("Community summaries successfully inserted into the database.")
        except Exception as e:
            logger.error(f"Error inserting community summaries into the database: {e}")

        # Assign to class property
        self.all_communities_summary = all_communities_summary
        logger.info("Community summarization process completed.")

    async def initialise_graph_rag_pipeline(self): 
        chunks = await self.split_doc_into_chunks()
        entities_and_relations = await self.extract_entities_and_relationships(chunks)
        summarized_relationships = await self.summarize_relationships(entities_and_relations)
        G = self.build_graph(summarized_relationships)
        communities = self.create_communities(G)    
        await self.summarize_communities(communities, G)
