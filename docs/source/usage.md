# Usage

## Running a `.knda` File

To interpret a Kinda-augmented Python file:

```bash
python -m kinda interpret your_file.py.knda
```

This will transform the file with Kinda’s fuzzy logic and output the generated Python code to stdout.

## Generating Runtime

Kinda needs a runtime to support its fuzzy behaviors. You can generate it manually:

```bash
python -m kinda generate-runtime
```

This will create a runtime directory (e.g., `kinda/langs/python/runtime/`) that gets bundled into builds.

## Using CLI Directly

The CLI also supports:

```bash
kinda interpret path/to/file.knda
kinda generate-runtime
```

(You can alias or wrap this as desired.)

## Example

```python
# test.knda
kinda int x = 10
sorta print("x is", x)

sometimes:
    sorta print("maybe it ran")
```

Run it:

```bash
python -m kinda interpret test.knda
```

Output might vary, e.g.:

```python
x ~= 9  # [print] x is 9
# [print] maybe it ran
```

## Python Version

Kinda is currently tested on Python 3.12. Other versions may work but are not officially supported (yet).
