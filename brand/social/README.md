# Social profile kit

Use these files when Jamie creates the ModelSpec profiles. The SVG files are editable sources derived from the brand 2a mark and lockup. The PNG files are upload-ready exports.

| Platform | Avatar or logo | Banner or cover |
|---|---|---|
| X | `x-avatar.png`, 400 x 400 | `x-banner.png`, 1500 x 500 |
| Instagram | `instagram-avatar.png`, 320 x 320 | No profile banner |
| TikTok | `tiktok-avatar.png`, 200 x 200 | No profile banner |
| LinkedIn Page | `linkedin-logo.png`, 400 x 400 | `linkedin-cover.png`, 1128 x 191 |

X publishes 400 x 400 and 1500 x 500 as its recommended profile dimensions. Instagram and TikTok do not have profile banners. LinkedIn's export sizes follow the current Page logo and cover specifications. Sources: [X profile help](https://help.x.com/en/managing-your-account/how-to-customize-your-profile) and [Hootsuite's current image-size guide](https://blog.hootsuite.com/social-media-image-sizes-guide/), read 2026-09-26.

The platform UI crops avatars to a circle in some views. Keep the full mark inside the canvas and do not add text to an avatar.

`profiles.json` is the single source for the site's `sameAs` URLs. Leave every value empty until Jamie creates and verifies the profile. Then enter only the handle or LinkedIn public identifier, not a full URL. An empty config emits no `sameAs` field.

Regenerate the PNG exports after changing an SVG:

```bash
for svg in brand/social/*.svg; do
  rsvg-convert --format png --output "${svg%.svg}.png" "$svg"
done
```
