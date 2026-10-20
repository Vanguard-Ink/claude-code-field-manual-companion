"""Write goldens.json from the PINNED tree. Run once, from the Roundup root:
    python3 <key>/make_goldens.py <key>/goldens.json"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())
from case1_cases import CASES  # noqa: E402
from case1_fixture import make_client, prop  # noqa: E402

out = {}
for name, issue, pname, kw in CASES:
    c, ids = make_client()
    out[name] = prop(c, ids[issue], pname).menu(**kw)
# not-editable path renders plain()
c, ids = make_client()
p = prop(c, ids["i1"], "status")
p.is_edit_ok = lambda: False
out["link_not_editable"] = p.menu()
p = prop(c, ids["i1"], "keyword")
p.is_edit_ok = lambda: False
out["ml_not_editable"] = p.menu()
with open(sys.argv[1], "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, sort_keys=True)
print(len(out), "goldens")
