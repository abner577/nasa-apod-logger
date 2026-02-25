from rich.text import Text

def build_box_lines(title: str, lines: list[str], padding_x: int = 2) -> list[str]:
    max_line_len = max((len(line) for line in lines), default=0)
    inner_width = max_line_len + (padding_x * 2)

    title_str = f" {title} "
    if len(title_str) > inner_width:
        inner_width = len(title_str)

    left_top = "┌"
    right_top = "┐"
    horiz = "─"

    remaining = inner_width - len(title_str)
    left_run = remaining // 2
    right_run = remaining - left_run
    top = f"{left_top}{horiz * left_run}{title_str}{horiz * right_run}{right_top}"

    side = "│"
    mid_lines = []
    for line in lines:
        space = inner_width - len(line)
        left_pad = " " * padding_x
        right_pad = " " * (space - padding_x) if space >= padding_x else ""
        if len(line) > inner_width:
            mid_lines.append(f"{side}{left_pad}{line}{side}")
        else:
            mid_lines.append(f"{side}{left_pad}{line}{right_pad}{side}")

    left_bot = "└"
    right_bot = "┘"
    bottom = f"{left_bot}{horiz * inner_width}{right_bot}"

    return [top] + mid_lines + [bottom]


def stylize_line(text: Text) -> None:
    s = text.plain
    if not s:
        return

    border_chars = {"┌", "┐", "└", "┘", "│", "─"}

    def is_boundary(ch: str) -> bool:
        return ch == "" or (not ch.isalnum())

    stripped = s.lstrip()
    if stripped.startswith(("┌", "└")):
        text.stylize("app.primary", 0, len(s))

        for title in (" STARTUP CHECKS: ", " QUICK INFO: ", " SETTINGS: "):
            start = s.find(title)
            if start != -1:
                text.stylize("app.primary", start, start + len(title))

    for idx, ch in enumerate(s):
        if ch in border_chars:
            text.stylize("app.primary", idx, idx + 1)
        elif ch == "✓":
            text.stylize("ok", idx, idx + 1)

    for idx, ch in enumerate(s):
        if ch != "X":
            continue

        left = s[idx - 1] if idx - 1 >= 0 else ""
        right = s[idx + 1] if idx + 1 < len(s) else ""

        if is_boundary(left) and is_boundary(right):
            text.stylize("err", idx, idx + 1)

    start = 0
    while True:
        i = s.find("/help", start)
        if i == -1:
            break
        text.stylize("app.primary", i, i + 5)
        start = i + 5