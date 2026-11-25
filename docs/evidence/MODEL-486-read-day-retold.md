# MODEL-486-B: the read day is retold when the publish date is unchanged

The refresh rewrote `read <date>` beside the quoted publish date only when that publish date changed. A row written on day D therefore kept `read D` with `observed_at` D, and the next run on a later day with the same publish date refused it as "configuration still quotes the previous reading", for good.

The rule now: when a configuration quotes a publish date and carries `read <date>` right after it, the writer sets that day to the run's observation day whether or not the publish date changed. Nothing else in the text moves when the publish date is unchanged; the exact-snapshot sentence is still removed only when the publish date changed. A retold read day alone is counted as a re-confirmation, not a new reading.

Still refused: a text that quotes the stored `evidence_date` or `observed_at` anywhere other than that `read` clause, because the writer cannot retell it. The stale-date check is unchanged. With two `read` dates, only the one beside the publish date is retold; the other stays as written and is refused if it is a stored day.

Measured on the private data with a stand-in reading (publish date unchanged, run day after the stored read day): 11 rows retold and accepted (0 before the change); 0 other Arena rows get a different text than they have today.
