import pathlib, re
root = pathlib.Path(r"c:\Users\kiban\Desktop\Projects\Programmation\Oxiliere\oxiliere_hr\frontend\src")
count=0
for p in root.rglob("*"):
    if not p.is_file(): continue
    if p.suffix not in (".ts",".svelte",".js"): continue
    # skip node_modules etc not in src
    try:
        t = p.read_text(encoding="utf-8")
    except: continue
    orig=t
    # Replace alias imports: @/features/ -> @/hr/
    # Handle both single and double quotes
    t = t.replace("@/features/", "@/hr/")
    # Also handle import '\"@/features\"' without trailing slash (unlikely but cover)
    # e.g. from '@/features' -> from '@/hr'
    # Use regex to avoid replacing api endpoints like "/features"
    t = re.sub(r"@\/features(?=['\"/])", "@/hr", t)
    if t != orig:
        p.write_text(t, encoding="utf-8")
        count+=1
        print(f"patched {p.relative_to(root)}")
print(f"total patched: {count}")
# Also check lib/hr internal - already covered
