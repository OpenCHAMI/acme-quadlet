# SPDX-FileCopyrightText: © 2026 OpenCHAMI a Series of LF Projects, LLC
# SPDX-License-Identifier: MIT
#
# See `make rpm-build` for the tag-to-version mapping. The packaged image is
# upstream acme.sh, so its tag is pinned in the quadlet files themselves
# rather than derived from this package's version.

Name:           openchami-acme-quadlet
Version:        %{version}
Release:        %{rel}%{?dist}
Summary:        OpenCHAMI ACME certificate Quadlet units

License:        MIT
URL:            https://github.com/OpenCHAMI/acme-quadlet
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

Requires(post,preun,postun):  systemd

# podman 5.0.0 is the first release whose Quadlet generator enables
# systemd-style *.container.d drop-in directories
Requires:                     podman >= 5.0.0

# NOTE: local-ca-quadlet provides the step-ca instance these units register
# against, and openchami-haproxy-quadlet owns the haproxy-certs volume the
# deploy hook writes into. Both are Suggests: a site may point these units at
# its own ACME server, or consume the issued certificates elsewhere.
Suggests:                     local-ca-quadlet >= 0.2.6
Suggests:                     openchami-haproxy-quadlet >= 0.0.1

%description
Podman Quadlet unit files (containers + volume) for issuing and deploying
OpenCHAMI TLS certificates with acme.sh, plus the systemd units that trust
the cluster root CA and renew the certificates on a timer.

%prep
%setup -q

%install

# systemd files
install -d %{buildroot}/usr/share/containers/systemd
for f in acme-register acme-deploy; do
    install -m 644 $f.container %{buildroot}/usr/share/containers/systemd/
done

install -d %{buildroot}/usr/share/containers/systemd/acme-.container.d
install -m 644 acme-.container.d/10-defaults-shared.conf \
    %{buildroot}/usr/share/containers/systemd/acme-.container.d/

# The shared and per-service drop-ins must not share a filename: systemd keeps
# only the highest-precedence file of a given name, so a collision would mask
# the shared one instead of layering onto it.
install -d %{buildroot}/usr/share/containers/systemd/acme-deploy.container.d
install -m 644 acme-deploy.container.d/10-defaults-service.conf \
    %{buildroot}/usr/share/containers/systemd/acme-deploy.container.d/

install -m 644 acme-certs.volume \
    %{buildroot}/usr/share/containers/systemd/acme-certs.volume

# The renewal timer ships disabled; enable it per site or via a
# meta-configuration package.
install -d %{buildroot}/usr/lib/systemd/system
install -m 644 openchami-cert-trust.service %{buildroot}/usr/lib/systemd/system/
install -m 644 openchami-cert-renewal.service %{buildroot}/usr/lib/systemd/system/
install -m 644 openchami-cert-renewal.timer %{buildroot}/usr/lib/systemd/system/

%files
%license LICENSES/MIT.txt
/usr/share/containers/systemd/acme-register.container
/usr/share/containers/systemd/acme-deploy.container
/usr/share/containers/systemd/acme-deploy.container.d
/usr/share/containers/systemd/acme-deploy.container.d/10-defaults-service.conf
/usr/share/containers/systemd/acme-.container.d
/usr/share/containers/systemd/acme-.container.d/10-defaults-shared.conf
/usr/share/containers/systemd/acme-certs.volume
/usr/lib/systemd/system/openchami-cert-trust.service
/usr/lib/systemd/system/openchami-cert-renewal.service
/usr/lib/systemd/system/openchami-cert-renewal.timer

%post
# reload systemd so the new Quadlet-generated units are seen
systemctl daemon-reload || :
if [ $1 -ge 2 ]; then
    systemctl try-restart acme-register.service || :
    systemctl try-restart acme-deploy.service || :
fi

%preun
if [ $1 -eq 0 ]; then
    systemctl stop acme-deploy.service >/dev/null 2>&1 || :
    systemctl stop acme-register.service >/dev/null 2>&1 || :
    systemctl disable --now openchami-cert-renewal.timer >/dev/null 2>&1 || :
fi

%postun
# reload systemd so the removed units are dropped
systemctl daemon-reload || :
