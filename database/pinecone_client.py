# database/pinecone_client.py
"""
Pinecone vector database client for semantic search.
Provides vector storage and similarity search for posts.
"""
from typing import List, Dict, Optional, Any
from loguru import logger
from config import config


class PineconeClient:
    """Handles all Pinecone vector database operations"""
    
    def __init__(self):
        self.api_key = config.PINECONE_API_KEY
        self.environment = config.PINECONE_ENVIRONMENT
        self.index_name = config.PINECONE_INDEX_NAME
        self.index = None
        self.dimension = 1536  # Claude embedding dimension
        
        if self.api_key:
            self._initialize()
    
    def _initialize(self):
        """Initialize Pinecone connection"""
        try:
            import pinecone
            
            pinecone.init(
                api_key=self.api_key,
                environment=self.environment
            )
            
            # Check if index exists, create if not
            if self.index_name not in pinecone.list_indexes():
                logger.info(f"Creating Pinecone index: {self.index_name}")
                pinecone.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine"
                )
            
            self.index = pinecone.Index(self.index_name)
            logger.info(f"Pinecone initialized: {self.index_name}")
        except ImportError:
            logger.warning("Pinecone not installed")
        except Exception as e:
            logger.error(f"Pinecone initialization failed: {e}")
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get embedding vector for text using Claude.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats (embedding vector) or None
        """
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
            
            # Use Claude to generate embedding-like representation
            # Note: Claude doesn't have a native embedding API
            # This is a placeholder - in production, use OpenAI or Cohere embeddings
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                messages=[{"role": "user", "content": f"Summarize this text in exactly 10 key concepts: {text}"}]
            )
            
            # Placeholder: Convert summary to simple vector
            # In production, use proper embedding API
            summary = response.content[0].text
            import hashlib
            hash_obj = hashlib.md5(summary.encode())
            hash_hex = hash_obj.hexdigest()
            
            # Convert hash to vector (placeholder)
            vector = [float(int(hash_hex[i:i+2], 16) / 255.0 for i in range(0, min(32, len(hash_hex)), 2)]
            
            # Pad or truncate to dimension
            if len(vector) < self.dimension:
                vector.extend([0.0] * (self.dimension - len(vector)))
            else:
                vector = vector[:self.dimension]
            
            return vector
        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            return None
    
    def upsert_post(self, post: Dict[str, Any]) -> bool:
        """
        Insert or update a post in Pinecone.
        
        Args:
            post: Post dictionary with '_id', 'content', etc.
            
        Returns:
            True if successful, False otherwise
        """
        if not self.index:
            logger.warning("Pinecone not initialized")
            return False
        
        try:
            post_id = str(post.get("_id", ""))
            content = post.get("content", "")
            
            if not content:
                return False
            
            vector = self.get_embedding(content)
            if not vector:
                return False
            
            # Prepare metadata
            metadata = {
                "source": post.get("source", "Unknown"),
                "location": post.get("location", "Unknown"),
                "topic": post.get("topic", "General"),
                "polarity": post.get("polarity", "Neutral"),
                "emotional_tone": post.get("emotional_tone", "Mixed"),
                "content_snippet": content[:200],
            }
            
            self.index.upsert(vectors=[(post_id, vector, metadata)])
            logger.info(f"Upserted post to Pinecone: {post_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to upsert post: {e}")
            return False
    
    def search_similar(
        self,
        query_text: str,
        top_k: int = 10,
        filter: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for posts similar to query text.
        
        Args:
            query_text: Text to search for
            top_k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of similar posts with scores
        """
        if not self.index:
            logger.warning("Pinecone not initialized")
            return []
        
        try:
            query_vector = self.get_embedding(query_text)
            if not query_vector:
                return []
            
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                filter=filter
            )
            
            return results.get("matches", [])
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def delete_post(self, post_id: str) -> bool:
        """
        Delete a post from Pinecone.
        
        Args:
            post_id: ID of post to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.index:
            return False
        
        try:
            self.index.delete(ids=[post_id])
            logger.info(f"Deleted post from Pinecone: {post_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete post: {e}")
            return False
    
    def get_index_stats(self) -> Dict:
        """Get statistics about the index"""
        if not self.index:
            return {}
        
        try:
            return self.index.describe_index_stats()
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}


# Single instance
pinecone_client = PineconeClient()
