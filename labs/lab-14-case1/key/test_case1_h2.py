"""H2: the show_nosel feature (issue 2551121) on both menu() methods."""
import json
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from case1_cases import CASES  # noqa: E402
from case1_fixture import make_client, prop  # noqa: E402

with open(os.path.join(HERE, "goldens.json"), encoding="utf-8") as f:
    GOLD = json.load(f)
BYNAME = {c[0]: c for c in CASES}
NOSEL = re.compile(r'<option [^>]*>- no selection -</option>\n')


def without_nosel(html, recount_height):
    out, n = NOSEL.subn("", html)
    assert n <= 1
    if recount_height:  # Multilink: size = min(options, 7)
        opts = out.count("<option ")
        out = re.sub(r'size="\d+"', 'size="%d"' % min(opts, 7), out, 1)
    return out


def render(name, **extra):
    _, issue, pname, kw = BYNAME[name]
    c, ids = make_client()
    return prop(c, ids[issue], pname).menu(**dict(kw, **extra))


LINK_OFF = ["link_default", "link_value_none_issue3", "link_value_minus1",
            "link_retired_current", "link_showid", "link_size",
            "link_condition", "link_additional", "link_html_kwargs"]
ML_AUTO = ["ml_default", "ml_retired_current", "ml_value_list",
           "ml_condition", "ml_nosy_default", "ml_empty",
           "ml_value_empty_list"]
ML_FIXED = ["ml_height"]


@pytest.mark.parametrize("name", LINK_OFF)
def test_h2_link_off_omits_option(name):
    assert render(name, show_nosel=False) == without_nosel(GOLD[name], False)


@pytest.mark.parametrize("name", ML_AUTO)
def test_h2_multilink_off_omits_option_and_height(name):
    assert render(name, show_nosel=False) == without_nosel(GOLD[name], True)


@pytest.mark.parametrize("name", ML_FIXED)
def test_h2_multilink_off_keeps_explicit_height(name):
    assert render(name, show_nosel=False) == without_nosel(GOLD[name], False)


@pytest.mark.parametrize("name", [c[0] for c in CASES])
def test_h2_true_equals_default(name):
    assert render(name, show_nosel=True) == GOLD[name]


@pytest.mark.parametrize("pname,cls", [("status", "status"),
                                       ("keyword", "keyword")])
@pytest.mark.parametrize("flag", [True, False])
def test_h2_not_forwarded_to_filter(pname, cls, flag):
    c, ids = make_client()
    linkcl = c.db.getclass(cls)
    seen = []
    real = linkcl.filter

    def spy(search_matches, filterspec, *a, **k):
        seen.append(dict(filterspec or {}))
        return real(search_matches, filterspec, *a, **k)

    linkcl.filter = spy
    prop(c, ids["i1"], pname).menu(show_nosel=flag)
    assert seen, "menu() should call filter()"
    assert all("show_nosel" not in s for s in seen)
