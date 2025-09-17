
import re
import logging
from typing import List, Dict, Tuple
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Check for 'punkt_tab' and download if necessary
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextChunker:
    """Handle text chunking for large documents."""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        """
        Initialize the text chunker.
        
        Args:
            chunk_size: Maximum number of characters per chunk
            overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.stop_words = set(stopwords.words('english'))
    
    def chunk_by_sentences(self, text: str) -> List[Dict]:
        """
        Chunk text by sentences while respecting chunk size limits.
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of chunk dictionaries with metadata
        """
        try:
            sentences = sent_tokenize(text)
            chunks = []
            current_chunk = ""
            current_chunk_sentences = []
            chunk_id = 0
            
            for i, sentence in enumerate(sentences):
                # Check if adding this sentence would exceed chunk size
                if len(current_chunk + sentence) > self.chunk_size and current_chunk:
                    # Save current chunk
                    chunks.append({
                        'id': chunk_id,
                        'text': current_chunk.strip(),
                        'sentences': current_chunk_sentences.copy(),
                        'start_sentence': chunk_id * len(current_chunk_sentences) if chunks else 0,
                        'end_sentence': chunk_id * len(current_chunk_sentences) + len(current_chunk_sentences) - 1,
                        'word_count': len(word_tokenize(current_chunk))
                    })
                    
                    # Start new chunk with overlap
                    if self.overlap > 0 and current_chunk_sentences:
                        overlap_text = self._get_overlap_text(current_chunk_sentences)
                        current_chunk = overlap_text
                        current_chunk_sentences = [s for s in current_chunk_sentences if s in overlap_text]
                    else:
                        current_chunk = ""
                        current_chunk_sentences = []
                    
                    chunk_id += 1
                
                current_chunk += " " + sentence if current_chunk else sentence
                current_chunk_sentences.append(sentence)
            
            # Add the last chunk if it has content
            if current_chunk.strip():
                chunks.append({
                    'id': chunk_id,
                    'text': current_chunk.strip(),
                    'sentences': current_chunk_sentences,
                    'start_sentence': len(chunks) * len(current_chunk_sentences) if chunks else 0,
                    'end_sentence': len(chunks) * len(current_chunk_sentences) + len(current_chunk_sentences) - 1,
                    'word_count': len(word_tokenize(current_chunk))
                })
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking text by sentences: {e}")
            return self._fallback_chunk(text)
    
    def chunk_by_paragraphs(self, text: str) -> List[Dict]:
        """
        Chunk text by paragraphs while respecting chunk size limits.
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of chunk dictionaries with metadata
        """
        try:
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            chunks = []
            current_chunk = ""
            current_paragraphs = []
            chunk_id = 0
            
            for paragraph in paragraphs:
                if len(current_chunk + paragraph) > self.chunk_size and current_chunk:
                    # Save current chunk
                    chunks.append({
                        'id': chunk_id,
                        'text': current_chunk.strip(),
                        'paragraphs': current_paragraphs.copy(),
                        'word_count': len(word_tokenize(current_chunk))
                    })
                    
                    # Start new chunk with overlap
                    if self.overlap > 0 and current_paragraphs:
                        overlap_text = current_paragraphs[-1] if len(current_paragraphs[-1]) <= self.overlap else current_paragraphs[-1][:self.overlap]
                        current_chunk = overlap_text
                        current_paragraphs = [overlap_text]
                    else:
                        current_chunk = ""
                        current_paragraphs = []
                    
                    chunk_id += 1
                
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
                current_paragraphs.append(paragraph)
            
            # Add the last chunk
            if current_chunk.strip():
                chunks.append({
                    'id': chunk_id,
                    'text': current_chunk.strip(),
                    'paragraphs': current_paragraphs,
                    'word_count': len(word_tokenize(current_chunk))
                })
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking text by paragraphs: {e}")
            return self._fallback_chunk(text)
    
    def _get_overlap_text(self, sentences: List[str]) -> str:
        """Get overlap text from the end of current chunk."""
        overlap_text = ""
        for sentence in reversed(sentences):
            if len(overlap_text + sentence) <= self.overlap:
                overlap_text = sentence + " " + overlap_text if overlap_text else sentence
            else:
                break
        return overlap_text.strip()
    
    def _fallback_chunk(self, text: str) -> List[Dict]:
        """Fallback chunking method using simple character splitting."""
        chunks = []
        chunk_id = 0
        
        for i in range(0, len(text), self.chunk_size - self.overlap):
            chunk_text = text[i:i + self.chunk_size]
            if chunk_text.strip():
                chunks.append({
                    'id': chunk_id,
                    'text': chunk_text.strip(),
                    'word_count': len(word_tokenize(chunk_text)),
                    'start_pos': i,
                    'end_pos': min(i + self.chunk_size, len(text))
                })
                chunk_id += 1
        
        return chunks

class TextSearcher:
    """Handle advanced text searching across chunks."""
    
    def __init__(self, chunks: List[Dict]):
        """Initialize with text chunks."""
        self.chunks = chunks
        self.stop_words = set(stopwords.words('english'))
    
    def search_chunks(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search for query across all chunks with relevance scoring.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of relevant chunks with scores
        """
        try:
            query_terms = [term.lower() for term in word_tokenize(query) if term.lower() not in self.stop_words]
            results = []
            
            for chunk in self.chunks:
                score = self._calculate_relevance_score(chunk['text'], query_terms)
                if score > 0:
                    # Find exact matches for highlighting
                    matches = self._find_matches(chunk['text'], query)
                    results.append({
                        'chunk': chunk,
                        'score': score,
                        'matches': matches,
                        'snippet': self._generate_snippet(chunk['text'], query, 200)
                    })
            
            # Sort by relevance score and return top results
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Error searching chunks: {e}")
            return []
    
    def _calculate_relevance_score(self, text: str, query_terms: List[str]) -> float:
        """Calculate relevance score for a text chunk."""
        text_lower = text.lower()
        text_words = word_tokenize(text_lower)
        
        score = 0.0
        for term in query_terms:
            # Exact matches get higher score
            if term in text_lower:
                score += text_lower.count(term) * 2.0
            
            # Partial matches get lower score
            for word in text_words:
                if term in word and len(term) > 2:
                    score += 0.5
        
        # Normalize by text length
        return score / len(text_words) if text_words else 0.0
    
    def _find_matches(self, text: str, query: str) -> List[Tuple[int, int]]:
        """Find all match positions in text."""
        matches = []
        query_lower = query.lower()
        text_lower = text.lower()
        
        start = 0
        while True:
            pos = text_lower.find(query_lower, start)
            if pos == -1:
                break
            matches.append((pos, pos + len(query)))
            start = pos + 1
        
        return matches
    
    def _generate_snippet(self, text: str, query: str, max_length: int = 200) -> str:
        """Generate a relevant snippet around the query match."""
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Find first occurrence
        pos = text_lower.find(query_lower)
        if pos == -1:
            return text[:max_length] + "..." if len(text) > max_length else text
        
        # Calculate snippet boundaries
        start = max(0, pos - max_length // 2)
        end = min(len(text), start + max_length)
        
        snippet = text[start:end]
        
        # Add ellipsis if needed
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        
        return snippet
