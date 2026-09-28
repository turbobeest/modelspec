# Create the ModelSpec social profiles

Jamie performs these steps. Agents prepare assets and copy but never create accounts, enter credentials, or enable account access.

Read the [handle availability report](handle-availability.md) first. Use `modelspecdev` everywhere only after confirming that the existing X profile is Jamie's. If a platform rejects the set, stop and choose one new set across all four platforms before announcing any profile.

## Before account creation

- [ ] Confirm the final shared handle set: `________________`.
- [ ] Confirm that the legal owner is `Sparks and Sawdust LLC`.
- [ ] Use `https://modelspec.dev` for every website or link-in-bio field.
- [ ] Open the upload files in `brand/social/` and the paste-ready text in `brand/social/profile-copy.md`.
- [ ] Prepare a unique password for each platform.

## X

- [ ] Create or confirm the account.
- [ ] Record the final handle: `@________________`.
- [ ] Paste the name: `ModelSpec`.
- [ ] Upload `brand/social/x-avatar.png` as the profile photo.
- [ ] Upload `brand/social/x-banner.png` as the header.
- [ ] Paste the X bio from `brand/social/profile-copy.md`.
- [ ] Paste the website: `https://modelspec.dev`.
- [ ] Leave the location and birth date blank.
- [ ] Confirm that the public URL opens while logged out.
- [ ] Enable 2FA and store the credentials in 1Password (AI-LAN vault).

## Instagram

- [ ] Create the account.
- [ ] Record the final handle: `@________________`.
- [ ] Paste the name: `ModelSpec`.
- [ ] Upload `brand/social/instagram-avatar.png` as the profile photo.
- [ ] Paste the Instagram bio from `brand/social/profile-copy.md`.
- [ ] Add the link: `https://modelspec.dev`.
- [ ] Select `Software company` if Instagram offers that category. Otherwise hide the category instead of choosing an inaccurate one.
- [ ] Leave pronouns blank.
- [ ] Confirm that the public URL opens while logged out.
- [ ] Enable 2FA and store the credentials in 1Password (AI-LAN vault).

Instagram has no profile banner.

## TikTok

- [ ] Create the account.
- [ ] Record the final handle: `@________________`.
- [ ] Paste the name: `ModelSpec`.
- [ ] Upload `brand/social/tiktok-avatar.png` as the profile photo.
- [ ] Paste the TikTok bio from `brand/social/profile-copy.md`.
- [ ] Add the website: `https://modelspec.dev`.
- [ ] Select `Software & Apps` if TikTok offers that category. Otherwise select the nearest truthful software category.
- [ ] Confirm that the public URL opens while logged out.
- [ ] Enable 2FA and store the credentials in 1Password (AI-LAN vault).

TikTok has no profile banner.

## LinkedIn company Page

- [ ] Create a company Page, not a personal profile.
- [ ] Record the final public identifier: `________________`.
- [ ] Paste the company name: `ModelSpec`.
- [ ] Paste the website: `https://modelspec.dev`.
- [ ] Paste the industry: `Software Development`.
- [ ] Select the truthful current company-size range. Do not guess.
- [ ] Select the organization type: `Privately Held`.
- [ ] Paste the tagline from `brand/social/profile-copy.md`.
- [ ] Upload `brand/social/linkedin-logo.png` as the logo.
- [ ] Upload `brand/social/linkedin-cover.png` as the cover image.
- [ ] Paste the About text from `brand/social/profile-copy.md`.
- [ ] Confirm that the Page identifies `Sparks and Sawdust LLC` as the owner or operator wherever LinkedIn provides an appropriate field.
- [ ] Confirm that the public URL opens while logged out.
- [ ] Enable 2FA and store the credentials in 1Password (AI-LAN vault).

LinkedIn applies 2FA to the administrator's account. Give Page administrator access only to named people who need it.

## Publish the identity links

- [ ] Enter each final handle or LinkedIn public identifier in `brand/social/profiles.json`. Enter handles only, not full URLs.
- [ ] Run `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_social_profiles.py`.
- [ ] Build the site and inspect the homepage JSON-LD. Confirm that `sameAs` contains only the four verified public URLs.
- [ ] Open a reviewed PR for the populated config. The empty config intentionally publishes no social URLs.
- [ ] Add the four public profile links to the first-batch campaign notes.
- [ ] Have Jamie approve the first batch. Publish each post manually under the [social playbook](playbook.md).
