import sys
with open('project_design.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()
with open('output.txt', 'w', encoding='utf-8') as out:
    for i, line in enumerate(lines):
        if 'folder' in line.lower() and 'structure' in line.lower():
            out.write(f"Line {i}: {line.strip()}\n")
            start = max(0, i-10)
            end = min(len(lines), i+200)
            out.write("".join(lines[start:end]))
            out.write("\n" + "="*50 + "\n")
