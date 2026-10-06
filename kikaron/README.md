# Kikaron Multipass for iOS

**Kikaron Multipass** for iOS was developed using Bitwarden® open source software:
it is a modified version, made by Cornae (2026) for [Kikaron](https://kikaron.com),
of the [Bitwarden® iOS application](https://github.com/bitwarden/ios). It is a client
for Multipass, Kikaron's password manager, which runs on
[Vaultwarden](https://github.com/dani-garcia/vaultwarden).

Not affiliated with or endorsed by Bitwarden, Inc. Bitwarden is a trademark or
registered trademark of Bitwarden, Inc. in the United States and/or other countries;
this app does not use it as its name or logo.

## Licence

Like the app it is based on, this is free software under the
[GNU General Public License v3.0](../LICENSE.txt), WITHOUT ANY WARRANTY. The
copyright of the original code stays with its authors (© Bitwarden Inc. 2015-2026);
the changes are © Cornae 2026, under the same licence.

The Bitwarden SDK (`sdk-swift`) is dual-licensed; this app uses it under its GPL-3.0
option and includes nothing from its `bitwarden_license` (commercial-only) code.

## What was changed (and the date)

Branch `kikaron`, based on upstream tag `v2026.9.1-bwpm`, changed from 2026-10-05.
Every change is made by `kikaron/brand.py`; the branded files are its output and can
be reproduced from an upstream checkout:

- identity: bundle id `com.kikaron.multipass`, name "Kikaron Multipass"; "Bitwarden"
  as a product name replaced by "Multipass" in the app's texts (the copyright notice
  and the licence stay; Bitwarden's own products, file format, website and services
  keep their name); Dutch "hoofdwachtwoord" becomes "Multipass-wachtwoord"
- the default server is `https://multipass.kikaron.com`, signed in through Kikaron
  (single sign-on)
- a simpler unlock screen; no plan / Authenticator-sync / Apple Watch / crash-log
  settings; no links to Bitwarden's help centre, privacy policy or website
- Kikaron's icon and splash; no push, NFC, iCloud, Crashlytics
- the About screen names this as a modified version and links here

## Building and following upstream

`kikaron/brand.sh` applies the changes to an upstream checkout; `make -f
kikaron/Makefile profiles archive ipa upload` builds it (Xcode, an Apple Developer
account). To follow upstream: fetch the tags, branch from the newest `v*-bwpm`,
check out `kikaron/` from this branch, run `kikaron/brand.sh` and commit its output.
