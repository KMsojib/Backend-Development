# 💳 Multi-Tenant Wallet & Ledger Project

This is a clean, well-engineered **Multi-Tenant Wallet & Financial Ledger** project built with Django and Django REST Framework (DRF). The project is designed to showcase strong backend fundamentals—specifically focusing on **software-level multi-tenant isolation**, **atomic financial ledgers**, and **concurrency safety (locks and idempotency)**.

---

## 🚀 Key Engineering Concepts Demonstrated

### 1. Multi-Tenant Data Isolation
* **Shared-Schema Architecture:** Demonstrates how to isolate data for different business accounts (tenants) within a single database.
* **Automated Query Filtering:** Uses a custom `TenantScopedModel` and `TenantScopedManager` that automatically injects `WHERE tenant_id = active_tenant` filters into Django queries, preventing accidental cross-tenant data access.
* **Thread-Safe Context:** Implemented custom middleware utilizing thread-local storage to safely capture, bind, and clear the active tenant ID on every API request.

### 2. Concurrency & Ledger Integrity
* **Row-Level Locking:** Uses pessimistic database locking (`SELECT FOR UPDATE`) to handle concurrent balance changes safely, completely preventing race conditions (like double-spending).
* **Deadlock Prevention:** Solves database deadlocks during wallet-to-wallet transfers by dynamically sorting target UUIDs alphabetically before locking rows.
* **Audit-Safe Ledger:** Designed without a mutable "balance" column. Wallet balances are computed dynamically at runtime by summing historic transaction records (`models.Sum('amount')`), creating a 100% auditable double-entry history.

### 3. API Idempotency
* **Request Retries Protection:** Features a custom `@idempotent_endpoint` decorator that checks for unique request keys.
* **Processing Lock State:** Uses an active lock state (`102 Processing`) to immediately block simultaneous duplicate requests (e.g., from double-clicking a submit button).
* **Automatic Rollback:** Safely clears the idempotency lock if an unexpected server-side exception occurs, allowing the client to safely retry.

---

## 🛠️ System Directory Flow

├── context.py       # Thread-safe thread-local storage for the active Tenant ID
├── middleware.py    # Middleware extracting and validating X-Tenant-ID headers
├── models.py        # Abstract TenantScopedModel and relational entities (Wallet, Transaction)
├── managers.py      # Automated query-level filtering & unscoped system-level bypasses
├── services.py      # Business logic layer (Deposit, Withdraw, Transfer with Row-locking)
├── serializers.py   # Data validation, request parsing, & cross-tenant field validators
└── idempotency.py   # API decorator handling request tracking & distributed locking

---

## 📊 Database Schema Design

| Table | Purpose | Main Fields |
| :--- | :--- | :--- |
| **`Tenant`** | Defines independent business organizations. | `id` (UUID), `name`, `api_key` |
| **`Customer`** | User profiles bound to a specific tenant. | `id` (UUID), `tenant_id`, `email` |
| **`Wallet`** | Holds currency types and links to ledger entries. | `id` (UUID), `tenant_id`, `customer_id`, `currency` |
| **`Transaction`** | The immutable transaction ledger table. | `id` (UUID), `tenant_id`, `wallet_id`, `amount` (Minor Units), `type`, `reference_id` |
| **`IdempotencyKey`**| Tracks API request keys to prevent duplicate execution. | `id` (UUID), `tenant_id`, `key`, `response_status`, `response_body` |

---

## ⚙️ How to Run the Project Locally

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

## 💻 API Header Requirements

To keep queries scoped and secure, all requests must include:

| Header | Type | Description |
| :--- | :--- | :--- |
| `X-Tenant-ID` | `UUID` | **Required.** Scopes all database calls to this tenant. |
| `Idempotency-Key` | `UUID` | **Optional.** Ensures safe retries for transactional requests. |

### Example: Wallet-to-Wallet Transfer Request
**POST** `/api/wallets/transfer/`  
**Headers:**
X-Tenant-ID: d3b07384-d113-49c5-a3d8-500f40bf59df
Idempotency-Key: e136f6d6-fcf6-494b-97c7-c750b286699a
Content-Type: application/json

**Body:**
{
  "to_wallet_id": "f51b9e38-89c5-430b-9d41-382a938c642e",
  "amount": 2500,
  "description": "Invoice payment"
}
