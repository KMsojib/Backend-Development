# 💳 Secure Multi-Tenant Wallet & Ledger Engine

An highly secure **Multi-Tenant Wallet & Financial Ledger Engine** built with Django and Django REST Framework (DRF). This system uses a **shared-database, software-isolated** architecture to manage high-frequency ledger transactions (deposits, withdrawals, transfers) with strict isolation, double-entry audit trails, and robust concurrency controls.

---

## 🚀 Key Engineering Pillars

### 1. Bulletproof Multi-Tenant Isolation
* **Shared-Database, Shared-Schema:** All tenants share a single database to minimize hosting costs and simplify migrations, while achieving strict data isolation.
* **Automated SQL Injections:** Built a custom base `TenantScopedModel` linked to a `TenantScopedManager` that intercepts Django's query engine to automatically append `WHERE tenant_id = active_tenant` to every database query.
* **Thread-Safe Context:** Implemented custom middleware utilizing thread-local storage to securely capture and clear tenant context on every HTTP request/response cycle, preventing memory/context leaks.

### 2. Concurrency & Integrity Controls
* **Pessimistic Row-Level Locking:** Uses database-level locks (`SELECT FOR UPDATE`) to block race conditions (such as double-spending) when multiple requests hit the same wallet simultaneously.
* **Alphabetical Deadlock Prevention:** Prevents database deadlocks during multi-party transfers by sorting wallet UUIDs alphabetically before acquiring locks.
* **Immutable Double-Entry Ledger:** Avoids mutable "balance" columns. Wallet balances are dynamically calculated at runtime by summing historic ledger entries (`models.Sum('amount')`), ensuring a 100% tamper-proof audit trail.

### 3. API Idempotency (Zero Double-Charging)
* **Distributed Database Locking:** Implemented a reusable `@idempotent_endpoint` decorator utilizing a unique database constraint `(tenant_id, idempotency_key)` to guarantee that identical API retries do not execute twice.
* **Active-Lock States (`102 Processing`):** Intercepts overlapping concurrent submissions with a `409 Conflict` response if a transaction is already in flight.
* **Transient Error Recovery:** Automatically clears and deletes locks if a server-side exception occurs, allowing clients to safely retry failed requests.

---

## 🛠️ System Architecture & Directory Flow

├── context.py       # Thread-safe thread-local storage for active Tenant ID
├── middleware.py    # Middleware extracting and validating X-Tenant-ID headers
├── models.py        # Abstract TenantScopedModel and relational entities (Wallet, Transaction)
├── managers.py      # Query-level filtering & unscoped system-level access doors
├── services.py      # Transaction business engine (Deposit, Withdraw, Transfer)
├── serializers.py   # Secure data serialization, input parsing, & cross-tenant validators
└── idempotency.py   # API decorator orchestrating distributed request locks

---

## 📊 Database Schema Design

The engine is engineered around a clean relational architecture where financial ledgers are decoupled from system configurations.

| Table | Purpose | Main Fields |
| :--- | :--- | :--- |
| **`Tenant`** | Defines the independent business accounts using the platform. | `id` (UUID), `name`, `api_key` |
| **`Customer`** | Represents user accounts bound to a specific tenant. | `id` (UUID), `tenant_id`, `email`, `is_active` |
| **`Wallet`** | Holds currency types and anchors ledger histories. | `id` (UUID), `tenant_id`, `customer_id`, `currency` |
| **`Transaction`** | The immutable double-entry ledger database. | `id` (UUID), `tenant_id`, `wallet_id`, `amount` (Minor Units), `type`, `reference_id` |
| **`IdempotencyKey`**| Tracks incoming request signatures to prevent duplicate calls. | `id` (UUID), `tenant_id`, `key`, `response_status`, `response_body` |

---

## ⚙️ Core Setup & Installation

### 1. Clone & Install Dependencies
git clone https://github.com/your-username/multi-tenant-wallet-engine.git
cd multi-tenant-wallet-engine
pip install -r requirements.txt

### 2. Run Database Migrations
python manage.py makemigrations
python manage.py migrate

### 3. Start the Server
python manage.py runserver

---

## 💻 API Usage & Header Requirements

To execute any write or read operation safely, all incoming API requests must include the target **Tenant ID** and an optional **Idempotency Key** in their headers:

| Header | Type | Description |
| :--- | :--- | :--- |
| `X-Tenant-ID` | `UUID` | **Required.** Authenticates and isolates the database scope to your target organization. |
| `Idempotency-Key` | `UUID` | **Recommended.** Safely retry mutation operations (e.g., transfers) without executing them twice. |

### Example: Executing a Wallet-to-Wallet Transfer
**Request Route:** `POST /api/wallets/transfer/`  
**Headers:**
X-Tenant-ID: d3b07384-d113-49c5-a3d8-500f40bf59df
Idempotency-Key: e136f6d6-fcf6-494b-97c7-c750b286699a
Content-Type: application/json

**JSON Payload:**
{
  "to_wallet_id": "f51b9e38-89c5-430b-9d41-382a938c642e",
  "amount": 2500,
  "description": "Invoice payment"
}

---

## 🔬 Deep-Dive: Code Highlights

### Alphabetical Deadlock Prevention
During a wallet transfer, locks must always be acquired in a deterministic order to prevent concurrent threads from blocking each other:

# Sort the IDs alphabetically to guarantee lock acquisition order
id_list = [str(from_wallet_id), str(to_wallet_id)]
id_list.sort()

# Query with Row-Level write locks on the ordered IDs
locked_wallets = Wallet.unscoped_objects.select_for_update().in_bulk(id_list)
