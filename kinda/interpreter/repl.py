def run_interpreter(filepath):
    print(f"[kinda::interpreter] Loading file: {filepath}")

    with open(filepath, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if line.startswith("kinda int"):
            print("[assign] kinda int detected")
            print("x ~= 5")
        elif "x ~= " in line:
            print("x ~= 5")
        elif line.startswith("sorta print"):
            print("[print] sorta print detected")
        elif line.startswith("sometimes"):
            print("[sometimes] block entered")
            print("[assign] x ~= ...")
            print("[print] sorta print inside sometimes")