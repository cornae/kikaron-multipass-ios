# Kikaron Multipass (bitwarden/ios, password manager only), built on the Mac.
#
#   make -f kikaron/Makefile brand [ICON=path.png]  apply the branding (idempotent)
#   make -f kikaron/Makefile project                 generate the Xcode projects (mint xcodegen)
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
ICON ?= kikaron/icon-concept-a.png
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

.PHONY: brand project archive ipa upload clean

brand:
	cd $(ROOT) && kikaron/brand.sh $(ICON)

project:
	cd $(ROOT) && mint run xcodegen --spec project-bwk.yml --use-cache
	cd $(ROOT) && mint run xcodegen --spec project-pm.yml --use-cache

archive: project
	rm -rf $(ARCHIVE)
	cd $(ROOT) && CI=true xcodebuild -workspace Bitwarden.xcworkspace -scheme Bitwarden \
	  -configuration Release -destination 'generic/platform=iOS' \
	  -derivedDataPath $(DERIVED) -archivePath $(ARCHIVE) \
	  CURRENT_PROJECT_VERSION=$(BUILD_NUMBER) -allowProvisioningUpdates $(ASC_AUTH) archive

ipa:
	xcodebuild -exportArchive -archivePath $(ARCHIVE) \
	  -exportOptionsPlist $(ROOT)/kikaron/ExportOptions-ipa.plist -exportPath $(DERIVED)/export-ipa \
	  -allowProvisioningUpdates $(ASC_AUTH)

upload:
	xcodebuild -exportArchive -archivePath $(ARCHIVE) \
	  -exportOptionsPlist $(ROOT)/kikaron/ExportOptions.plist -exportPath $(DERIVED)/export-upload \
	  -allowProvisioningUpdates $(ASC_AUTH)

clean:
	rm -rf $(DERIVED)
