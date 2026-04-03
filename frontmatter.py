def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text:
        return ({}, text)

    lines = text.split("\n")

    if not lines[0].strip() == "---":
        return ({}, text)

    metadata = {}
    content_start = len(lines)

    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            content_start = i + 1
            break

        line = lines[i].strip()
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()

    remaining = "\n".join(lines[content_start:]) if content_start < len(lines) else ""
    return (metadata, remaining)
