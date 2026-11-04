# APPCELL — Product Requirements Document (PRD)

**Document version:** 0.1  
**Status:** Draft for hackathon prototype  
**Product category:** AI That Protects — Application / SDK Security  
**Platform for MVP:** Android  
**Primary users:** App developers and everyday app users  
**Working tagline:** *Every component gets only the access it needs.*

---

## 1. Executive Summary

APPCELL is a developer-integrated security layer that helps isolate third-party application components—such as analytics, advertising, crash-reporting, and other SDKs—and restricts the sensitive operations they can request.

A mobile application can contain many components supplied by different vendors. Users generally install and grant permissions to the host application, while developers may integrate third-party SDKs to provide additional functionality. APPCELL addresses the risk that a component may request or misuse capabilities beyond what it needs.

APPCELL's core approach is to:

1. Run supported third-party components in separate, permission-restricted execution cells.
2. Require sensitive operations to pass through a central **Capability Broker**.
3. Apply explicit, component-specific policies using a default-deny model.
4. Record security-relevant decisions in a privacy-conscious audit log.
5. Explain blocked or unusual behaviour to developers and, where appropriate, users.

The AI component is an assistant for explaining and prioritising suspicious behaviour. **AI does not decide whether an operation is authorised.** The deterministic policy engine and platform-enforced isolation make that decision.

### MVP boundary

The hackathon prototype will be an Android sample application that integrates APPCELL and runs purpose-built, APPCELL-compatible components in isolated services. It will demonstrate legitimate access, denied access, attempted data transfer, and audit explanations.

The MVP will **not** claim to sandbox every arbitrary, unmodified SDK inside every existing Android application. Components must be adapted to APPCELL's integration contract, or explicitly supported by a compatible isolation mechanism.

---

## 2. Problem Statement

Modern applications often include third-party SDKs for analytics, advertising, payments, crash reporting, authentication, and other features. An application may need a sensitive permission for its main functionality, but that does not mean every embedded component needs the same access.

For example:

- A photo editor needs camera access to capture a picture.
- An analytics component may need limited event counts, but not the user's contacts.
- An advertising component may need an approved network endpoint, but not unrestricted access to private files.
- A crash-reporting component may need a redacted diagnostic report, not the full contents of a user's documents.

A broad application-level permission boundary can make it difficult to distinguish which internal component initiated an operation. This can create opportunities for excessive access, accidental data exposure, or abuse by a compromised dependency.

### Core problem

**How can an application grant a capability to the feature that genuinely needs it without automatically granting the same capability to every third-party component bundled into the application?**

---

## 3. Product Vision

Make component-level security practical for ordinary app developers and understandable to end users.

APPCELL aims to provide a reusable integration layer so developers can declare what each component may do, enforce those rules at runtime, and inspect evidence of attempted policy violations.

### Product value

**For developers:** A reusable SDK, policy format, enforcement broker, and test harness for restricting third-party components.

**For everyday users:** Better protection against unnecessary access by components inside participating applications, with clearer explanations of what was blocked and why.

---

## 4. Goals and Non-Goals

### 4.1 MVP goals

- Demonstrate a host Android application containing multiple APPCELL-compatible components.
- Run each demo component in a separately isolated execution process where supported by the Android implementation.
- Prevent isolated components from directly using sensitive host-app capabilities.
- Mediate sensitive operations through a central broker.
- Apply component-specific, least-privilege policies.
- Deny unapproved operations by default.
- Show real-time allow/deny decisions in a dashboard.
- Store a local audit trail without recording raw personal data by default.
- Demonstrate repeatable attacks against a deliberately malicious test component.
- Measure enforcement accuracy, latency, and resource overhead.

### 4.2 Longer-term goals

- Provide a developer SDK and build-time policy validation.
- Support more component types and capability adapters.
- Add dependency integrity checks and signed policy bundles.
- Provide end-user permission explanations in participating apps.
- Build a standard benchmark for component-level permission abuse.
- Explore support for additional platforms after validating the Android design.

### 4.3 Non-goals for the MVP

- Guarantee that APPCELL is impossible to hack.
- Protect a device whose operating system or kernel is compromised.
- Sandbox arbitrary existing apps without developer integration.
- Automatically understand every possible behaviour of arbitrary native or managed code.
- Replace Android's permission model, application sandbox, or platform security controls.
- Detect every form of malware or every covert communication channel.
- Use an LLM as the final authority for security decisions.
- Claim that a component is safe merely because its identity or package signature is valid.

---

## 5. Target Users and Use Cases

### 5.1 App developers

**Needs:**
- Integrate third-party functionality without granting unnecessary privileges.
- Define clear permissions for each supported component.
- Inspect which component requested a sensitive operation.
- Test malicious or compromised component behaviour before release.

**Primary use case:** A developer integrates a photo-editing SDK and allows it to process an image supplied by the host app, but does not allow it to access contacts or unrestricted storage.

### 5.2 Everyday app users

**Needs:**
- Understand why an application or component requested access.
- See when APPCELL blocks an operation outside the declared policy.
- Have confidence that participating apps do not automatically share every host permission with every component.

**Primary use case:** A user sees that an analytics component attempted to access contacts, which the app's APPCELL policy does not permit.

### 5.3 Security testers

**Needs:**
- Run repeatable tests against malicious components.
- Verify that blocked operations did not reach the protected resource.
- Export evidence and compare enforcement performance across test runs.

---

## 6. Key Product Concepts

| Concept | Definition |
|---|---|
| Host application | The Android app integrating APPCELL and owning the protected resources. |
| Component | A supported third-party module or SDK integrated through the APPCELL contract. |
| Cell | The isolated execution environment in which a component runs. |
| Capability | A named operation a component may request, such as `camera.capture` or `analytics.submit_event`. |
| Capability Broker | The trusted host-side service that validates and performs approved operations. |
| Policy | The rules defining which capabilities a component may request, under what conditions, and for how long. |
| Audit event | A local record of a request and the broker's decision, without unnecessary sensitive payloads. |
| Quarantine | A state in which a component is stopped or prevented from making further broker requests. |

---

## 7. Core User Experience

### 7.1 Developer setup flow

1. Developer adds the APPCELL library to the Android project.
2. Developer identifies the supported components that should run inside APPCELL.
3. Developer provides a component manifest and capability policy.
4. APPCELL validates that each component has a declared identity and policy.
5. The application launches the component through its isolated execution service.
6. The component requests sensitive operations through the broker API.
7. The broker evaluates the request and returns an allow/deny result.
8. The developer inspects the audit log and adjusts the policy if necessary.

### 7.2 End-user flow

1. User opens a participating application.
2. APPCELL enforces the app's declared component policies in the background.
3. If an operation is denied, the app may show a concise explanation when user awareness is useful.
4. The user or developer can inspect a privacy-conscious event summary.

### 7.3 Security-event flow

1. A component requests a capability.
2. The broker identifies the calling component and validates the request structure.
3. The broker checks the component's policy, request scope, expiry, and context.
4. The broker allows, denies, or asks for user/developer approval according to policy.
5. The broker performs an allowed operation itself or returns a narrowly scoped result.
6. The broker records the decision and reason code.
7. Repeated or high-severity violations can trigger quarantine.

---

## 8. Functional Requirements

Priorities: **P0 = required for MVP**, **P1 = desirable**, **P2 = future**.

| ID | Priority | Requirement |
|---|---:|---|
| FR-01 | P0 | APPCELL shall register each supported component with a stable component ID and declared version. |
| FR-02 | P0 | APPCELL shall load supported components through a dedicated isolated execution boundary. |
| FR-03 | P0 | Each component shall have a separate capability policy. |
| FR-04 | P0 | The policy engine shall use default-deny behaviour for capabilities not explicitly granted. |
| FR-05 | P0 | Sensitive host operations shall be exposed through broker APIs rather than directly to the component. |
| FR-06 | P0 | The broker shall validate the caller identity, requested capability, policy, request scope, and expiry before acting. |
| FR-07 | P0 | The broker shall return a structured allow/deny result with a machine-readable reason code. |
| FR-08 | P0 | APPCELL shall record component ID, capability, decision, reason code, timestamp, and request ID in a local audit log. |
| FR-09 | P0 | Audit logs shall not store raw contacts, images, message contents, credentials, or other sensitive payloads by default. |
| FR-10 | P0 | The demo dashboard shall show component status and live allow/deny events. |
| FR-11 | P0 | The test harness shall include at least one benign component and one intentionally malicious component. |
| FR-12 | P0 | APPCELL shall deny malformed, expired, unknown, or unauthorised requests. |
| FR-13 | P1 | APPCELL shall support per-component rate limits for selected capabilities. |
| FR-14 | P1 | APPCELL shall support temporary user/developer approval for selected operations. |
| FR-15 | P1 | APPCELL shall quarantine a component after a configurable number of high-severity violations. |
| FR-16 | P1 | APPCELL shall provide a local export of redacted audit events for testing. |
| FR-17 | P1 | A local AI assistant shall summarise suspicious events in plain language, using broker-generated event metadata. |
| FR-18 | P2 | APPCELL shall validate signed component manifests and policy bundles during installation or update. |
| FR-19 | P2 | APPCELL shall provide a developer command-line tool for policy linting and test execution. |
| FR-20 | P2 | APPCELL shall support additional operating systems or platform-specific isolation mechanisms. |

---

## 9. Capability and Policy Model

### 9.1 Example capabilities

The MVP should support a small, explicit set of capabilities rather than a generic `access_device` permission.

| Capability | Example purpose | Suggested MVP policy |
|---|---|---|
| `analytics.submit_event` | Submit a small, predefined usage event | Allow selected analytics component; restrict fields and rate |
| `diagnostics.submit_report` | Submit a redacted crash report | Allow only redacted, schema-validated reports |
| `network.request` | Request network access through the broker | Deny by default; allow approved destinations and methods only |
| `media.process_image` | Process an image explicitly supplied by the host app | Allow only for the image object passed to the component |
| `contacts.read` | Read contact information | Deny for all demo components |
| `files.read_private` | Read private application files | Deny for all demo components |

Camera access should remain in the host app for the MVP. The host may pass a selected image or narrowly scoped media object to a component for processing. The component should not receive direct camera permission.

### 9.2 Example policy

```json
{
  "policy_version": 1,
  "component_id": "com.example.analytics",
  "component_version": "1.0.0",
  "default_decision": "DENY",
  "capabilities": {
    "analytics.submit_event": {
      "decision": "ALLOW",
      "allowed_fields": ["screen_id", "event_type"],
      "max_requests_per_minute": 30
    },
    "network.request": {
      "decision": "ALLOW",
      "allowed_hosts": ["telemetry.example.test"],
      "allowed_methods": ["POST"]
    },
    "contacts.read": {
      "decision": "DENY"
    },
    "files.read_private": {
      "decision": "DENY"
    }
  }
}
```

This is an illustrative policy format for the prototype. The implementation must validate the schema and reject unknown or ambiguous fields.

### 9.3 Policy decision rules

- **Default deny:** An unlisted capability is denied.
- **Least privilege:** Grant only the smallest capability and data scope needed.
- **Short-lived grants:** Temporary approvals have an expiry.
- **No wildcard sensitive access:** Avoid broad grants such as `all_files` or `all_network`.
- **Fail closed:** If the broker, policy store, or identity check is unavailable, sensitive requests are denied.
- **No silent privilege escalation:** A component cannot grant itself new capabilities.

---

## 10. Proposed Technical Architecture

### 10.1 High-level components

1. **Android Host App** — Owns app functionality and protected resources.
2. **APPCELL SDK** — Provides registration, policy loading, component lifecycle, and broker client APIs.
3. **Isolated Component Runner** — Executes supported components in a separately isolated Android service/process.
4. **Capability Broker** — Runs in the trusted host process and is the only path to the selected sensitive host operations.
5. **Policy Engine** — Evaluates identity, capability, scope, expiry, and context.
6. **Audit Logger** — Stores redacted security decisions locally.
7. **Developer Dashboard** — Shows component identity, permissions, event history, and test results.
8. **AI Explainer (optional P1)** — Converts structured security events into plain-language summaries; it cannot override policy decisions.

### 10.2 Request flow

```text
Third-party component
        |
        | requests a named capability over IPC
        v
APPCELL Capability Broker
        |
        v
Caller identity + request validation
        |
        v
Deterministic Policy Engine
        |
   +----+----+
   |         |
 ALLOW      DENY
   |         |
   v         v
Perform     Return denial
narrow      + reason code
operation
   |
   v
Redacted audit event
   |
   v
Developer dashboard / optional AI explanation
```

### 10.3 Android isolation approach

For the MVP, investigate Android services declared with `android:isolatedProcess="true"`. Android's service documentation states that such a service runs in a special isolated process with no permissions of its own; communication with it occurs through the service API. This is a useful basis for demonstrating a component that cannot directly use the host app's granted permissions.

Each demo component should be placed behind its own isolated service/process where supported. The host app should expose only narrow broker methods over IPC. Do not place untrusted components in the normal host process and assume that a wrapper alone creates a security boundary.

**Platform caveat:** Android platform APIs and versions vary. Confirm the exact behaviour on the target emulator/device and test the actual process identity and permission boundary. Do not build the MVP around Android's SDK Sandbox API: current Android reference documentation marks `SdkSandboxManager` deprecated at API level 37.

### 10.4 Trust boundaries

- The isolated component is treated as potentially malicious.
- The broker and policy engine are part of the trusted computing base.
- The operating system's process isolation and permission enforcement are trusted for the stated threat model.
- The AI explainer is untrusted for enforcement purposes.
- The developer's policy is trusted only to the extent that it has been reviewed and correctly deployed.

---

## 11. Security and Threat Model

### 11.1 Assets to protect

- Contacts and personal information.
- Private application files and user-selected media.
- Authentication tokens and secrets.
- App data passed between components.
- Network destinations and outbound payloads.
- Component policies and audit records.

### 11.2 Threat actors

- A malicious third-party SDK author.
- A legitimate SDK that becomes compromised after an update.
- A vulnerable or hijacked component attempting to abuse its host application's privileges.
- An attacker supplying malicious input that triggers unsafe component behaviour.
- A component attempting to misuse the broker or exploit IPC validation errors.

### 11.3 Threats and mitigations

| Threat | MVP mitigation | Residual risk |
|---|---|---|
| Component requests an undeclared capability | Default-deny policy and broker enforcement | Broker implementation bugs remain possible |
| Component tries direct access to protected Android resources | Isolated process with no permissions of its own; do not expose direct host handles | OS or platform vulnerabilities may bypass isolation |
| Component requests a broader operation than required | Narrow, typed broker APIs and parameter validation | An overly broad broker API can recreate excessive privilege |
| Component sends data to an unapproved host | Broker-mediated network requests with destination and method allowlists | Covert channels and unmediated network paths are not fully solved by the MVP |
| Replays an old approval/request | Unique request ID, expiry, and one-time-use tracking for sensitive requests | State-management bugs may weaken replay protection |
| Component impersonates another component | Bind caller identity to the registered isolated process; do not trust a caller-supplied component ID | Incorrect process-to-component mapping is a critical failure |
| Malicious or malformed IPC payload | Strict schemas, size limits, type validation, and safe error handling | Parser or deserialisation bugs remain possible |
| Broker becomes unavailable | Fail closed for sensitive operations | Availability may be reduced |
| AI explainer gives a wrong explanation | AI has no enforcement authority; display underlying reason code | A misleading summary may still confuse users |
| Audit log leaks sensitive data | Redact payloads; store metadata only by default | Metadata can still reveal usage patterns |

### 11.4 Explicit security limitations

APPCELL cannot guarantee that an application is completely secure or that a determined attacker can never bypass it. The MVP does not protect against a compromised operating system/kernel, a compromised trusted host process, physical attacks, all side channels, or every possible covert channel. A component that receives sensitive raw data can potentially misuse that data within the access it has been given. Therefore, data minimisation is as important as permission enforcement.

---

## 12. AI Integration

AI is included to make security events easier to understand, not to replace deterministic security controls.

### AI responsibilities

- Summarise a sequence of denied or unusual capability requests.
- Explain a broker reason code in plain language.
- Group related events into a possible incident for developer review.
- Suggest a least-privilege policy adjustment for human approval.

### AI restrictions

- AI cannot approve a denied operation.
- AI cannot modify policies automatically in the MVP.
- AI cannot receive raw contacts, credentials, private files, or full payloads for routine explanation.
- AI output must be labelled as an explanation or suggestion, not proof of an attack.

### Example explanation

> The analytics component attempted to read contacts. Its policy does not include `contacts.read`, so APPCELL denied the request. No contact records were returned to the component.

The dashboard must show the underlying event and reason code alongside any AI-generated explanation.

---

## 13. User Interface Requirements

### 13.1 Developer dashboard

The MVP dashboard should contain:

- Overall APPCELL status.
- List of registered components.
- Component version and isolation status.
- Allowed capabilities for each component.
- Live request feed with allow/deny decisions.
- Reason code and timestamp for each decision.
- Violation counter and quarantine status.
- A button to run the controlled attack demo.
- Export of redacted test results.

### 13.2 End-user explanation

For the MVP, a simple in-app security event panel is sufficient. It should avoid overwhelming users with every routine operation. High-severity blocked events should identify the component, the requested access, and the outcome in plain language.

---

## 14. MVP Scope and Demo Scenarios

### 14.1 Demo application

Build a sample photo-editing application with three APPCELL-compatible components:

1. **Image Processor (benign):** Processes an image explicitly passed by the host app.
2. **Analytics Component (benign):** Submits approved, minimal event metadata.
3. **Malicious Test Component:** Attempts to access contacts and submit data to an unapproved destination.

The malicious component is a controlled test module created by the team. No real user data should be collected or transmitted.

### 14.2 Demo scenarios

**Scenario A — Legitimate operation**

- User selects a test image.
- Host app passes the image to the image processor.
- The processor returns the edited result.
- APPCELL records an allowed `media.process_image` request.

**Expected result:** `ALLOW`.

**Scenario B — Unauthorised contacts access**

- Malicious component requests `contacts.read`.
- The policy engine checks the component policy.
- The capability is not granted.

**Expected result:** `DENY`; no contacts are returned.

**Scenario C — Unapproved network destination**

- Malicious component requests a broker-mediated network operation to an unapproved test host.
- The broker checks the destination and method against the component policy.

**Expected result:** `DENY`; no outbound request is made by the broker.

**Scenario D — Replayed request**

- The test harness submits the same one-time request ID a second time.

**Expected result:** The second request is rejected as a replay.

**Scenario E — Repeated violations**

- The malicious component repeatedly attempts a high-severity denied operation.
- APPCELL reaches the configured violation threshold.

**Expected result:** The component is quarantined or stopped, and the dashboard records the action.

### 14.3 Stage presentation

The strongest demonstration is a split-screen view:

- **Left:** What the component is trying to access.
- **Middle:** APPCELL's component identity and policy decision.
- **Right:** The actual result—allowed operation, denied operation, or quarantine.

Judges should be able to trigger the malicious component themselves and see the denial in real time.

---

## 15. Success Metrics and Acceptance Criteria

All values below are prototype targets to be measured, not existing performance claims.

| Metric | MVP target | Measurement method |
|---|---:|---|
| Unauthorised capability requests blocked | 100% of the defined test cases | Automated adversarial test suite |
| Valid allowed requests completed | 100% of defined benign test cases | Functional test suite |
| Replay attempts rejected | 100% of replay test cases | Replay test harness |
| Component identity correctly mapped | 100% of defined test cases | IPC identity tests |
| Sensitive payloads in routine audit logs | 0 by default | Log inspection and automated scan |
| Dashboard decision visibility | Within 1 second for demo events | End-to-end timestamp measurement |
| Broker decision overhead | Measure p50/p95; establish a target after baseline | Instrumented benchmark |
| Isolation boundary | Demonstrate that test components lack direct access to protected permissions | On-device permission and process tests |

### Release acceptance checklist

- [ ] The host app launches all demo components.
- [ ] Each component runs behind the intended isolated execution boundary.
- [ ] The team verifies the actual process identity and permission state on the target device.
- [ ] Components cannot directly perform the protected operations used in the demo.
- [ ] The broker distinguishes components correctly.
- [ ] Default-deny behaviour works for unknown capabilities.
- [ ] Allowed and denied operations appear in the dashboard.
- [ ] Logs contain no raw sensitive test payloads.
- [ ] Replay tests pass.
- [ ] The malicious component can be quarantined.
- [ ] The demo works offline and does not depend on external APIs.
- [ ] Known limitations are presented honestly to judges.

---

## 16. Recommended Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Android host app | Kotlin + Android Studio | Sample application and trusted host process |
| Isolation | Android isolated services/processes | Execute supported components without their own permissions |
| IPC | Android Binder / bound service API | Component-to-broker communication |
| Policy engine | Kotlin | Deterministic capability decisions |
| Policy format | JSON with strict schema validation | Component-specific policy definitions |
| Local storage | Room / SQLite | Policies, event metadata, and test history |
| Dashboard | Native Android UI or local React dashboard | Live visualisation of decisions |
| AI explainer | Optional local model or template-based summaries | Explain structured events without controlling enforcement |
| Testing | Android instrumented tests + Kotlin/JUnit | Permission, IPC, replay, and attack tests |
| Optional analysis | Python | Benchmark analysis and charts after test runs |

### Stack recommendation

For the first working prototype, keep the security-critical path entirely in Kotlin: isolated service, broker, policy engine, and audit logger. Add a web dashboard or local AI explainer only after the enforcement path works reliably.

---

## 17. Development Plan

### Phase 1 — Threat model and baseline

- Define the protected resources and attacker capabilities.
- Build a plain Android sample app with one benign and one malicious test component.
- Record what the malicious component can do without APPCELL's brokered isolation model.

**Deliverable:** Baseline demonstration and documented threat model.

### Phase 2 — Isolation and component identity

- Implement the isolated component service.
- Register component IDs and versions.
- Verify process identity and permission boundaries on the target Android device.

**Deliverable:** A component that runs in the intended isolated process.

### Phase 3 — Capability Broker and policies

- Implement typed broker APIs.
- Add default-deny policy evaluation.
- Add validation for caller identity, request scope, expiry, and request IDs.

**Deliverable:** Enforced allow/deny decisions for the demo capabilities.

### Phase 4 — Audit, dashboard, and attack harness

- Record redacted events.
- Build the live dashboard.
- Add contacts-access, network-destination, malformed-request, and replay tests.
- Add quarantine behaviour.

**Deliverable:** Complete interactive security demonstration.

### Phase 5 — AI explanations and evaluation

- Add plain-language explanations from structured event metadata.
- Benchmark allowed and denied operations.
- Measure latency and resource overhead.
- Document false positives, false negatives, and limitations.

**Deliverable:** Final prototype, benchmark results, and limitations report.

---

## 18. Risks and Open Questions

| Risk / question | Why it matters | Proposed response |
|---|---|---|
| Existing SDKs may expect direct Android APIs | They may not work unchanged inside an isolated component | Require an adapter or APPCELL-compatible integration contract for the MVP |
| Host broker becomes a high-value target | A broker flaw can undermine the whole design | Keep APIs small, validate every argument, minimise trusted code, and test aggressively |
| Components share an isolation boundary | One component could affect another if they share a process | Use a separate isolated process per component for the demo where feasible |
| Performance overhead | IPC and policy checks add latency | Benchmark representative requests and keep broker APIs coarse enough to avoid excessive IPC |
| Policy mistakes | Overly broad policies can nullify protection | Default deny, policy linting, clear capability names, and human review |
| Data is passed into a component | A component can misuse information it legitimately receives | Minimise data, pass handles or scoped objects where possible, and avoid passing secrets |
| Platform compatibility | Android behaviour differs by version/device | Select and test a defined Android API range; disclose compatibility limits |
| Users may misunderstand AI explanations | A confident summary can be mistaken for proof | Display deterministic reason codes and raw event metadata alongside explanations |

### Open questions before implementation

1. Which Android API level and physical device will be used for the final demonstration?
2. Will the MVP use one isolated process per component, or a smaller number of isolated processes with clearly documented separation limits?
3. Which two or three broker capabilities can be implemented and tested end to end within the available time?
4. Will the dashboard be native Android UI or a local web interface?
5. Is a local AI model feasible on the demo hardware, or should the first release use deterministic explanation templates?

---

## 19. Research and Differentiation Hypothesis

APPCELL should not claim that process isolation, Android permissions, or SDK sandboxing are inventions of this project. Those concepts and platform mechanisms already exist.

The hackathon contribution to investigate is the combination of:

- A simple developer-facing component integration contract.
- Per-component, narrowly scoped capability policies.
- A broker that mediates protected host operations.
- User/developer-visible explanations of blocked behaviour.
- A repeatable benchmark showing whether malicious components can exceed their declared capabilities.

### Research question

**Can a developer-friendly, component-level capability broker reduce the permissions and data access available to third-party application components, while keeping common component tasks functional and making violations observable?**

### Evidence required

To support this contribution, the team must show:

1. A baseline where the test component can perform an unwanted action or where the host app cannot distinguish the requesting component.
2. The APPCELL implementation and its actual isolation boundary.
3. An attack suite with reproducible attempts to exceed granted capabilities.
4. Results showing which attempts were blocked, which succeeded, and what performance overhead was introduced.
5. A clear statement of remaining limitations.

The project should describe its novelty as a **prototype and evaluated integration approach**, not as a claim that no similar security mechanism exists anywhere.

---

## 20. Final Product Definition

**APPCELL is an Android developer-integrated security layer that runs supported third-party components behind isolated execution boundaries and mediates their sensitive operations through component-specific, default-deny capability policies. It gives developers and users visibility into what components attempt to access and why those requests are allowed or blocked.**

**Tagline:** *Every component gets only the access it needs.*

---

## 21. References

1. Android Developers — [`<service>` manifest element](https://developer.android.com/guide/topics/manifest/service-element): documents `android:isolatedProcess`, including that an isolated service runs in a special process with no permissions of its own.
2. Android Developers — [`ServiceInfo`](https://developer.android.com/reference/android/content/pm/ServiceInfo): documents the isolated-process service flag.
3. Android Developers — [`SdkSandboxManager`](https://developer.android.com/reference/android/app/sdksandbox/SdkSandboxManager): API reference notes that `SdkSandboxManager` is deprecated at API level 37. APPCELL's MVP should not depend on this API without rechecking the platform's current supported alternative.

---

**End of document.**
