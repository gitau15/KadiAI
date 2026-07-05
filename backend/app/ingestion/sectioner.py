import re


def detect_sections(text: str) -> list[dict]:
    """
    Detect section/article/part boundaries in Kenyan legal text.
    Returns list of {type, number, title, start_pos, end_pos}.
    """
    patterns = [
        # Constitution articles: "Article 86." or "86."
        (r"(?:^|\n)\s*(?:Article\s+)?(\d{1,3})\.\s+.*", "article"),
        # Statute sections: "Section 6." or "6. (1)"
        (r"(?:^|\n)\s*(?:Section\s+)?(\d{1,3}[A-Z]?)\.\s+.*", "section"),
        # Parts: "PART II — THE EXECUTIVE"
        (r"(?:^|\n)\s*(PART\s+[IVX]+)\s*[—–-]\s*(.*)", "part"),
        # Numbered paragraphs in judgments: "[214]"
        (r"(?:^|\n)\s*\[(\d+)\]\s+.*", "paragraph"),
    ]

    sections = []
    lines = text.split("\n")

    for i, line in enumerate(lines):
        for pattern, stype in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                sections.append({
                    "type": stype,
                    "number": match.group(1),
                    "title": line.strip()[:120],
                    "line_index": i,
                })
                break

    return sections
