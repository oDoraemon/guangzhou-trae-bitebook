from typing import List, Dict, Any
from app.model.doc_text import DocText

def ask_ai(texts: List[DocText]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for t in texts[:50]:
        base = (t.text or "").strip()
        snippet = base[:160] if base else ""
        q = f"根据以下内容提出一个问题：{snippet}"
        a = f"解析：该段落主要内容概述为：{snippet}"
        items.append({"doc_text_id": t.id, "page_number": t.page_number, "question": q, "answer": a, "provider": "aliyun", "model": "placeholder"})
    return items

