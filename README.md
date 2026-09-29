<!--
SPDX-FileCopyrightText: © 2026 OpenCHAMI a Series of LF Projects, LLC

SPDX-License-Identifier: MIT
-->

# acme-quadlet

Podman Quadlet packaging for OpenCHAMI TLS certificate issuance with [acme.sh](https://github.com/acmesh-official/acme.sh). The RPM ships two oneshot containers — `acme-register`, which issues a certificate for the host FQDN against the cluster step-ca, and `acme-deploy`, which installs it into the `haproxy-certs` volume via acme.sh's haproxy deploy hook — along with the `acme-certs` volume, a service that trusts the cluster root CA, and a daily renewal timer. 

## Usage

```bash
make rpm-build
sudo dnf install ./dist/rpmbuild/RPMS/noarch/openchami-acme-quadlet-*.rpm
sudo systemctl daemon-reload
sudo systemctl start acme-register.service
```

The certificate FQDN defaults to the system hostname (`%H`). Override it, and any other Podman or systemd setting, with a drop-in under `/etc/containers/systemd/acme-.container.d/` — which applies to both containers — then run `systemctl daemon-reload`.

The renewal timer ships disabled. Enable it with `systemctl enable --now openchami-cert-renewal.timer`.
