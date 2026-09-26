# Handle availability report

Checked 2026-09-26 with unauthenticated HTTPS GET requests to each public profile URL. A public response is evidence about that URL only. It does not reserve a handle, prove ownership, or replace the platform's account-creation check.

## X

X returned profile metadata or a specific `User Profile Not Found` page, so the public result is distinguishable.

| Candidate | Public URL | Result on 2026-09-26 |
|---|---|---|
| `modelspec` | <https://x.com/modelspec> | Taken. Display name `Ayang`; joined September 2010. |
| `modelspec_dev` | <https://x.com/modelspec_dev> | No public profile found. Appears unclaimed; confirm during signup. |
| `modelspecdev` | <https://x.com/modelspecdev> | Taken. Display name `Jamie`; joined September 2026. Jamie must confirm that this is the intended account. |
| `modelspecai` | <https://x.com/modelspecai> | No public profile found. Appears unclaimed; confirm during signup. |
| `modelspec_ai` | <https://x.com/modelspec_ai> | Taken by `ModelSpec.ai`. Do not use. |
| `modelspec.ai` | <https://x.com/modelspec.ai> | X handles cannot contain a period. The URL returns a not-found page. |

## Instagram

Instagram returned the same generic application shell and HTTP 200 status for every tested URL. Public HTTP cannot distinguish a profile from a missing profile. Every result is **can't tell without login**.

Tested 2026-09-26: <https://www.instagram.com/modelspec/>, <https://www.instagram.com/modelspec_dev/>, <https://www.instagram.com/modelspecdev/>, <https://www.instagram.com/modelspecai/>, <https://www.instagram.com/modelspec_ai/>, and <https://www.instagram.com/modelspec.ai/>.

## TikTok

TikTok returned the same generic application shell and HTTP 200 status for every tested URL. Public HTTP cannot distinguish a profile from a missing profile. Every result is **can't tell without login**.

Tested 2026-09-26: <https://www.tiktok.com/@modelspec>, <https://www.tiktok.com/@modelspec_dev>, <https://www.tiktok.com/@modelspecdev>, <https://www.tiktok.com/@modelspecai>, <https://www.tiktok.com/@modelspec_ai>, and <https://www.tiktok.com/@modelspec.ai>.

## LinkedIn

All tested company URLs returned HTTP 404. That means no public Page exists at the URL, but LinkedIn assigns and validates the public identifier during Page creation. Treat each result as **appears unclaimed; confirm during creation**, not as proof of availability.

Tested 2026-09-26: <https://www.linkedin.com/company/modelspec/>, <https://www.linkedin.com/company/modelspec_dev/>, <https://www.linkedin.com/company/modelspecdev/>, <https://www.linkedin.com/company/modelspecai/>, <https://www.linkedin.com/company/modelspec_ai/>, and <https://www.linkedin.com/company/modelspec.ai/>.

## Recommended handle set

Use `modelspecdev` on X, Instagram, and TikTok, and use `modelspecdev` as the LinkedIn public identifier. This set is readable, has no punctuation differences between platforms, and does not imply affiliation with the unrelated `modelspec.ai` name.

Before using this set, Jamie must confirm that <https://x.com/modelspecdev> is their account. If it is not, attempt `modelspecai` on all four platforms during the same session. Do not announce a handle until all four platforms accept the set.
