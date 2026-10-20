#!/bin/bash
# PreToolUse hook (LAB-11 v2, 2026-10-12): block `git commit` whose
# subject does not start with a package name. Exit 2 sends the reason back.
# v1 took the LAST -m and so blocked correct commits that carry a
# Co-Authored-By trailer as a second -m; see Chapter 12.
cmd=$(jq -r '.tool_input.command // ""')
case "$cmd" in *"git commit"*) ;; *) exit 0 ;; esac
# The subject is the FIRST -m; later ones are trailers.
subj=$(printf '%s\n' "$cmd" \
  | grep -oE -- "-m +[\"'][^\"']*" | head -n 1 \
  | sed -E "s/^-m +[\"']//")
# Heredoc form: -m "$(cat <<'EOF' ... subject on line 2.
case "$subj" in '$('*)
  subj=$(printf '%s\n' "$cmd" | sed -n '2p') ;; esac
[ -z "$subj" ] && exit 0
pkgs='^(billing|reports|shared|web): '
printf '%s' "$subj" | grep -qE "$pkgs" && exit 0
echo "Commit blocked by team hook: start the subject" \
  "with the package, e.g. 'billing: retry gateway" \
  "timeouts' (see CLAUDE.md)." >&2
exit 2
