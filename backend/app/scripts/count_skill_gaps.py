import pathlib, hashlib
p=pathlib.Path(__file__).parent.parent / 'data' / 'skill_gaps'
files=list(p.glob('*.json'))
hashes={}
for f in files:
    s=f.read_text(encoding='utf-8')
    h=hashlib.md5(s.encode('utf-8')).hexdigest()
    hashes.setdefault(h,[]).append(f.name)
print('total_files', len(files))
print('unique_hashes', len(hashes))
for h,fls in sorted(hashes.items(), key=lambda kv: -len(kv[1]))[:5]:
    print(len(fls), 'files ->', fls[:5])
