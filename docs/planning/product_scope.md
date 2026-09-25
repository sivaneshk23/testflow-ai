# Product Scope

## MVP features

1. Open one configured, controlled Python demo project.
2. Inspect project metadata and approved test files using the Python standard library `ast` module.
3. Discover only pytest tests that satisfy configured allowlist rules.
4. Let the user select approved tests or an approved test subset.
5. Execute pytest through a controlled runner with fixed arguments, timeout, working directory, and environment policy.
6. Capture structured test evidence as JSON.
7. Classify outcomes deterministically (passed, failed, skipped, collection error, timeout, or blocked).
8. Present a clear Streamlit report containing scope, timestamps, counts, evidence, and limitations.
9. Separate observed evidence from suggested explanations.
10. Demonstrate the workflow using only a self-created synthetic project.

## Explicitly excluded features

- Arbitrary user-uploaded script execution.
- Running arbitrary shell commands or user-supplied command strings.
- Remote repository cloning or automatic access to private repositories.
- Automatic code modification or commit creation.
- Production deployment or cloud execution.
- Secrets, credentials, personal data, client data, or social-media data.
- General-purpose AI coding agent behavior.
- Guaranteed root-cause diagnosis.
- Support for test frameworks other than pytest in the MVP.
- Multi-user accounts, collaboration, or persistent hosted storage.

## Future possibilities

- Additional controlled project templates.
- Read-only Git diff context.
- Pluggable deterministic failure classifiers.
- Optional local or approved AI explanation provider.
- Historical report comparison with explicit retention controls.
- Additional test frameworks after a separate security review.
- Accessibility and localization enhancements based on user testing.

## Scope limitations

The MVP supports one local, configured, controlled project at a time. The project must be synthetic or explicitly permitted, have a supported Python layout, and expose tests through the configured pytest entry point. The system reports what was observed; it does not prove why a failure occurred. Any future expansion of project or execution scope requires new requirements, threat modeling, and tests.

