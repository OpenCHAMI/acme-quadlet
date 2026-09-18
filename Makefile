# Copyright © 2026 OpenCHAMI a Series of LF Projects, LLC
# SPDX-FileCopyrightText: © 2026 OpenCHAMI a Series of LF Projects, LLC
#
# SPDX-License-Identifier: MIT

.PHONY: help rpm-build rpm-clean

VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
# RPM version/release: strip the leading 'v' and drop git-describe's
# '-N-gHASH[-dirty]' suffix (hyphens aren't allowed in an RPM Version
# field anyway). An exact tag like v0.1.2 becomes 0.1.2.
RPM_VERSION ?= $(shell echo "$(VERSION)" | sed -e 's/^v//' -e 's/-.*//')
RPM_RELEASE ?= 1
RPM_NAME ?= openchami-acme-quadlet
RPM_TOPDIR ?= $(CURDIR)/dist/rpmbuild
RPM_SRCDIR := $(RPM_TOPDIR)/SOURCES/$(RPM_NAME)-$(RPM_VERSION)

help: ## Display this help screen
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

rpm-build: ## Build the acme quadlet RPM (VERSION/RPM_RELEASE override the derived defaults)
	@command -v rpmbuild >/dev/null 2>&1 || { echo "rpmbuild is required but not installed."; exit 1; }
	rm -rf $(RPM_TOPDIR)
	mkdir -p $(RPM_SRCDIR)/LICENSES
	cp -rL packaging/rpm-quadlet/systemd/* $(RPM_SRCDIR)/
	cp LICENSES/MIT.txt $(RPM_SRCDIR)/LICENSES/
	tar -C $(RPM_TOPDIR)/SOURCES -czf $(RPM_TOPDIR)/SOURCES/$(RPM_NAME)-$(RPM_VERSION).tar.gz \
		$(RPM_NAME)-$(RPM_VERSION)
	rpmbuild --define "_topdir $(RPM_TOPDIR)" \
		--define "version $(RPM_VERSION)" \
		--define "rel $(RPM_RELEASE)" \
		-bb packaging/rpm-quadlet/$(RPM_NAME).spec
	@echo "Built: $(RPM_TOPDIR)/RPMS/noarch/$$(ls $(RPM_TOPDIR)/RPMS/noarch)"

rpm-clean: ## Remove local RPM build artifacts
	rm -rf $(RPM_TOPDIR)

.DEFAULT_GOAL := help
