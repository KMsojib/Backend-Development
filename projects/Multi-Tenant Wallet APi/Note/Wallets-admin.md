## 🎛️ Administrative Control Layer (`admin.py`)

The Django Admin interface is customized to support cross-tenant ledger auditing for platform superusers while preventing performance bottlenecks.

### 🛡️ Cross-Tenant Auditing: `TenantScopedAdminBase`
* **The Manager Override:** Because core models utilize a tenant-scoped manager by default, a standard admin panel lookup would mask records across disparate merchants. The admin interface implements a unified `TenantScopedAdminBase` class that explicitly routes queries through `unscoped_objects`. This gives global platform managers full visibility into system mechanics.
* **Audit Immutability:** Financial tracking logs (`Transaction` and `IdempotencyKey`) mark historical creation timestamps as `readonly_fields`. This safeguards systemic audit data from manual alterations inside the portal UI.

### ⚙️ Performance & Usability Configurations

1. **`CustomerAdmin` Optimization**
   * Employs `raw_id_fields = ('user',)` to replace standard relational select dropdowns with a search-popup dialog. This avoids memory exhaustion states when the system scales to thousands of distinct active users.

2. **`WalletAdmin` Live Aggregation**
   * Binds a custom `current_balance` evaluation wrapper. This securely invokes the underlying model aggregation pipeline, displaying live balances in minor units on the list overview dashboard without requiring a hardcoded balance database field.

3. **`TransactionAdmin` Tracking**
   * Exposes search fields indexed by `wallet__id` and `reference_id`. This allows rapid tracing of matching debit (`TRANSFER_OUT`) and credit (`TRANSFER_IN`) legs of internal financial movements.