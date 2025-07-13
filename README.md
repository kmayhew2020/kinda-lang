# Kinda

> A programming language for people who aren't totally sure.

**Kinda** is a fuzzy, emotionally unstable, and sometimes functional programming language.  
It’s built for developers who write code like:
> "I mean… this should work, right?"

Kinda introduces uncertainty as a first-class concept:
- `kinda int x = 5;` declares a variable with soft intent
- `sometimes (x > 3) { ... }` blocks might run. Or not.
- `x ~= x + 1;` nudges x toward a new value… sorta
- `sorta print(...)` prints. Probably.
- `maybe (cond)` adds existential dread to conditionals

---

## 🚀 Why Use Kinda?

- To test your code's resilience to randomness  
- To model uncertainty and human-like hesitation  
- To simulate moody agents or erratic systems  
- To debug real programs by writing fake ones  
- To laugh while crying during incident response

---

## 🔣 Example

```knda
kinda int x = 5;
kinda int y = 10;

sometimes (x < y) {
    sorta print("x is probably less than y");
    x ~= x + 1;
}

sorta print("final x:", x);
```

This might print:

```
x is probably less than y
final x: 6
```

Or:

```
final x: 5
```

Or nothing at all. That’s the vibe.

---

## 🧠 Philosophy

Kinda is not just a language.
It’s a reflection of:

* How humans think
* How bugs happen
* And how systems kinda sorta work until they don’t

---

## 🔧 Running Kinda Code

### 1. Clone this repo

```bash
git clone https://github.com/YOU/kinda.git
cd kinda
```

### 2. Run the interpreter

```bash
python interpreter.py example.knda
```

You’ll need Python 3.8+
No external dependencies. Just hope.

---

## 🧪 Planned Features

* `maybe` conditionals
* `meh()` functions that do nothing
* Personality modes (`--lazy`, `--anxious`, `--angry`)
* Mood-based evaluation
* Compiler messages like "You tried."

---

## 📄 License

MIT, but if it breaks everything you love, that's kinda on you.

---

## 🤝 Contributing

Pull requests welcome. Or don’t.
We’ll figure it out. Probably.

