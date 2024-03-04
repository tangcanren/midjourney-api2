filename = "banned_words.txt"
BANNED_PROMPT = set()
with open(filename, "r") as r:
  for line in r.readlines():
    BANNED_PROMPT.add(line.strip())
