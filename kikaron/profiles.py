#!/usr/bin/env python3
"""App Store provisioning profiles for Kikaron Multipass, via the App Store
Connect API (Xcode 27's -allowProvisioningUpdates with an API key fails with
"Authentication failed" for new profiles, so we make them ourselves).

  python3 kikaron/profiles.py KEY_ID ISSUER_ID

Finds or (re)creates one IOS_APP_STORE profile per bundle ID, signed for the
team's Apple Distribution certificate that has its private key in this Mac's
keychain, installs them where Xcode looks, and fails if a profile lacks the
app group (= the group is not assigned to that App ID in the portal).
Prints the xcconfig lines for manual signing.
"""
import base64, json, os, plistlib, subprocess, sys, time, urllib.error, urllib.request

KID, ISS = sys.argv[1], sys.argv[2]
BUNDLE = os.environ.get("BUNDLE_ID", "com.kikaron.multipass")
GROUP = "group." + BUNDLE
TARGETS = {  # bundle suffix -> xcconfig variable
    "": "PROVISIONING_PROFILE_SPECIFIER",
    ".autofill": "PROVISIONING_PROFILE_SPECIFIER_AUTOFILL_EXTENSION",
    ".share-extension": "PROVISIONING_PROFILE_SPECIFIER_SHARE_EXTENSION",
    ".find-login-action-extension": "PROVISIONING_PROFILE_SPECIFIER_ACTION_EXTENSION",
}
KEY = os.path.expanduser(f"~/.appstoreconnect/private_keys/AuthKey_{KID}.p8")
PROFILE_DIRS = [os.path.expanduser("~/Library/MobileDevice/Provisioning Profiles"),
                os.path.expanduser("~/Library/Developer/Xcode/UserData/Provisioning Profiles")]


def b64(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def token():
    hdr = b64(json.dumps({"alg": "ES256", "kid": KID, "typ": "JWT"}).encode())
    now = int(time.time())
    pl = b64(json.dumps({"iss": ISS, "iat": now, "exp": now + 1100, "aud": "appstoreconnect-v1"}).encode())
    der = subprocess.run(["openssl", "dgst", "-sha256", "-sign", KEY], input=f"{hdr}.{pl}".encode(),
                         capture_output=True, check=True).stdout
    i = 2 if der[1] < 0x80 else 2 + (der[1] & 0x7F)
    def rd(i):
        l = der[i + 1]; return der[i + 2:i + 2 + l].lstrip(b"\0").rjust(32, b"\0"), i + 2 + l
    r, i = rd(i); s, _ = rd(i)
    return f"{hdr}.{pl}.{b64(r + s)}"


TOK = token()


def api(method, path, body=None):
    req = urllib.request.Request("https://api.appstoreconnect.apple.com" + path, method=method,
                                 data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": "Bearer " + TOK, "Content-Type": "application/json"})
    try:
        raw = urllib.request.urlopen(req).read()
        return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path}: HTTP {e.code} {e.read().decode()[:500]}")


KEYCHAIN = os.path.expanduser(os.environ.get("SIGNING_KEYCHAIN",
                                             "~/Library/Keychains/kikaron-signing.keychain-db"))


def keychain_serials():
    """Serials of Apple Distribution certs whose private key is in KEYCHAIN
    (a keychain of our own, so codesign never waits on a GUI prompt)."""
    out = subprocess.run(["security", "find-certificate", "-a", "-c", "Apple Distribution", "-p", KEYCHAIN],
                         capture_output=True, text=True).stdout
    idents = subprocess.run(["security", "find-identity", "-v", "-p", "codesigning", KEYCHAIN],
                            capture_output=True, text=True).stdout
    serials = set()
    for pem in out.split("-----END CERTIFICATE-----")[:-1]:
        pem += "-----END CERTIFICATE-----\n"
        info = subprocess.run(["openssl", "x509", "-noout", "-serial", "-fingerprint", "-sha1"], input=pem,
                              capture_output=True, text=True).stdout
        serial = info.split("serial=")[1].split()[0].upper()
        sha1 = info.split("=")[-1].strip().replace(":", "").upper()
        if sha1 in idents:  # has its private key here
            serials.add(serial.lstrip("0"))
    return serials


def main():
    have = keychain_serials()
    certs = [c for c in api("GET", "/v1/certificates?filter[certificateType]=DISTRIBUTION&limit=50")["data"]
             if c["attributes"]["serialNumber"].upper().lstrip("0") in have]
    if not certs:
        sys.exit("no Apple Distribution certificate with a private key in this keychain")
    cert = certs[0]["id"]
    cert_der = base64.b64decode(certs[0]["attributes"]["certificateContent"])
    lines = []
    export = {}
    for suffix, var in TARGETS.items():
        ident = BUNDLE + suffix
        bids = [b for b in api("GET", f"/v1/bundleIds?filter[identifier]={ident}")["data"]
                if b["attributes"]["identifier"] == ident]
        if not bids:
            sys.exit(f"bundle ID {ident} is not registered")
        bid = bids[0]["id"]
        name = f"Kikaron Multipass{suffix or ' app'} App Store"
        raw = None
        for p in api("GET", f"/v1/profiles?filter[name]={urllib.parse.quote(name)}")["data"]:
            content = base64.b64decode(p["attributes"]["profileContent"])
            pinfo = plistlib.loads(subprocess.run(["security", "cms", "-D"], input=content,
                                                  capture_output=True).stdout)
            ok = (p["attributes"]["profileState"] == "ACTIVE"
                  and GROUP in pinfo["Entitlements"].get("com.apple.security.application-groups", [])
                  and cert_der in pinfo.get("DeveloperCertificates", []))
            if ok and raw is None:
                raw = content
            else:  # stale (e.g. made before the group was assigned): regenerate
                api("DELETE", f"/v1/profiles/{p['id']}")
        if raw is None:
            r = api("POST", "/v1/profiles", {"data": {"type": "profiles",
                "attributes": {"name": name, "profileType": "IOS_APP_STORE"},
                "relationships": {"bundleId": {"data": {"type": "bundleIds", "id": bid}},
                                  "certificates": {"data": [{"type": "certificates", "id": cert}]}}}})
            raw = base64.b64decode(r["data"]["attributes"]["profileContent"])
        info = plistlib.loads(subprocess.run(["security", "cms", "-D"], input=raw, capture_output=True).stdout)
        if GROUP not in info["Entitlements"].get("com.apple.security.application-groups", []):
            sys.exit(f"{ident}: profile has no {GROUP} - assign the App Group to this App ID in the "
                     "developer portal (Identifiers > App Groups), then re-run")
        for d in PROFILE_DIRS:
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, info["UUID"] + ".mobileprovision"), "wb") as fh:
                fh.write(raw)
        lines.append(f"{var} = {name}")
        export[ident] = name
        print(f"{ident}: {name} ({info['UUID']})", file=sys.stderr)
    print("\n".join(lines))
    out = os.environ.get("EXPORT_OPTIONS_DIR")
    if out:  # export options for manual signing: upload, and a plain IPA
        os.makedirs(out, exist_ok=True)
        for fname, dest in (("ExportOptions-upload.plist", "upload"), ("ExportOptions-ipa.plist", "export")):
            with open(os.path.join(out, fname), "wb") as fh:
                plistlib.dump({"method": "app-store-connect", "destination": dest, "teamID": "MS3X6X39RW",
                               "signingStyle": "manual", "signingCertificate": "Apple Distribution",
                               "provisioningProfiles": export, "uploadSymbols": True,
                               "manageAppVersionAndBuildNumber": False}, fh)


if __name__ == "__main__":
    import urllib.parse
    main()
