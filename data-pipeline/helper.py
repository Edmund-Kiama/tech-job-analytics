import textwrap

def CommentPrinter(comment: str) -> None:
    message = f"""
    ===================================
    {comment}
    ====================================
    """
    print(textwrap.dedent(message).strip())
