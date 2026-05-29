import json
from collections import defaultdict

scores = [json.loads(l) for l in open('data/historical/gap_scores.jsonl', encoding='utf-8') if l.strip()]
by_co = defaultdict(lambda: defaultdict(int))
for r in scores:
    by_co[r['company_id']][r.get('verdict', '?')] += 1

for co, vc in sorted(by_co.items()):
    print(f"{co:15} rev={vc['reversed']:3}  partial={vc['partially_fulfilled']:3}  too_early={vc['too_early']:3}  fulfilled={vc['fulfilled']:2}")

print("\nFulfilled claims:")
for r in scores:
    if r.get('verdict') == 'fulfilled':
        print(f"  {r['company_id']:12} conf={r['confidence']}  {r['claim_text'][:80]}")
