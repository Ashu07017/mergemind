def split_diff_by_file(diff: str) -> list[dict]:
    """
    Splits a unified diff into per-file chunks.
    Returns a list of dicts: [{"filename": "auth.py", "content": "diff --git ..."}]
    """
    if not diff or not diff.strip():
        return []

    chunks = []
    current_filename = None
    current_lines = []

    for line in diff.split("\n"):
        if line.startswith("diff --git"):
            if current_filename and current_lines:
                chunks.append({
                    "filename": current_filename,
                    "content": "\n".join(current_lines)
                })
            parts = line.split(" b/")
            current_filename = parts[-1] if len(parts) > 1 else "unknown_file"
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_filename and current_lines:
        chunks.append({
            "filename": current_filename,
            "content": "\n".join(current_lines)
        })

    return chunks