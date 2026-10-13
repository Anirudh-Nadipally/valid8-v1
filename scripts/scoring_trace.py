import json, yaml, html
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scoring_pipeline.validator import Validator
from scoring_pipeline.scorer import Scorer
ex = {"idea_core":{"problem_statement":"Founders lose good startup ideas in notes apps and never test them against real demand.","solution_description":"A validation dashboard that scores each idea, maps competitors and drafts a go-to-market plan in minutes.","target_customer":"Solo founders and student builders","value_proposition":"Opinionated scoring plus a pivot lab","competitors_mentioned":["Notion","ChatGPT"],"differentiation":"Rule-based scores with a traceable reason for every point"},
"market_classification":{"industry_vertical":"ai_ml","business_model":"freemium","target_geography":"global","customer_segment":"prosumer"},
"stage_indicators":{"development_stage":"prototype","team_size":"solo","funding_stage":"bootstrapped","has_revenue":False,"has_users":True},
"extraction_metadata":{"source_type":"form_input","extraction_confidence":"high","fields_extracted":["problem_statement","solution_description","target_customer","value_proposition"],"fields_inferred":["industry_vertical"],"extraction_notes":None}}
v = Validator().validate(ex)
r1 = Scorer("balanced").score(ex); r2 = Scorer("balanced").score(ex)
assert r1["final_score"]==r2["final_score"]
rules = yaml.safe_load(open("scoring_pipeline/rules/scoring-rules.yaml"))
desc={}
def walk(o):
    if isinstance(o,dict):
        if "id" in o: desc[o["id"]]=(o.get("description") or o.get("name") or "", o.get("points", o.get("adjustment","")))
        for x in o.values(): walk(x)
    elif isinstance(o,list):
        for x in o: walk(x)
walk(rules)
print(json.dumps({"valid":v.get("is_valid", v.get("valid")),"final":r1["final_score"],"grade":r1["grade"]}))
rows=""
for d,s in r1["dimension_scores"].items():
    rl="<br>".join(f"<code>{x}</code> {html.escape(str(desc.get(x,('',''))[0]))}" for x in s["rules_triggered"]) or "<span class=m>base score, no rule fired</span>"
    rows+=f"<tr><td>{d.replace('_',' ')}</td><td class=n>{s['score']}</td><td class=n>{s['weight']:.2f}</td><td>{rl}</td></tr>"
page=f"""<html><head><style>body{{font-family:Inter,-apple-system,Segoe UI,sans-serif;margin:0;padding:36px;background:#0f172a;color:#e2e8f0;width:1100px}}
h1{{font-size:20px;margin:0 0 4px}} .s{{color:#94a3b8;font-size:13px;margin-bottom:20px}} table{{border-collapse:collapse;width:100%;font-size:14px}}
td,th{{text-align:left;padding:10px 12px;border-bottom:1px solid #1e293b;vertical-align:top}} th{{color:#94a3b8;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.05em}}
.n{{font-variant-numeric:tabular-nums;width:70px}} code{{background:#1e293b;color:#a5b4fc;padding:1px 6px;border-radius:4px;font-size:12px}} .m{{color:#64748b}}
.f{{margin-top:18px;font-size:16px}} .f b{{color:#a5b4fc}}</style></head><body>
<h1>Layer 3 scoring trace (no LLM)</h1><div class=s>Real output of scoring_pipeline.Scorer("balanced") on a sample extraction. Run twice, identical result.</div>
<table><tr><th>Dimension</th><th>Score</th><th>Weight</th><th>Rules fired</th></tr>{rows}</table>
<div class=f>Final score <b>{r1['final_score']}</b> · grade <b>{r1['grade']}</b> · rules version {r1.get('rules_version','')}</div></body></html>"""
open(os.devnull,"w").write(page)

for dim, s in r1["dimension_scores"].items():
    print(f"{dim:<26} {s['score']:>3}  w={s['weight']:.2f}  {', '.join(s['rules_triggered']) or '-'}")
