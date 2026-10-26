# Local source rollout

The 23 local publishers and communities added in hotToday are registered in
`hotrank/source_catalog.py`. The API's agent source registry and display labels
use that list. The legacy bootstrap card list also includes the same entries.

Confirm that the crawler has written snapshots for each source before registering
its public card. In the API's existing runtime, preview the merge and then apply it:

```bash
docker exec hotrank python -m hotrank.source_catalog
docker exec hotrank python -m hotrank.source_catalog --apply
```

The command appends missing cards by `tablename`, preserving current names,
metadata and order. An explicit agent allowlist is extended with the new sources;
an absent allowlist continues to use the application defaults. A watched Redis
transaction prevents concurrent catalog edits from being overwritten. Existing
registry TTLs are preserved. Applying a change saves the previous registry values
under the reported backup key for seven days and invalidates only `rank`.
Running the command again makes no changes when the sources are already present.

Restart the API after updating its Python source registry. Build the Vue app
before copying its new assets into the public root; keep previous hashed assets
available for clients with an older page open. Replace `index.html` atomically
after the assets exist. Existing feed files must remain in the public root.

Verify the public ranking endpoint contains all 23 source labels and valid story
links. Check the homepage with a fresh browser context, plus desktop and mobile
viewports in both title modes. Cards should retain vertical scrolling without
horizontal overflow, including long unbroken titles and the topic assistant button.
