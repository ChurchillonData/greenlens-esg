import json

# Materiality multipliers by claim category.
# High-materiality claims (net_zero, scope_3) get harder scrutiny — the same
# base evidence signal is more alarming when the claim touches the company's
# core climate commitment rather than an operational detail.
MATERIALITY = {
    "net_zero":              1.35,
    "scope_3":               1.30,
    "climate_lobbying":      1.25,
    "methane":               1.20,
    "emissions_reduction":   1.15,
    "renewables_investment": 1.10,
    "biodiversity":          1.05,
    "just_transition":       1.00,
    "other":                 1.00,
}

rows = [json.loads(l) for l in open('data/outputs/rationales.jsonl', encoding='utf-8') if l.strip()]

seen = set()
out = []
for r in rows:
    ct = r['claim_text']
    if ct not in seen:
        seen.add(ct)
        evidence = [
            {
                'source': e.get('source', ''),
                'source_credibility': e.get('source_credibility', 0.0),
                'url': e.get('url', ''),
                'date': e.get('date', ''),
                'text': e['text'][:300].strip(),
            }
            for e in r.get('evidence', [])[:5]
        ]
        category = r['category']
        base_score = r['predicted']['risk_score']
        multiplier = MATERIALITY.get(category, 1.0)
        green_signal = round(min(1.0, base_score * multiplier), 4)

        out.append({
            'company_id':           r['company_id'],
            'page':                 r.get('page'),
            'category':             category,
            'claim_text':           ct,
            'scope':                r.get('scope', ''),
            'deadline_year':        r.get('deadline_year'),
            'target_value':         r.get('target_value'),
            'target_unit':          r.get('target_unit', ''),
            'predicted_class':      r['predicted']['class'],
            'risk_score':           green_signal,
            'materiality_weight':   multiplier,
            'reasoning':            r['predicted']['reasoning'],
            'rationale':            r['rationale']['rationale'],
            'key_factors':          r['rationale']['key_factors'],
            'decision_trace':       r['rationale'].get('decision_trace', []),
            'evidence':             evidence,
        })

with open('frontend/src/data/rationales.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print(f'Written {len(out)} records')
cats = {}
for r in out:
    cats.setdefault(r['category'], []).append(r['risk_score'])
for cat, scores in sorted(cats.items()):
    avg = sum(scores) / len(scores)
    print(f'  {cat:25} n={len(scores):3}  avg_signal={avg:.3f}  multiplier={MATERIALITY.get(cat,1.0)}')
