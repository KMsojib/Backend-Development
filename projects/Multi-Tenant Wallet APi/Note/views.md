## 🕹️ Interface Routing Control Layer (`views.py`)

The application exposes RESTful API access interfaces using custom-configured **Django REST Framework (DRF)** ViewSets.

### 🛡️ Defensive Controller Isolation Architecture

* **Administrative Privilege Escalation Guard:** The `?all=true` query parameter enables platform audits across tenant boundaries. To secure this surface, lookups explicitly require staff permissions (`request.user.is_staff`). Standard connections attempting to invoke the global view state are restricted to their local tenant partition.
* **Pre-Flight Scoping Verification:** State-mutating routes (`deposit`, `withdraw`, `transfer`) use `self.get_object()` to verify target assets instead of relying entirely on raw string parameter parameters. This validates that the source asset belongs to the caller's active tenant organization before invoking the backend ledger service.
* **Master Audit Timelines:** Custom pagination (`MasterAuditTimelinePagination`) fragments transaction streams, optimizing payload data transfers when loading customer financial logs.
* **Unified Error Mapping:** Exception parsing hooks intercept core database validation messages safely, converting back-end assertion failures into formatted `HTTP 400 Bad Request` payloads while avoiding server crash triggers.