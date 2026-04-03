def parse_frontmatter(text: str) -> tuple[dict, str]:
    """
    Parse YAML frontmatter from a string.

    Args:
        text: Input string that may start with YAML frontmatter

    Returns:
        Tuple of (metadata_dict, remaining_content)
    """
    if not text:
        return {}, text

    # Check if text starts with --- on its own line
    if not text.startswith("---\n"):
        return {}, text

    # Find the closing delimiter
    lines = text.split("\n")
    if len(lines) < 2:
        return {}, text  # Only opening delimiter, no content

    # Look for closing --- delimiter
    closing_index = -1
    for i in range(1, len(lines)):
        if lines[i] == "---":
            closing_index = i
            break

    # If no closing delimiter found, treat as no frontmatter
    if closing_index == -1:
        return {}, text

    # Extract frontmatter content (between delimiters)
    frontmatter_lines = lines[1:closing_index]

    # Parse key: value pairs
    metadata = {}
    for line in frontmatter_lines:
        line = line.strip()
        if not line or ":" not in line:
            continue

        # Split on first colon to handle values that might contain colons
        parts = line.split(":", 1)
        if len(parts) == 2:
            key, value = parts
            metadata[key.strip()] = value.strip()

    # Extract remaining content (after closing delimiter)
    remaining_lines = lines[closing_index + 1 :]
    remaining_content = "\n".join(remaining_lines)

    return metadata, remaining_content
