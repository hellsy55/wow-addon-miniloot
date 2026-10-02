# Conflict decisions

Stop on a real conflict. Identify and explain the actual incoming source: normally `upstream/master` during upstream sync, `origin/new-features` during fork-remote integration, or the specified PR during PR implementation. Identify the local branch being synchronized. Read only conflicting sections and necessary context. In Portuguese explain the practical incoming behavior, our local behavior, what incoming-only loses, what local-only loses, and whether combining preserves both. Recommend exactly one alternative when evidence suffices.

Offer: a) keep the actual incoming source version; b) keep the local version of the branch being synchronized; c) combine both, with a concrete proposal when technically possible; d) abort. Label options with the real source and local branch. Wait for the user's choice before editing or aborting. Do not show conflict markers, huge diffs, or large code blocks by default. Show code only on request or when a small excerpt is indispensable to deciding.

For a chosen abort of an active merge, use `git merge --abort`. Report clearly that this merge was not applied, distinguishing any fast-forward or commit completed before it. If no merge is active, identify the actual operation and its applicable abort procedure rather than claiming a merge was aborted. Treat abort failures as real errors.

A nontrivial decision may use exactly one read-only deep_reviewer under AGENTS.md. Its advice is not authorization.

For a, b, or c, apply only the chosen resolution, stage only relevant files, show the entire staged file list, staged stat, and COMPLETE staged diff again, and wait for explicit approval immediately before committing. Report the adopted resolution and any remaining pending work.
