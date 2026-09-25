# Risk Register

| Risk | Impact | Likelihood | Mitigation | Verification method |
|---|---|---:|---|---|
| Arbitrary code execution through user input | Critical | Medium | Fixed demo project, path containment, allowlists, fixed runner arguments, no shell fragments | Security tests attempt traversal, metacharacters, and unapproved commands |
| Uploaded project executes automatically | Critical | Medium | Exclude uploads from MVP; require preconfigured controlled project | UI and integration tests verify uploads are absent/blocked |
| Suggested cause is mistaken for root cause | High | High | Evidence-first report and explicit advisory labels | Manual UI review and report assertions |
| Test process hangs | High | Medium | Hard timeout and bounded process lifecycle | Timeout integration test |
| Output leaks secrets or host details | High | Low | Synthetic data only, output bounds, filtering, review | Compliance scan and fixture tests |
| Misclassified pytest result | High | Medium | Ordered deterministic classifier and explicit categories | Classification unit matrix |
| Stale result shown as current | Medium | Medium | Isolated run IDs and reset semantics | Repeat/reset integration test |
| MVP grows beyond solo-developer capacity | High | High | Fixed exclusions and task gates | Scope review before each implementation task |
| Streamlit UI is inaccessible or confusing | Medium | Medium | Text status, labels, contrast, manual verification | Keyboard and assistive-technology-oriented review |
| Bob usage cannot be demonstrated | High | Medium | Planned evidence capture for each major task | Checklist review of sessions/screenshots |
| Dependency or environment differences change results | Medium | Medium | Record environment metadata, pin demo assumptions, state limitations | Repeated run on supported environment |
| Unsafe future AI integration | High | Medium | Keep adapter optional and unable to modify evidence or execute code | Interface and security tests |

