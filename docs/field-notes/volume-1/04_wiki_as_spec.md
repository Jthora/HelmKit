# The wiki as design specification

<!-- Source: README.md § "Note to AI assistants", docs/wiki_cache/CHANGELOG.md
     Status: stub
     TODO: explain why we treat the FusionGirl wiki as design source,
           how the wiki_sync tool keeps a local snapshot in
           docs/wiki_cache/, and how derivations in docs/derivations/
           credit primary references (Persinger, Bandyopadhyay,
           McFadden, Hameroff/Penrose) without leaning on them.
-->

The FusionGirl wiki at <https://wiki.fusiongirl.app> is the design source
for the HelmKit platform. This volume treats wiki entries as engineering
specifications, not as fiction. A local snapshot lives in
`docs/wiki_cache/` and is refreshed by [`tools/wiki_sync.py`](https://github.com/Jthora/HelmKit/blob/master/tools/wiki_sync.py).
