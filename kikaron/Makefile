# Kikaron Multipass (bitwarden/ios, password manager only), built on the Mac.
#
#   make -f kikaron/Makefile brand [ICON=path.png]  apply the branding (idempotent)
#   make -f kikaron/Makefile project                 generate the Xcode projects (mint xcodegen)
#   make -f kikaron/Makefile profiles                App Store profiles via the API -> manual signing
#   make -f kikaron/Makefile archive                 signed Release archive
#   make -f kikaron/Makefile ipa                     archive -> signed IPA in build/export-ipa
#   make -f kikaron/Makefile upload                  archive -> App Store Connect / TestFlight
#
# The App Store Connect API key IDs come from kikaron/upload.local.mk
# (gitignored) or, failing that, the Kikaron iPhone apps' upload.local.mk:
#   ASC_KEY_ID := …
#   ASC_ISSUER_ID := …
# The .p8 lives in ~/.appstoreconnect/private_keys/, never in this repository.

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)
ICON ?= kikaron/icon.png
DERIVED := $(ROOT)/build
ARCHIVE := $(DERIVED)/Multipass.xcarchive
# Date-based, so it only ever goes up, whatever upstream tag we sit on.
BUILD_NUMBER ?= $(shell date -u +%Y%m%d.%H%M)

-include $(ROOT)/kikaron/upload.local.mk
ifeq ($(ASC_KEY_ID),)
-include $(HOME)/Sites/kikaron-app-messages-ios/upload.local.mk
endif
ASC_KEY_PATH ?= $(HOME)/.appstoreconnect/private_keys/AuthKey_$(ASC_KEY_ID).p8
ifneq ($(ASC_KEY_ID),)
ASC_AUTH := -authenticationKeyPath $(ASC_KEY_PATH) -authenticationKeyID $(ASC_KEY_ID) \
  -authenticationKeyIssuerID $(ASC_ISSUER_ID)
endif

export PATH := /opt/homebrew/bin:$(PATH)

# Manual signing uses a keychain of its own (password in a 0600 file outside
# the repo), so codesign never stops on a GUI "allow access" prompt.
SIGNING_KEYCHAIN := $(HOME)/Library/Keychains/kikaron-signing.keychain-db
SIGNING_KEYCHAIN_PASS := $(HOME)/.appstoreconnect/kikaron-signing.keychain-pass
UNLOCK := if [ -f $(SIGNING_KEYCHAIN_PASS) ]; then security unlock-keychain -p "$$(cat $(SIGNING_KEYCHAIN_PASS))" $(SIGNING_KEYCHAIN); fi

.PHONY: brand project profiles archive ipa upload clean

brand:
	cd $(ROOT) && kikaron/brand.sh $(ICON)

# Manual signing with API-made App Store profiles (Xcode 27 cannot create
# them with the API key). Remove Configs/Local-signing.xcconfig to go back
# to automatic signing.
profiles:
	cd $(ROOT) && { echo "CODE_SIGN_STYLE = Manual"; echo "CODE_SIGN_IDENTITY = Apple Distribution"; \
	  EXPORT_OPTIONS_DIR=$(DERIVED) python3 kikaron/profiles.py $(ASC_KEY_ID) $(ASC_ISSUER_ID); } > Configs/Local-signing.xcconfig.tmp \
	  && mv Configs/Local-signing.xcconfig.tmp Configs/Local-signing.xcconfig

project:
	cd $(ROOT) && mint run xcodegen --spec project-bwk.yml --use-cache
	cd $(ROOT) && mint run xcodegen --spec project-pm.yml --use-cache

archive: project
	rm -rf $(ARCHIVE)
	@$(UNLOCK)
	cd $(ROOT) && CI=true xcodebuild -workspace Bitwarden.xcworkspace -scheme Bitwarden \
	  -configuration Release -destination 'generic/platform=iOS' \
	  -derivedDataPath $(DERIVED) -archivePath $(ARCHIVE) \
	  CURRENT_PROJECT_VERSION=$(BUILD_NUMBER) -allowProvisioningUpdates $(ASC_AUTH) archive

# With manual signing (make profiles) the export options are the generated ones.
EXPORT_IPA := $(if $(wildcard $(DERIVED)/ExportOptions-ipa.plist),$(DERIVED)/ExportOptions-ipa.plist,$(ROOT)/kikaron/ExportOptions-ipa.plist)
EXPORT_UPLOAD := $(if $(wildcard $(DERIVED)/ExportOptions-upload.plist),$(DERIVED)/ExportOptions-upload.plist,$(ROOT)/kikaron/ExportOptions.plist)

ipa:
	@$(UNLOCK)
	xcodebuild -exportArchive -archivePath $(ARCHIVE) \
	  -exportOptionsPlist $(EXPORT_IPA) -exportPath $(DERIVED)/export-ipa \
	  -allowProvisioningUpdates $(ASC_AUTH)

upload:
	@$(UNLOCK)
	xcodebuild -exportArchive -archivePath $(ARCHIVE) \
	  -exportOptionsPlist $(EXPORT_UPLOAD) -exportPath $(DERIVED)/export-upload \
	  -allowProvisioningUpdates $(ASC_AUTH)

clean:
	rm -rf $(DERIVED)
