def parse_selection(text: str, count: int) -> list[int]:
    text = text.strip()
    if not text:
        return list(range(count))

    numbers: set[int] = set()
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            numbers.update(range(int(start), int(end) + 1))
        else:
            numbers.add(int(part))

    return sorted({n - 1 for n in numbers if 1 <= n <= count})


def select_modules(modules: list[dict]) -> list[dict]:
    print("\nAvailable modules:")
    for i, module in enumerate(modules, start=1):
        print(f"  {i}. {module['name']}")

    while True:
        raw = input(
            "\nSelect modules to download "
            "(comma-separated numbers, ranges like 1-3, blank = all): "
        )
        try:
            indices = parse_selection(raw, len(modules))
        except ValueError:
            print("Invalid input, please use numbers/ranges like: 1,3,5-7")
            continue
        if not indices:
            print("No valid module numbers in that selection, try again.")
            continue
        return [modules[i] for i in indices]
