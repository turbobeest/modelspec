def _stream_canonical_envelope(data: bytes) -> tuple[dict[str, Any], str] | None:
    text = gzip.decompress(data).decode("utf-8")
    prefix = '{"content":'
    if not text.startswith(prefix + "{"):
        return None
    content, end = json.JSONDecoder().raw_decode(text, len(prefix))
    suffix = text[end:].lstrip()
    envelope = json.loads("{" + suffix[1:]) if suffix.startswith(",") else {}
    if "content" in envelope:
        raise ValueError("duplicate content member")
    envelope["content"] = content
    digest = hashlib.sha256()
    for offset in range(len(prefix), end, 4096):
        digest.update(text[offset:min(offset + 4096, end)].encode("utf-8"))
    return envelope, "sha256:" + digest.hexdigest()
