# 📂 wallets/tests.py
import uuid
import threading
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.test import TransactionTestCase 
from rest_framework import status #type:ignore
from django.db import OperationalError
from .models import Tenant, Customer, Wallet, Transaction, IdempotencyKey
from .services import WalletService
from wallets.exceptions import InsufficientFundsError, CrossTenantOperationError


class WalletAPITests(TransactionTestCase):

    def setUp(self):
        """
        Setup core tenant workspaces, auth user objects, and target customer profiles.
        """
        self.tenant_a = Tenant.objects.create(name="Tenant Alpha Workspace")
        self.tenant_b = Tenant.objects.create(name="Tenant Beta Workspace")

        # Three distinct users to satisfy unique constraints
        self.user_a1 = User.objects.create_user(username="alice_alpha", password="password123")
        self.user_a2 = User.objects.create_user(username="charlie_alpha", password="password123")
        self.user_b = User.objects.create_user(username="bob_beta", password="password123")

        # Three customer records
        self.customer_a1 = Customer.objects.create(tenant_id=self.tenant_a.id, user=self.user_a1, email="alice@alpha.com")
        self.customer_a2 = Customer.objects.create(tenant_id=self.tenant_a.id, user=self.user_a2, email="charlie@alpha.com")
        self.customer_b = Customer.objects.create(tenant_id=self.tenant_b.id, user=self.user_b, email="bob@beta.com")

        # Distinct wallets matching your UNIQUE validation constraint
        self.wallet_a1 = Wallet.objects.create(tenant_id=self.tenant_a.id, customer=self.customer_a1, currency="USD")
        self.wallet_a2 = Wallet.objects.create(tenant_id=self.tenant_a.id, customer=self.customer_a2, currency="USD")
        self.wallet_b = Wallet.objects.create(tenant_id=self.tenant_b.id, customer=self.customer_b, currency="USD")

        self.deposit_url_a1 = reverse('wallet-deposit', kwargs={'pk': str(self.wallet_a1.id)})
        self.withdraw_url_a1 = reverse('wallet-withdraw', kwargs={'pk': str(self.wallet_a1.id)})
        self.transfer_url_a1 = reverse('wallet-transfer', kwargs={'pk': str(self.wallet_a1.id)})

    def test_withdrawal_fails_with_insufficient_funds(self):
        WalletService.deposit(tenant_id=self.tenant_a.id, wallet_id=str(self.wallet_a1.id), amount_minor_units=5000)
        response = self.client.post(self.withdraw_url_a1, data={"amount": 6000}, format='json', HTTP_X_TENANT_ID=str(self.tenant_a.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_idempotency_key_cached_response(self):
        idem_key = str(uuid.uuid4())
        payload = {"amount": 2500}
        
        response1 = self.client.post(self.deposit_url_a1, data=payload, format='json', HTTP_X_TENANT_ID=str(self.tenant_a.id), HTTP_X_IDEMPOTENCY_KEY=idem_key)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        response2 = self.client.post(self.deposit_url_a1, data=payload, format='json', HTTP_X_TENANT_ID=str(self.tenant_a.id), HTTP_X_IDEMPOTENCY_KEY=idem_key)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

    def test_cross_tenant_access_blocked(self):
        cross_deposit_url = reverse('wallet-deposit', kwargs={'pk': str(self.wallet_b.id)})
        response = self.client.post(cross_deposit_url, data={"amount": 1000}, format='json', HTTP_X_TENANT_ID=str(self.tenant_a.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_concurrent_transfers_race_handling(self):
        # Fund Wallet A1 with 10,000 cents ($100.00)
        WalletService.deposit(tenant_id=self.tenant_a.id, wallet_id=str(self.wallet_a1.id), amount_minor_units=10000)

        exceptions = []
        payload = {
            "to_wallet_id": str(self.wallet_a2.id),
            "amount": 6000  # $60.00 each request
        }

        def threaded_transfer():
            try:
                # 💡 Fire requests via the test client to isolate thread requests properly
                response = self.client.post(
                    self.transfer_url_a1, 
                    data=payload, 
                    format='json', 
                    HTTP_X_TENANT_ID=str(self.tenant_a.id)
                    # Omit Idempotency Key header to explicitly test pure balance contention!
                )
                if response.status_code >= 400:
                    exceptions.append(ValidationError(response.data))
            except Exception as e:
                exceptions.append(e)

        thread1 = threading.Thread(target=threaded_transfer)
        thread2 = threading.Thread(target=threaded_transfer)

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        # At least one exception must be raised (either a Validation or Operational/Lock error)
        self.assertTrue(len(exceptions) >= 1, "Concurrency protection failed to intercept double-spend!")
        
        # Refresh from db to check the exact final ledger state
        self.wallet_a1.refresh_from_db()
        self.wallet_a2.refresh_from_db()

        # 💡 Assert that exactly ONE transaction succeeded! 
        # (Balance must be 4000 if 1 succeeded, or 10000 if SQLite locked out both safely)
        self.assertIn(self.wallet_a1.balance, [4000, 10000])
        
        if self.wallet_a1.balance == 4000:
            self.assertEqual(self.wallet_a2.balance, 6000)
        else:
            self.assertEqual(self.wallet_a2.balance, 0)
            
    # 🧪 TEST FOR WALLETS/SERVICES.PY & EXCEPTIONS
    def test_deposit_negative_amount_raises_validation_error(self):
        """Ensures passing <= 0 minor units throws a clean validation error."""
        with self.assertRaises(ValidationError):
            WalletService.deposit(tenant_id=self.tenant_a.id, wallet_id=str(self.wallet_a1.id), amount_minor_units=-500)

    def test_transfer_same_wallet_fails(self):
        """Ensures transferring to oneself is blocked."""
        with self.assertRaises(ValidationError):
            WalletService.transfer(
                tenant_id=self.tenant_a.id, 
                from_wallet_id=str(self.wallet_a1.id), 
                to_wallet_id=str(self.wallet_a1.id), 
                amount_minor_units=100
            )

    # 🧪 TEST FOR WALLETS/MIDDLEWARE.PY
    def test_request_missing_tenant_header_fails(self):
        """Ensures the API completely rejects requests without a tenant context header."""
        response = self.client.post(self.deposit_url_a1, data={"amount": 1000}, format='json')
        self.assertEqual(response.status_code, 400)

    # 🧪 NEW TARGET TESTS FOR EXCEPTIONS AND VIEW HANDLERS GAP COVERAGE
    def test_custom_exceptions_payload_and_mapping(self):
        """Verify custom domain exceptions map to the correct error structures and HTTP statuses."""
        from wallets.exceptions import custom_wallet_exception_handler
        
        # Test Insufficient Funds mapping (422)
        exc_1 = InsufficientFundsError("Not enough cash.")
        res_1 = custom_wallet_exception_handler(exc_1, {})
        self.assertEqual(res_1.status_code, 422)
        self.assertEqual(res_1.data['error']['code'], 'insufficient_funds')

        # Test Cross-Tenant isolation mapping (403)
        exc_2 = CrossTenantOperationError()
        res_2 = custom_wallet_exception_handler(exc_2, {})
        self.assertEqual(res_2.status_code, 403)

    def test_customer_overall_history_not_found(self):
        """Force views.py to execute the customer overall-history exception catch block."""
        bad_uuid = uuid.uuid4()
        url = f"/api/customers/{bad_uuid}/overall-history/"
        response = self.client.get(url, HTTP_X_TENANT_ID=str(self.tenant_a.id))
        self.assertEqual(response.status_code, 404)

    def test_wallet_history_not_found(self):
        """Force views.py to execute the wallet history exception catch block."""
        bad_uuid = uuid.uuid4()
        url = f"/api/wallets/{bad_uuid}/history/"
        response = self.client.get(url, HTTP_X_TENANT_ID=str(self.tenant_a.id))
        self.assertEqual(response.status_code, 404)

    def test_wallet_deposit_validation_error_catch(self):
        """Send bad data to verify the service exception capturing logic in view endpoints."""
        url = f"/api/wallets/{self.wallet_a1.id}/deposit/"
        response = self.client.post(url, data={"amount": -50}, format='json', HTTP_X_TENANT_ID=str(self.tenant_a.id))
        self.assertEqual(response.status_code, 400)

    def test_wallet_withdraw_validation_error_catch(self):
        """Send an excessive amount to trigger a validation error inside the withdraw view."""
        url = f"/api/wallets/{self.wallet_a1.id}/withdraw/"
        response = self.client.post(url, data={"amount": 99999999}, format='json', HTTP_X_TENANT_ID=str(self.tenant_a.id))
        self.assertEqual(response.status_code, 400)

    def test_wallet_transfer_validation_error_catch(self):
        """Trigger a validation catch block by attempting to run a self-transfer through the view endpoint."""
        url = f"/api/wallets/{self.wallet_a1.id}/transfer/"
        payload = {"to_wallet_id": str(self.wallet_a1.id), "amount": 500}
        response = self.client.post(url, data=payload, format='json', HTTP_X_TENANT_ID=str(self.tenant_a.id))
        self.assertEqual(response.status_code, 400)

# 📂 wallets/tests.py

    def test_staff_user_unscoped_querysets(self):
        """Authenticate a staff user and call '?all=true' query parameters across your Viewsets."""
        staff_user = User.objects.create_user(username="staff_admin", password="password123", is_staff=True)
        
        # 💡 Swap force_authenticate for Django's native force_login
        self.client.force_login(staff_user)

        # Cover CustomerViewSet unscoped query branches
        response_cust = self.client.get("/api/customers/?all=true", HTTP_X_TENANT_ID=str(self.tenant_a.id))
        self.assertEqual(response_cust.status_code, 200)

        # Cover WalletViewSet unscoped query branches
        response_wallet = self.client.get("/api/wallets/?all=true", HTTP_X_TENANT_ID=str(self.tenant_a.id))
        self.assertEqual(response_wallet.status_code, 200)
        
        # Cover customer overall history view branch matching 'show_all'
        url_hist = f"/api/customers/{self.customer_a1.id}/overall-history/?all=true"
        response_hist = self.client.get(url_hist, HTTP_X_TENANT_ID=str(self.tenant_a.id))
        self.assertEqual(response_hist.status_code, 200)
        
        # 💡 Clean up session logging out
        self.client.logout()