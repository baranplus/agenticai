import json
import redis
from typing import Optional, Dict, Any, List
from utils.logger import logger


class RedisManager:
    """
    Redis cache manager for caching question-answer pairs.
    - Connects to Redis instance
    - Caches question-answer pairs
    - Retrieves answers based on questions
    - Supports TTL (time-to-live) for cache expiration
    """

    def __init__(
        self,
        host: str,
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        decode_responses: bool = True,
    ):
        """
        Initialize Redis connection.
        
        Args:
            host: Redis host address
            port: Redis port (default: 6379)
            db: Redis database number (default: 0)
            password: Redis password (optional)
            decode_responses: Whether to decode responses as strings (default: True)
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.decode_responses = decode_responses

        try:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=decode_responses,
            )
            # Test connection
            if not self.client.ping():
                raise ConnectionError("Can't connect to Redis instance")
            logger.info(f"Connected to Redis at {host}:{port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise ConnectionError(f"Can't connect to an instance of Redis database: {str(e)}")

    def cache_qa_pair(
        self,
        question: str,
        answer: str,
        metadata: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Cache a question-answer pair in Redis.
        
        Args:
            question: The question string (used as key)
            answer: The answer string
            metadata: Optional metadata dictionary to store with the pair
            ttl: Time-to-live in seconds (optional)
        
        Returns:
            True if cached successfully, False otherwise
        """
        try:
            key = self._generate_key(question)
            data = {
                "question": question,
                "answer": answer,
                "metadata": metadata or {},
            }
            
            json_data = json.dumps(data, ensure_ascii=False)
            
            if ttl:
                self.client.setex(key, ttl, json_data)
            else:
                self.client.set(key, json_data)
            
            logger.info(f"Cached QA pair for question: {question}")
            return True
        except Exception as e:
            logger.error(f"Error caching QA pair: {str(e)}")
            return False

    def get_answer_by_question(
        self, question: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve answer and metadata for a given question.
        
        Args:
            question: The question string
        
        Returns:
            Dictionary with 'answer' and 'metadata' keys, or None if not found
        """
        try:
            key = self._generate_key(question)
            cached_data = self.client.get(key)
            
            if cached_data:
                data = json.loads(cached_data)
                logger.info(f"Cache hit for question: {question}")
                return {
                    "answer": data.get("answer"),
                    "metadata": data.get("metadata"),
                }
            
            logger.info(f"Cache miss for question: {question}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving cached answer: {str(e)}")
            return None

    def cache_qa_pairs_batch(
        self,
        qa_pairs: List[Dict[str, Any]],
        ttl: Optional[int] = None,
    ) -> int:
        """
        Cache multiple question-answer pairs in a single operation.
        
        Args:
            qa_pairs: List of dicts with 'question', 'answer', and optional 'metadata'
            ttl: Time-to-live in seconds for all pairs (optional)
        
        Returns:
            Number of successfully cached pairs
        """
        success_count = 0
        for pair in qa_pairs:
            question = pair.get("question")
            answer = pair.get("answer")
            metadata = pair.get("metadata")
            
            if question and answer:
                if self.cache_qa_pair(question, answer, metadata, ttl):
                    success_count += 1
        
        logger.info(f"Cached {success_count}/{len(qa_pairs)} QA pairs")
        return success_count

    def get_answer_with_similarity(
        self, question: str, similarity_threshold: float = 0.8
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve answer with fuzzy matching for similar questions.
        Uses Redis SCAN to find keys and does simple string similarity.
        
        Args:
            question: The question string
            similarity_threshold: Similarity score threshold (0.0 to 1.0)
        
        Returns:
            Dictionary with 'answer', 'metadata', and 'similarity_score' keys, or None
        """
        try:
            # First try exact match
            exact_match = self.get_answer_by_question(question)
            if exact_match:
                exact_match["similarity_score"] = 1.0
                return exact_match
            
            # Try fuzzy matching
            prefix = self._generate_key_prefix()
            best_match = None
            best_score = 0.0
            
            for key in self.client.scan_iter(match=f"{prefix}*"):
                similarity_score = self._calculate_similarity(
                    question, self._extract_question_from_key(key)
                )
                
                if similarity_score > best_score and similarity_score >= similarity_threshold:
                    best_score = similarity_score
                    cached_data = self.client.get(key)
                    if cached_data:
                        data = json.loads(cached_data)
                        best_match = {
                            "answer": data.get("answer"),
                            "metadata": data.get("metadata"),
                            "similarity_score": similarity_score,
                        }
            
            if best_match:
                logger.info(
                    f"Found similar question with score {best_score}: {question}"
                )
            return best_match
        except Exception as e:
            logger.error(f"Error retrieving answer with similarity: {str(e)}")
            return None

    def delete_cached_answer(self, question: str) -> bool:
        """
        Delete a cached question-answer pair.
        
        Args:
            question: The question string
        
        Returns:
            True if deleted, False otherwise
        """
        try:
            key = self._generate_key(question)
            result = self.client.delete(key)
            if result:
                logger.info(f"Deleted cached answer for question: {question}")
                return True
            logger.info(f"No cached answer found for question: {question}")
            return False
        except Exception as e:
            logger.error(f"Error deleting cached answer: {str(e)}")
            return False

    def clear_all_cache(self) -> bool:
        """
        Clear all cached question-answer pairs.
        
        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            prefix = self._generate_key_prefix()
            cursor = 0
            count = 0
            
            while True:
                cursor, keys = self.client.scan(cursor, match=f"{prefix}*")
                if keys:
                    count += self.client.delete(*keys)
                if cursor == 0:
                    break
            
            logger.info(f"Cleared {count} cached QA pairs")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False

    def get_all_cached_questions(self) -> List[str]:
        """
        Get all cached question strings.
        
        Returns:
            List of question strings
        """
        try:
            questions = []
            prefix = self._generate_key_prefix()
            
            for key in self.client.scan_iter(match=f"{prefix}*"):
                cached_data = self.client.get(key)
                if cached_data:
                    data = json.loads(cached_data)
                    questions.append(data.get("question"))
            
            logger.info(f"Retrieved {len(questions)} cached questions")
            return questions
        except Exception as e:
            logger.error(f"Error retrieving cached questions: {str(e)}")
            return []

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache information
        """
        try:
            prefix = self._generate_key_prefix()
            count = 0
            
            for _ in self.client.scan_iter(match=f"{prefix}*"):
                count += 1
            
            info = self.client.info()
            
            return {
                "total_cached_pairs": count,
                "redis_memory_used": info.get("used_memory_human", "N/A"),
                "redis_connected_clients": info.get("connected_clients", 0),
                "redis_db": self.db,
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {}

    def check_connection(self) -> bool:
        """
        Check if Redis connection is still alive.
        
        Returns:
            True if connected, False otherwise
        """
        try:
            return bool(self.client.ping())
        except Exception as e:
            logger.error(f"Redis connection check failed: {str(e)}")
            return False

    @staticmethod
    def _generate_key_prefix() -> str:
        """Generate prefix for all QA cache keys."""
        return "qa_cache:"

    @staticmethod
    def _generate_key(question: str) -> str:
        """Generate Redis key from question."""
        prefix = RedisManager._generate_key_prefix()
        # Normalize question for consistent key generation
        normalized = question.strip().lower().replace(" ", "_")
        return f"{prefix}{normalized}"

    @staticmethod
    def _extract_question_from_key(key: str) -> str:
        """Extract original question format from Redis key."""
        prefix = RedisManager._generate_key_prefix()
        return key.replace(prefix, "").replace("_", " ")

    @staticmethod
    def _calculate_similarity(str1: str, str2: str) -> float:
        """
        Calculate simple string similarity using character overlap.
        
        Args:
            str1: First string
            str2: Second string
        
        Returns:
            Similarity score between 0.0 and 1.0
        """
        s1 = str1.lower().split()
        s2 = str2.lower().split()
        
        if not s1 or not s2:
            return 0.0
        
        intersection = len(set(s1) & set(s2))
        union = len(set(s1) | set(s2))
        
        return intersection / union if union > 0 else 0.0
