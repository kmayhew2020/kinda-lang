# Features

Kinda introduces fuzzy behavior into your existing codebase using playful, chaos-infused constructs.

## Constructs

- `kinda int`, `kinda float`, etc.
  - Declares a variable with a type and adds a hint of randomness.
  - Example: `kinda int x = 7` might result in `x = 6` or `x = 8`.

- `sorta print(...)`
  - Prints with probability, emphasis, or personality quirks.
  - Example: Might skip the print, or embellish it: `[print] x is probably 7`.

- `sometimes:` block
  - Executes with a tunable chance.
  - Example:
    ```python
    sometimes:
        sorta print("it worked")
    ```

## Personalities

You can configure your runtime to inject a personality into execution. A “chaotic neutral” config might add more randomness than a “lawful boring” one.

## Language Support

- ✅ Python (alpha)
- 🚧 C, JavaScript, etc. (coming soon)

## Chaos Modes

- `test` – deterministic fuzz for unit testing
- `live` – full fuzzy chaos at runtime
