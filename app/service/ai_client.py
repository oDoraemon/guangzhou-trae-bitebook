from typing import List, Dict, Any, Optional
import os
import json
from sqlalchemy.orm import Session
from app.repository.doc_text_repository import DocTextRepository

def ask_ai(book_id: int, db: Session, max_rounds: int = 6) -> List[Dict[str, Any]]:
    repo = DocTextRepository()

    def read_book_texts(start: int = 0, limit: int = 10, page_number: Optional[int] = None) -> str:
        items = repo.list_range_by_book(db, book_id, start, limit)
        if page_number is not None:
            items = [t for t in items if t.page_number == page_number]
        payload = []
        for t in items:
            payload.append({
                "id": t.id,
                "book_id": t.book_id,
                "page_number": t.page_number,
                "text": t.text or "",
                "bbox_x": t.bbox_x,
                "bbox_y": t.bbox_y,
                "bbox_w": t.bbox_w,
                "bbox_h": t.bbox_h,
            })
        return json.dumps({"items": payload, "count": len(payload), "start": start, "limit": limit})

    tools = [
        {
            "type": "function",
            "function": {
                "name": "read_book_texts",
                "description": "读取数据库中指定图书的文本段落。支持分页与按页过滤。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start": {"type": "integer", "description": "起始偏移"},
                        "limit": {"type": "integer", "description": "读取数量"},
                        "page_number": {"type": "integer", "description": "页面编号，可选"},
                    },
                    "required": ["start", "limit"]
                },
            },
        },
    ]
    prompt = f"""
        请读取接口文本，并针对返回的文本设计考核题目，考核读者对相关概念的理解。
        你需要判断提供给你的文本是否包含足够的信息来设计题目。若文本不足，请继续读取。
        若文本足够，你需要根据文本设计题目。
        每设计一道题目，你需要包含一个问题和一个解析。
        问题需要是具体的、可回答的问题，解析需要是对问题的详细解释。
        每出完一道题，你需要清除之前的记忆，继续读取文本，设计下一道题。
        直到后台接口不再返回新的数据。
    """

    messages = [
        {"role": "system", "content": "你负责为指定资料生成若干理解性问题及解析, 帮助读者记忆相关概念。必要时调用 read_book_texts 获取更多上下文。最终仅以 JSON 数组输出，每项包含 doc_text_id、page_number、question、answer。"},
        {"role": "user", "content": prompt},
    ]

    func_mapper = {
        "read_book_texts": read_book_texts,
    }

    api_key = os.getenv("DASHSCOPE_API_KEY")

    def try_parse_items(content: str) -> List[Dict[str, Any]]:
        try:
            data = json.loads(content)
        except Exception:
            import re
            m = re.search(r"\[.*\]", content, re.S)
            if not m:
                return []
            try:
                data = json.loads(m.group(0))
            except Exception:
                return []
        if not isinstance(data, list):
            return []
        items: List[Dict[str, Any]] = []
        for it in data:
            items.append({
                "doc_text_id": it.get("doc_text_id"),
                "page_number": it.get("page_number"),
                "question": it.get("question"),
                "answer": it.get("answer"),
                "provider": "aliyun",
                "model": "qwen-plus",
            })
        return items

    def local_fallback(max_items: int = 20) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        cursor = 0
        while len(items) < max_items:
            batch = repo.list_range_by_book(db, book_id, cursor, 1)
            if not batch:
                break
            t = batch[0]
            base = (t.text or "").strip()
            if not base:
                cursor += 1
                continue
            q = f"请基于该段文本提出理解性问题：{base[:140]}"
            a = f"解析：该段文本要点概述：{base[:280]}"
            items.append({"doc_text_id": t.id, "page_number": t.page_number, "question": q, "answer": a, "provider": "local", "model": "fallback"})
            cursor += 1
        return items

    if not api_key:
        return local_fallback()

    try:
        import dashscope
        def call(messages):
            return dashscope.Generation.call(
                api_key=api_key,
                model="qwen-plus",
                messages=messages,
                tools=tools,
                result_format="message",
            )

        response = call(messages)
        assistant_msg = response.output.choices[0].message
        messages.append(assistant_msg)

        rounds = 0
        while rounds < max_rounds and assistant_msg.get("tool_calls"):
            for tool in assistant_msg["tool_calls"]:
                name = tool["function"]["name"]
                args = json.loads(tool["function"]["arguments"]) if isinstance(tool["function"]["arguments"], str) else tool["function"]["arguments"]
                tool_id = tool.get("id")
                result = func_mapper[name](**args)
                messages.append({"role": "tool", "content": result, "tool_call_id": tool_id})
            response = call(messages)
            assistant_msg = response.output.choices[0].message
            messages.append(assistant_msg)
            rounds += 1

        items = try_parse_items(assistant_msg.get("content", ""))
        if items:
            return items
        return local_fallback()
    except Exception:
        return local_fallback()
