import re

HIGH_KEYWORDS = [
    'zero-day', '0-day', 'zeroday',
    'actively exploited', 'exploited in the wild',
    'kev', 'known exploited',
    'critical vulnerability', 'critical exploit',
    'ransomware', 'nation-state',
]

def classify_severity(title, summary, source, cvss_threshold=8.0):
    """
    Returns 'high' or 'normal'.
    High if: source is cisa_kev, or HIGH_KEYWORDS found in title/summary,
    or CVSS score >= threshold extracted from text.
    """
    if source == 'cisa_kev':
        return 'high'

    text = f"{title or ''} {summary or ''}".lower()

    for kw in HIGH_KEYWORDS:
        if kw in text:
            return 'high'

    # Extract CVSS score from text (e.g. "CVSS 9.8", "CVSS: 8.5", "CVSSv3 9.0")
    matches = re.findall(r'cvss\w*[\s:v]*(\d+\.?\d*)', text)
    for m in matches:
        try:
            if float(m) >= cvss_threshold:
                return 'high'
        except ValueError:
            pass

    return 'normal'
