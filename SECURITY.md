# Security

This tool does not serve HTTP. It only scrapes the LibreHardwareMonitor URL in `config.yaml` and writes a local `.prom` file.

LibreHardwareMonitor's web server usually has **no authentication**. Keep it on localhost (`127.0.0.1`). Do not bind it to the LAN.

`config.yaml` is gitignored. Do not commit it.

## Reporting a vulnerability

Please do not open a public issue.

Use [GitHub's private vulnerability reporting](https://github.com/mishelest/lhm-textfile-exporter/security/advisories/new) on this repository.
