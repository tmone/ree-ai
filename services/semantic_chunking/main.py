"""
Semantic Chunking Service - 6 Steps theo CTO
Uses Sentence-Transformers + NLTK for semantic text chunking
"""
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import nltk

from core.base_service import BaseService
from shared.utils.logger import LogEmoji
from shared.config import settings


# Download NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


class SemanticChunker(BaseService):
    """
    Semantic Chunking Service - CTO Service #3

    6 Steps:
    1. Sentence Segmentation
    2. Generate Embedding cho từng câu
    3. Cosine Similarity Calculation
    4. Combine Sentences với threshold >0.75
    5. Overlap window
    6. Create Embedding for whole chunk
    """

    def __init__(self):
        super().__init__(
            name="semantic_chunking",
            version="1.0.0",
            capabilities=["text_chunking", "semantic_analysis"],
            port=8080  # Match docker-compose internal port (exposed as 8082:8080)
        )

        # MEDIUM FIX Bug#13: Use configurable embedding model
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.logger.info(f"{LogEmoji.SUCCESS} Loaded SentenceTransformer model: {settings.EMBEDDING_MODEL}")

    def setup_routes(self):
        """Setup Semantic Chunking API routes"""

        @self.app.post("/chunk")
        async def chunk_text(request: Dict[str, Any]):
            """
            Chunk text using 6-step semantic chunking

            Request: {"text": "..."}
            Response: {"chunks": [...], "count": 5}
            """
            text = request.get("text", "")

            if not text:
                return {"error": "No text provided"}

            chunks = self.chunk(text)

            return {
                "success": True,
                "count": len(chunks),
                "chunks": chunks,
                "method": "6-step semantic chunking"
            }

    def chunk(self, text: str, threshold: float = None, overlap: int = 1) -> List[Dict[str, Any]]:
        """
        6-Step Semantic Chunking

        Args:
            text: Input text to chunk
            threshold: Similarity threshold for combining sentences (default from config)
            overlap: Number of sentences to overlap between chunks

        Returns:
            List of chunks with text and embeddings
        """
        # MEDIUM FIX Bug#18: Use configurable threshold
        if threshold is None:
            threshold = settings.CHUNK_SIMILARITY_THRESHOLD

        # Step 1: Sentence Segmentation
        sentences = self._step1_segment_sentences(text)

        if len(sentences) == 0:
            return []

        # Step 2: Generate Embedding cho từng câu
        sentence_embeddings = self._step2_generate_embeddings(sentences)

        # Step 3: Cosine Similarity Calculation
        similarities = self._step3_calculate_similarities(sentence_embeddings)

        # Step 4: Combine Sentences với threshold
        combined_chunks = self._step4_combine_sentences(sentences, similarities, threshold)

        # Step 5: Overlap window
        overlapped_chunks = self._step5_add_overlap(combined_chunks, overlap)

        # Step 6: Create Embedding for whole chunk
        final_chunks = self._step6_create_chunk_embeddings(overlapped_chunks)

        self.logger.info(
            f"{LogEmoji.SUCCESS} Chunked {len(sentences)} sentences into {len(final_chunks)} chunks"
        )

        return final_chunks

    def _step1_segment_sentences(self, text: str) -> List[str]:
        """
        Step 1: Sentence Segmentation using NLTK

        Example:
            Input: "Nhà 3 phòng ngủ. Giá 5 tỷ. View đẹp."
            Output: ["Nhà 3 phòng ngủ.", "Giá 5 tỷ.", "View đẹp."]
        """
        # Use NLTK's sentence tokenizer
        sentences = nltk.sent_tokenize(text, language='english')  # Works for Vietnamese too

        # Filter empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    def _step2_generate_embeddings(self, sentences: List[str]) -> np.ndarray:
        """
        Step 2: Generate Embedding cho từng câu

        Uses: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
        Output dimension: 384
        """
        embeddings = self.model.encode(sentences, convert_to_numpy=True)
        return embeddings

    def _step3_calculate_similarities(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Step 3: Cosine Similarity Calculation

        Calculates similarity matrix between all sentence pairs
        """
        # Normalize embeddings
        normalized = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

        # Calculate cosine similarity matrix
        similarity_matrix = np.dot(normalized, normalized.T)

        return similarity_matrix

    def _step4_combine_sentences(
        self,
        sentences: List[str],
        similarities: np.ndarray,
        threshold: float
    ) -> List[str]:
        """
        Step 4: Combine Sentences với threshold >0.75

        Groups consecutive sentences with similarity > threshold
        """
        if len(sentences) == 0:
            return []

        chunks = []
        current_chunk = [sentences[0]]

        for i in range(1, len(sentences)):
            # Check similarity with previous sentence
            if similarities[i-1][i] > threshold:
                # Similar -> add to current chunk
                current_chunk.append(sentences[i])
            else:
                # Not similar -> start new chunk
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentences[i]]

        # Add last chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _step5_add_overlap(self, chunks: List[str], window: int) -> List[str]:
        """
        Step 5: Overlap window

        Adds overlap between chunks for context continuity

        Example with window=1:
            Chunk 1: "Sentence 1. Sentence 2."
            Chunk 2: "Sentence 2. Sentence 3."  (Sentence 2 overlaps)
        """
        if len(chunks) <= 1 or window == 0:
            return chunks

        overlapped = []

        for i in range(len(chunks)):
            chunk_sentences = nltk.sent_tokenize(chunks[i])

            # Add sentences from previous chunk for overlap
            if i > 0 and window > 0:
                prev_sentences = nltk.sent_tokenize(chunks[i-1])
                overlap_sentences = prev_sentences[-window:]
                chunk_sentences = overlap_sentences + chunk_sentences

            overlapped.append(" ".join(chunk_sentences))

        return overlapped

    def _step6_create_chunk_embeddings(self, chunks: List[str]) -> List[Dict[str, Any]]:
        """
        Step 6: Create Embedding for whole chunk

        Generates final embeddings for each chunk
        """
        chunk_embeddings = self.model.encode(chunks, convert_to_numpy=True)

        final_chunks = []
        for chunk_text, embedding in zip(chunks, chunk_embeddings):
            final_chunks.append({
                "text": chunk_text,
                "embedding": embedding.tolist(),
                "embedding_dimension": len(embedding)
            })

        return final_chunks


if __name__ == "__main__":
    service = SemanticChunker()
    service.run()
