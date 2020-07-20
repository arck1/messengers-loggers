def escape_html(text: str) -> str:
    """
    Escapes all html characters in text
    :param str text:
    :rtype: str
    """
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
