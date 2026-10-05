# Kikaron Multipass (this fork)

This branch (`kikaron`) is **Kikaron Multipass**: the GPL-3.0 password-manager
app of [bitwarden/ios](https://github.com/bitwarden/ios) (based on open-source
Bitwarden code), rebranded and pointed at Kikaron's Vaultwarden server
`https://multipass.kikaron.com`. Only the `Bitwarden` (password manager)
scheme is built: no Authenticator, no watch app, no notification extension,
no Firebase/Crashlytics. The Bitwarden SDK binary (`sdk-swift`) is built from
`bitwarden-uniffi` without the `bitwarden-license` feature, i.e. used under its
GPL-3.0 option. Everything Kikaron-specific is in `kikaron/`; every other change
is the *output* of `kikaron/brand.sh` and is committed separately.

| | |
|-|-|
| Bundle IDs | `com.kikaron.multipass` (+ `.autofill`, `.share-extension`, `.find-login-action-extension`) |
| Team / app group | `MS3X6X39RW` / `group.com.kikaron.multipass` |
| Names | store / home screen "Kikaron Multipass", in the app "Multipass" |

## Moving to a new upstream tag

```bash
git fetch upstream --tags
TAG=$(git tag -l 'v*-bwpm' --sort=-v:refname | head -1)    # never -bwa
git switch -c kikaron-${TAG#v} "$TAG"
git checkout kikaron -- kikaron .gitignore                  # our scripts only
git commit -m "kikaron: scripts"
kikaron/brand.sh [path/to/icon-1024.png]                    # idempotent; fails loudly if an anchor moved
git add -A && git commit -m "kikaron: apply branding ($TAG)"
make -f kikaron/Makefile archive upload                    # needs mint (brew install mint && mint bootstrap)
```

If `brand.sh` reports an anchor that is gone, upstream moved that code: update
the exact text in `kikaron/brand.py` (never hand-edit the branded files). The
icon is any opaque 1024x1024 PNG; `python3 kikaron/icon.py concept-a OUT.png`
re-renders the placeholder. The build number is the UTC date
(`yyyymmdd.HHMM`), so it only rises whatever tag the branch sits on. The App
Store Connect API key IDs are read from `kikaron/upload.local.mk` (gitignored)
or the Kikaron iPhone apps' `upload.local.mk`.

---

<p align="center">
    <picture>
        <source media="(prefers-color-scheme: dark)" srcset=".github/images/ios-dark.png">
        <source media="(prefers-color-scheme: light)" srcset=".github/images/ios-light.png">
        <img alt="Bitwarden iOS apps screenshots." src=".github/images/ios-light.png">
    </picture>
</p>
<p align="center">
    <a href="https://github.com/bitwarden/ios/actions/workflows/ci-bwpm.yml?query=branch:main" target="_blank"><img src="https://github.com/bitwarden/ios/actions/workflows/ci-bwpm.yml/badge.svg?branch=main" alt="GitHub Workflow iOS Password Manager build on main" /></a>
    <a href="https://github.com/bitwarden/ios/actions/workflows/ci-bwa.yml?query=branch:main" target="_blank"><img src="https://github.com/bitwarden/ios/actions/workflows/ci-bwa.yml/badge.svg?branch=main" alt="GitHub Workflow iOS Authenticator build on main" /></a>
    <a href="https://github.com/bitwarden/ios/actions/workflows/test.yml?query=branch:main" target="_blank"><img src="https://github.com/bitwarden/ios/actions/workflows/test.yml/badge.svg?branch=main" alt="GitHub Workflow iOS Password Manager Test on main" /></a>
    <a href="https://github.com/bitwarden/ios/actions/workflows/test-bwa.yml?query=branch:main" target="_blank"><img src="https://github.com/bitwarden/ios/actions/workflows/test-bwa.yml/badge.svg?branch=main" alt="GitHub Workflow iOS Authenticator Test on main" /></a>
</p>

---

# Bitwarden iOS Password Manager & Authenticator Apps

Please refer to the [iOS section](https://contributing.bitwarden.com/getting-started/mobile/ios/) of the [Contributing Documentation](https://contributing.bitwarden.com/) for build instructions, recommended tooling, code style tips, and lots of other great information to get you started.

## Related projects:

- [bitwarden/server](https://github.com/bitwarden/server): The core infrastructure backend (API, database, Docker, etc).
- [bitwarden/clients](https://github.com/bitwarden/clients): Non-mobile Bitwarden Clients Applications.
- [bitwarden/directory-connector](https://github.com/bitwarden/directory-connector): A tool for syncing a directory (AD, LDAP, Azure, G Suite, Okta) to an organization.

# We're Hiring!

Interested in contributing in a big way? Consider joining our team! We're hiring for many positions. Please take a look at our [Careers page](https://bitwarden.com/careers/) to see what opportunities are [currently open](https://bitwarden.com/careers/#open-positions) as well as what it's like to work at Bitwarden.

# Contribute

Code contributions are welcome! Please commit any pull requests against the `main` branch. Learn more about how to contribute by reading the [Contributing Guidelines](https://contributing.bitwarden.com/contributing/). Check out the [Contributing Documentation](https://contributing.bitwarden.com/) for how to get started with your first contribution.

Security audits and feedback are welcome. Please open an issue or email us privately if the report is sensitive in nature. You can read our security policy in the [`SECURITY.md`](SECURITY.md) file.
