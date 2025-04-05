def e(text: str) -> str:
  reserved_chars = {
    '(': r'\(',
    ')': r'\)',
    '_': r'\_',
    '.': r'\.',
    '-': r'\-',
    '!': r'\!',
  }
    
  for char, escaped_char in reserved_chars.items():
    text = text.replace(char, escaped_char)
    
  return text