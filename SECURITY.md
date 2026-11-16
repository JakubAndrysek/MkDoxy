# Security policy

## Reporting a vulnerability

Please email **email@kubaandrysek.cz** with the subject `MkDoxy security report`.
This is the repository owner's published contact address. Do not post exploit
details, credentials or sensitive project data in a public issue or discussion.

Include, where possible:

- Affected MkDoxy version or commit, Python/MkDocs/Doxygen versions and platform.
- A minimal reproduction, relevant configuration and the security impact.
- Any suggested mitigation. Remove secrets and proprietary inputs from examples.

The owner will assess the report and coordinate remediation and disclosure with
the reporter. This is a volunteer-maintained project; there is no guaranteed
response or fix timeline. Please coordinate public disclosure while the report
is being assessed. Ordinary bugs without a security impact belong in GitHub
issues and should follow [CONTRIBUTING.md](CONTRIBUTING.md).

## Versions and fixes

Security fixes focus on the latest published release and the development branch.
There are no promised long-term security-maintenance branches or automatic
backports. Reports concerning older releases are welcome; remediation may require
upgrading. Compatibility with a Python version does not extend that interpreter's
upstream security support.

## Documentation build inputs

MkDoxy runs in your MkDocs build environment and invokes Doxygen. Treat project
configuration, Python plugins, custom templates and build inputs as trusted code
and data; MkDoxy is not a sandbox for untrusted repositories. Evaluate reports
involving an unexpected trust-boundary crossing privately using the contact above.
