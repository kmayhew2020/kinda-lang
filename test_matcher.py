from kinda.grammar.matchers import match_construct

lines = [
    "kinda int repeat_count ~= 3",
    'sorta print("Hello")',
    "sometimes: x > 0",
]

for line in lines:
    key, groups = match_construct(line)
    print(f"[matcher test] '{line}' → key={key}, groups={groups}")
