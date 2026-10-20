"""Shared fixture for LAB-14's hidden checks. Never copied into a workspace
except by grade.py, into a throwaway grading copy."""
from roundup import hyperdb
from roundup.anypy.cgi_ import FieldStorage
from roundup.cgi.templating import HTMLItem
from roundup.test import memorydb
from roundup.test.mocknull import MockNull as _Null


def make_client():
    memorydb.db_nuke("")
    db = memorydb.create("admin")
    # As test_templating's HTMLPropertyTestClass: a detector needs these.
    db.tx_Source = "web"
    db.issue.addprop(tx_Source=hyperdb.String())
    db.security.hasPermission = lambda *a, **k: True
    db.getuid = lambda: 10
    c = _Null()
    c.db = db
    c.form = FieldStorage()
    c.userid = "1"
    c._props = _Null()
    c.session_api = _Null(_sid="1234567890")
    # memorydb ships 8 statuses and 5 priorities; add an escaping case
    # and one status that gets retired.
    st = {n: db.status.lookup(n) for n in ("unread", "in-progress")}
    db.status.create(name="testing & <review>")
    gone = db.status.create(name="obsolete")
    kw = [db.keyword.create(name=n) for n in
          ("ui", "a-very-long-keyword-name", "db", "mail")]
    u = [db.user.create(username=n, realname=r) for n, r in
         (("ann", "Ann A"), ("bob", "Bob <B>"), ("cy", ""))]
    i1 = db.issue.create(title="one", status=st["in-progress"],
                         keyword=[kw[0], kw[2]], nosy=[u[1]],
                         priority=db.priority.lookup("bug"))
    i2 = db.issue.create(title="two", status=gone, keyword=[kw[3]])
    i3 = db.issue.create(title="three")
    db.status.retire(gone)
    retired_kw = db.keyword.create(name="old-kw")
    db.issue.set(i3, keyword=[retired_kw])
    db.keyword.retire(retired_kw)
    db.commit()
    return c, {"i1": i1, "i2": i2, "i3": i3, "kw": kw, "st": st}


def prop(client, issue, name):
    return HTMLItem(client, "issue", issue)[name]
