import re

# Read your text file
with open("../text_files/booksAndresearches.txt", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Remove LaTeX inline ($...$), display (\[...\]), or $$...$$ blocks
text = re.sub(r"\$.*?\$|\\\[.*?\\\]|\$\$.*?\$\$", "", text, flags=re.DOTALL)

# 2. Remove inline math-like expressions (things with operators and variables/numbers)
equation_pattern = re.compile(
    r"\b(?:[A-Za-z0-9\(\)]+(?:\s*[\^=\+\*/]\s*[A-Za-z0-9\(\)]+)+)\b"
)
text = re.sub(equation_pattern, "", text)

# Save cleaned file
with open("research_cleaned.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("✅ Equations removed, saved as research_cleaned.txt")
