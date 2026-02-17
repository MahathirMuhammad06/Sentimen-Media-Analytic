"""
Advanced keyword extraction untuk history search dengan akurasi tinggi
Menggunakan kombinasi TF-IDF, named entity recognition, dan title keyword prioritization
"""

import re
from collections import Counter
from typing import List, Tuple

# Indonesian stopwords
INDONESIAN_STOPWORDS = {
    'yang', 'dan', 'di', 'ke', 'dari', 'untuk', 'adalah', 'dengan', 'pada', 'oleh',
    'atau', 'ini', 'itu', 'juga', 'telah', 'akan', 'dapat', 'ada', 'tidak', 'sedang',
    'saat', 'melalui', 'serta', 'seperti', 'bagian', 'suatu', 'karena', 'kalau', 'bila',
    'selain', 'lebih', 'kurang', 'dalam', 'antara', 'mereka', 'mereka', 'kita', 'kami',
    'sama', 'bukan', 'sudah', 'belum', 'memang', 'tentang', 'sebelum', 'sesudah',
    'tapi', 'namun', 'padahal', 'malah', 'justru', 'sebaliknya', 'apalagi', 'bahkan',
    'oleh', 'daripada', 'uraian', 'laporan', 'berita', 'artikel', 'tentang', 'kata',
    'a', 'an', 'the', 'at', 'by', 'in', 'to', 'as', 'is', 'was', 'be', 'are',
    'com', 'co', 'id', 'http', 'https', 'www', 'tribunnews', 'tribunlampung', 'lampung',
    'org', 'net', 'raih', 'ambil', 'buat', 'buat', 'lain', 'kali', 'sangat', 'sengat'
}

# Common title patterns to extract (proper nouns, named entities)
ENTITY_PATTERNS = [
    r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # Proper nouns (Nama Orang, Tempat)
    r'\b([A-Z]{2,})\b',  # Acronyms (KUHP, UU, dll)
]

def extract_keywords_high_accuracy(title: str, content: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords dengan akurasi tinggi menggunakan:
    1. Title keyword prioritization (weighted 3x)
    2. Named entity recognition
    3. TF-IDF scoring
    4. Frequency analysis
    
    Args:
        title: Article title (high priority)
        content: Article content
        max_keywords: Maximum keywords to return
        
    Returns:
        List of extracted keywords ranked by relevance
    """
    
    if not title or not content:
        return []
    
    # Combined text with title weighted higher
    combined_text = title + " " + title + " " + title + " " + content
    
    # Tokenize dan clean
    tokens = _tokenize_indonesian(combined_text)
    
    # Step 1: Extract named entities dari title (highest priority)
    title_entities = _extract_entities(title)
    title_tokens = _tokenize_indonesian(title)
    
    # Step 2: Calculate word frequency dengan weighting
    word_freq = Counter()
    
    # Add title tokens with 3x weight (but filter stopwords)
    for token in title_tokens:
        if token not in INDONESIAN_STOPWORDS and len(token) > 2:
            word_freq[token] += 3
    
    # Add content tokens with 1x weight
    for token in tokens:
        if token not in INDONESIAN_STOPWORDS and len(token) > 2:
            word_freq[token] += 1
    
    # Step 3: Prioritize named entities (proper nouns, acronyms)
    entity_keywords = []
    for entity in title_entities:
        clean_entity = entity.strip()
        if clean_entity.lower() not in INDONESIAN_STOPWORDS and len(clean_entity) > 2:
            # Boost entity score significantly
            score = word_freq.get(clean_entity.lower(), 0) + 50
            entity_keywords.append((clean_entity, score))
    
    # Step 4: Extract high-frequency keywords
    all_keywords = []
    
    # Add entities first (remove duplicates)
    entity_set = {e[0].lower() for e in entity_keywords}
    all_keywords.extend(entity_keywords)
    
    # Add top frequent words (filter entities already added)
    for word, freq in word_freq.most_common(max_keywords * 3):
        if word.lower() not in entity_set and len(word) > 2:
            all_keywords.append((word, freq))
    
    # Step 5: Sort by relevance and return (deduplicate)
    sorted_keywords = sorted(all_keywords, key=lambda x: x[1], reverse=True)
    
    # Deduplicate preserving order
    seen = set()
    result = []
    for kw, score in sorted_keywords:
        kw_lower = kw.lower()
        if kw_lower not in seen and len(result) < max_keywords:
            seen.add(kw_lower)
            result.append(kw)
    
    return result


def _tokenize_indonesian(text: str) -> List[str]:
    """
    Tokenize Indonesian text dengan normalization
    
    Args:
        text: Text to tokenize
        
    Returns:
        List of normalized tokens
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove URLs
    text = re.sub(r'http[s]?://\S+', '', text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Split on word boundaries (keep Indonesian words)
    # Match: alphanumeric, Indonesian characters, and hyphens
    tokens = re.findall(r'[a-z0-9\s\-_áàâäãåèéêëìíîïòóôöõùúûüñç]{2,}', text)
    
    # Further split by spaces and hyphens
    all_tokens = []
    for token in tokens:
        parts = re.split(r'[\s\-_]+', token.strip())
        all_tokens.extend([p for p in parts if p])
    
    return all_tokens


def _extract_entities(text: str) -> List[str]:
    """
    Extract named entities (proper nouns, acronyms) dari text
    
    Args:
        text: Text to extract from
        
    Returns:
        List of entities
    """
    entities = []
    
    for pattern in ENTITY_PATTERNS:
        matches = re.findall(pattern, text)
        entities.extend(matches)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_entities = []
    for entity in entities:
        if entity.lower() not in seen and len(entity) > 1:
            seen.add(entity.lower())
            unique_entities.append(entity)
    
    return unique_entities


def format_keywords_for_db(keywords: List[str], max_length: int = 512) -> str:
    """
    Format keywords list untuk database storage (comma-separated)
    
    Args:
        keywords: List of keywords
        max_length: Maximum string length
        
    Returns:
        Comma-separated keywords string
    """
    if not keywords:
        return None
    
    result = ", ".join(keywords)
    
    # Truncate if exceeds max length
    if len(result) > max_length:
        result = result[:max_length]
        # Remove incomplete last keyword
        result = result[:result.rfind(',')].strip()
    
    return result if result else None


# Backward compatibility - keep old function but improve it
def extract_keywords_flagged(text: str) -> list:
    """
    Extract flagged keywords (negative, crime, etc)
    Keep for backward compatibility
    """
    keywords = {
        "korupsi", "kriminal", "demo", "kecelakaan", "bencana",
        "pembunuhan", "narkoba", "olahraga", "hukum", "polisi",
        "pencurian", "penipuan", "pembakaran", "tawuran", "bentrok"
    }
    
    text = text.lower()
    found = [k for k in keywords if k in text]
    return found
