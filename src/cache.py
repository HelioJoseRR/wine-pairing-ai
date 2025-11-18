"""
Sistema de cache simples para requisições LLM
"""
import hashlib
import json
from typing import Dict, Optional, Any
from pathlib import Path

class LLMCache:
    """Cache em memória com persistência opcional em disco"""
    
    def __init__(self, cache_file: Optional[str] = None):
        self.cache: Dict[str, Any] = {}
        self.cache_file = Path(cache_file) if cache_file else None
        
        if self.cache_file and self.cache_file.exists():
            self._load_cache()
    
    def _hash_key(self, text: str) -> str:
        """Gera hash MD5 do texto para usar como chave"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Recupera valor do cache"""
        hash_key = self._hash_key(key)
        return self.cache.get(hash_key)
    
    def set(self, key: str, value: Any) -> None:
        """Armazena valor no cache"""
        hash_key = self._hash_key(key)
        self.cache[hash_key] = value
        
        if self.cache_file:
            self._save_cache()
    
    def _load_cache(self) -> None:
        """Carrega cache do disco"""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                self.cache = json.load(f)
        except Exception:
            self.cache = {}
    
    def _save_cache(self) -> None:
        """Salva cache no disco"""
        try:
            if self.cache_file:
                self.cache_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # Falha silenciosa se não conseguir salvar
    
    def clear(self) -> None:
        """Limpa todo o cache"""
        self.cache = {}
        if self.cache_file and self.cache_file.exists():
            self.cache_file.unlink()
