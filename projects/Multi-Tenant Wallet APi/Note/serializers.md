## 📋 Serialization Schemas & Validation Layer (`serializers.py`)

Data typing, validation rules, structural transformations, and relational payload protections are managed via custom **Django REST Framework Serializers**.

### 🛡️ Relational Edge Validation Flow

* **Multi-Tenant Relationship Guards:** Exposing relational fields directly allows malicious parameter pollution vectors (e.g., trying to associate a wallet with another tenant's customer). To stop this, the `WalletSerializer` implements an explicit `validate_customer` validation hook that verifies the profile owner's tenant matches the caller's thread-scoped context.
* **Cross-Tenant Routing Protections:** The `TransferSerializer` intercept loop automatically parses the target destination wallet identifier (`to_wallet_id`). It validates that the receiver resource exists within the same tenant boundary before passing the payload to the service engine, blocking inter-tenant currency routing early.
* **Minor Unit Integer Controls:** Input schemas require values as strict integers (`min_value=1`). This native enforcement prevents floating-point inaccuracies or fractional parsing bugs from reaching the database ledger.
* **Schema Schema Synchronization:** The `IdempotencyKeySerializer` aligns fields with the core tracking tables (`key`, `response_status`, `response_body`), preventing serialization reflection drops.