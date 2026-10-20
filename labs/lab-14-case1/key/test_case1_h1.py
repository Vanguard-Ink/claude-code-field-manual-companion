"""H1: default output of both menu() methods is byte-identical to goldens
rendered from the pinned code."""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from case1_cases import CASES  # noqa: E402
from case1_fixture import make_client, prop  # noqa: E402

with open(os.path.join(HERE, "goldens.json"), encoding="utf-8") as f:
    GOLD = json.load(f)


@pytest.mark.parametrize("name,issue,pname,kw", CASES,
                         ids=[c[0] for c in CASES])
def test_h1_default_output(name, issue, pname, kw):
    c, ids = make_client()
    assert prop(c, ids[issue], pname).menu(**kw) == GOLD[name]


@pytest.mark.parametrize("pname,gold", [("status", "link_not_editable"),
                                        ("keyword", "ml_not_editable")])
def test_h1_not_editable(pname, gold):
    c, ids = make_client()
    p = prop(c, ids["i1"], pname)
    p.is_edit_ok = lambda: False
    assert p.menu() == GOLD[gold]
