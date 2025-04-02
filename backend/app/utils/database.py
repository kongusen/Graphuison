# backend/app/utils/database.py
from neo4j import GraphDatabase
from backend.app.config import settings
import logging

logger = logging.getLogger(__name__)

class Neo4jClient:
    def __init__(self):
        self.uri = settings.NEO4J_URI
        self.username = settings.NEO4J_USERNAME
        self.password = settings.NEO4J_PASSWORD
        self.driver = None

    def connect(self):
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            self.driver.verify_connectivity()
            logger.info("Neo4j database connected successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j database: {e}")
            raise

    def close(self):
        if self.driver:
            self.driver.close()
            logger.info("Neo4j database connection closed.")

    def create_node(self, name: str, type: str):
         with self.driver.session() as session:
            try:
                query = """
                    CREATE (n:Entity {name: $name, type: $type})
                    RETURN n
                """
                result = session.run(query, name=name, type=type)
                record = result.single()
                node = record.get("n")
                return node.id
            except Exception as e:
                logger.error(f"Failed to create entity node: {e}")
                return None

    def create_relationship(self, source_id: int, target_id: int, relation: str):
        with self.driver.session() as session:
            try:
                query = """
                    MATCH (source:Entity), (target:Entity)
                    WHERE id(source) = $source_id AND id(target) = $target_id
                    CREATE (source)-[r:Relationship {relation: $relation}]->(target)
                    RETURN r
                """
                result = session.run(query, source_id=source_id, target_id=target_id, relation=relation)
                record = result.single()
                relationship = record.get("r")
                return relationship.id
            except Exception as e:
                 logger.error(f"Failed to create relationship node: {e}")
                 return None


    def get_graph_data(self):
        with self.driver.session() as session:
            try:
                 query = """
                        MATCH (source:Entity)-[r:Relationship]->(target:Entity)
                        RETURN source.name as source, type(r) as relation, target.name as target, 
                               source.type as source_type, target.type as target_type
                    """
                 result = session.run(query)
                 graph_data = [
                     {
                         "source": record["source"], 
                         "relation": record["relation"], 
                         "target": record["target"],
                         "source_type": record["source_type"],
                         "target_type": record["target_type"]
                     } 
                     for record in result
                 ]
                 return graph_data
            except Exception as e:
                logger.error(f"Failed to fetch graph data: {e}")
                return []

    def clear_database(self):
        with self.driver.session() as session:
            try:
                # 删除所有节点和关系
                query = """
                    MATCH (n)
                    DETACH DELETE n
                """
                session.run(query)
                logger.info("Database cleared successfully.")
                return True
            except Exception as e:
                logger.error(f"Failed to clear database: {e}")
                return False

    def get_entity_by_name(self, name: str):
        with self.driver.session() as session:
            try:
                query = """
                    MATCH (n:Entity {name: $name})
                    RETURN n
                """
                result = session.run(query, name=name)
                record = result.single()
                if record:
                    return record.get("n")
                return None
            except Exception as e:
                logger.error(f"Failed to get entity by name: {e}")
                return None

    def find_related_entities(self, entity_name: str, max_depth: int = 2):
        with self.driver.session() as session:
            try:
                query = """
                    MATCH path = (start:Entity {name: $entity_name})-[*1..%d]-(related)
                    RETURN related.name as name, related.type as type
                """ % max_depth
                result = session.run(query, entity_name=entity_name)
                entities = [{"name": record["name"], "type": record["type"]} for record in result]
                return entities
            except Exception as e:
                logger.error(f"Failed to find related entities: {e}")
                return []

neo4j_client = Neo4jClient()