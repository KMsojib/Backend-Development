## 🏗️ Core Database Architecture (`models.py`)

The data layer is designed around an immutable ledger-based accounting system matching strict multi-tenant tenant data boundaries.

### 🏢 Multi-Tenant Architectural Pattern: `TenantScopedModel`
Rather than manually duplicating a foreign key across every database table, the project utilizes an abstract base inheritance model class: `TenantScopedModel`.
* **Dynamic Data Isolation:** Every system entity inherits from this base, locking records to a distinct `Tenant` partition automatically.
* **The Invisible Filter Guard (`TenantScopedManager`):** By routing standard lookups through a custom manager, the system implicitly injects a `WHERE tenant_id = X` clause into all Django ORM evaluations. This eliminates developer oversight, preventing cross-tenant data leaks at the database level.
* **Audit Protection (`models.PROTECT`):** To preserve complete audit trails, all relationships utilize `PROTECT` deletion behavior instead of cascade loops. Financial histories can never be retroactively modified or deleted.

### 📊 Model Index & Financial Guardrails

1. **`Tenant`**
   * Acts as the isolated corporate/organizational partition boundary. Identifiers use auto-generated `UUID` strings rather than sequential integers to obfuscate system scale from unauthorized scanning.

2. **`Customer`**
   * Proxies global Django authentication `User` instances inside specific tenant contexts.
   * **Enforced Constraint:** `unique_together = ('tenant', 'user')` ensures a single system account cannot create duplicate customer nodes under a matching merchant identity.

3. **`Wallet`**
   * Manages assets for a specific currency type.
   * **Enforced Constraint:** `unique_together = ('tenant', 'customer', 'currency')` guarantees a customer holds at most one active account ledger root per currency.
   * **Immutable Source of Truth:** Completely bypasses highly volatile, mutable database balance columns. A wallet's current balance is derived on-the-fly dynamically via an `.aggregate(models.Sum('amount'))` query tracking related transactions, making the ledger the absolute source of truth.

4. **`Transaction`**
   * Represents an unalterable point-in-time financial delta event.
   * **Strict Minor Units:** Values are explicitly stored as `IntegerField` minor units (e.g., cents, paisa). This eliminates floating-point arithmetic precision errors during fractional conversion loops.
   * **Double-Entry Transfers:** Incorporates a `reference_id` UUID token. When executing internal funds transfers, matching debit (`TRANSFER_OUT`) and credit (`TRANSFER_IN`) transactional adjustments share a singular identifier to guarantee balanced double-entry accounting audits.

5. **`IdempotencyKey`**
   * Tracks network flights to intercept and eliminate duplicate request form submits.
   * **Enforced Constraint:** `unique_together = ('tenant', 'key')` limits key unique requirements to a tenant's local horizon. This design choice prevents client token collisions across disparate businesses while fully insulating unique request tracking within the tenant scope.