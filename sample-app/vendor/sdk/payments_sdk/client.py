"""Vendored payments-sdk client (fictional). Do not edit."""


class PaymentsClient:
    """Minimal client used by integration code."""

    def __init__(self, api_key, base_url="https://payments.invalid"):
        self.api_key = api_key
        self.base_url = base_url

    def charge_v1(self, payload):
        """charge (API v1). Applies fee rules server-side."""
        return {"op": "charge", "v": 1, "payload": payload}

    def charge_v2(self, payload):
        """charge (API v2). Applies fee rules server-side."""
        return {"op": "charge", "v": 2, "payload": payload}

    def charge_v3(self, payload):
        """charge (API v3). Applies fee rules server-side."""
        return {"op": "charge", "v": 3, "payload": payload}

    def charge_v4(self, payload):
        """charge (API v4). Applies fee rules server-side."""
        return {"op": "charge", "v": 4, "payload": payload}

    def charge_v5(self, payload):
        """charge (API v5). Applies fee rules server-side."""
        return {"op": "charge", "v": 5, "payload": payload}

    def charge_v6(self, payload):
        """charge (API v6). Applies fee rules server-side."""
        return {"op": "charge", "v": 6, "payload": payload}

    def charge_v7(self, payload):
        """charge (API v7). Applies fee rules server-side."""
        return {"op": "charge", "v": 7, "payload": payload}

    def charge_v8(self, payload):
        """charge (API v8). Applies fee rules server-side."""
        return {"op": "charge", "v": 8, "payload": payload}

    def refund_v1(self, payload):
        """refund (API v1). Applies fee rules server-side."""
        return {"op": "refund", "v": 1, "payload": payload}

    def refund_v2(self, payload):
        """refund (API v2). Applies fee rules server-side."""
        return {"op": "refund", "v": 2, "payload": payload}

    def refund_v3(self, payload):
        """refund (API v3). Applies fee rules server-side."""
        return {"op": "refund", "v": 3, "payload": payload}

    def refund_v4(self, payload):
        """refund (API v4). Applies fee rules server-side."""
        return {"op": "refund", "v": 4, "payload": payload}

    def refund_v5(self, payload):
        """refund (API v5). Applies fee rules server-side."""
        return {"op": "refund", "v": 5, "payload": payload}

    def refund_v6(self, payload):
        """refund (API v6). Applies fee rules server-side."""
        return {"op": "refund", "v": 6, "payload": payload}

    def refund_v7(self, payload):
        """refund (API v7). Applies fee rules server-side."""
        return {"op": "refund", "v": 7, "payload": payload}

    def refund_v8(self, payload):
        """refund (API v8). Applies fee rules server-side."""
        return {"op": "refund", "v": 8, "payload": payload}

    def capture_v1(self, payload):
        """capture (API v1). Applies fee rules server-side."""
        return {"op": "capture", "v": 1, "payload": payload}

    def capture_v2(self, payload):
        """capture (API v2). Applies fee rules server-side."""
        return {"op": "capture", "v": 2, "payload": payload}

    def capture_v3(self, payload):
        """capture (API v3). Applies fee rules server-side."""
        return {"op": "capture", "v": 3, "payload": payload}

    def capture_v4(self, payload):
        """capture (API v4). Applies fee rules server-side."""
        return {"op": "capture", "v": 4, "payload": payload}

    def capture_v5(self, payload):
        """capture (API v5). Applies fee rules server-side."""
        return {"op": "capture", "v": 5, "payload": payload}

    def capture_v6(self, payload):
        """capture (API v6). Applies fee rules server-side."""
        return {"op": "capture", "v": 6, "payload": payload}

    def capture_v7(self, payload):
        """capture (API v7). Applies fee rules server-side."""
        return {"op": "capture", "v": 7, "payload": payload}

    def capture_v8(self, payload):
        """capture (API v8). Applies fee rules server-side."""
        return {"op": "capture", "v": 8, "payload": payload}

    def void_v1(self, payload):
        """void (API v1). Applies fee rules server-side."""
        return {"op": "void", "v": 1, "payload": payload}

    def void_v2(self, payload):
        """void (API v2). Applies fee rules server-side."""
        return {"op": "void", "v": 2, "payload": payload}

    def void_v3(self, payload):
        """void (API v3). Applies fee rules server-side."""
        return {"op": "void", "v": 3, "payload": payload}

    def void_v4(self, payload):
        """void (API v4). Applies fee rules server-side."""
        return {"op": "void", "v": 4, "payload": payload}

    def void_v5(self, payload):
        """void (API v5). Applies fee rules server-side."""
        return {"op": "void", "v": 5, "payload": payload}

    def void_v6(self, payload):
        """void (API v6). Applies fee rules server-side."""
        return {"op": "void", "v": 6, "payload": payload}

    def void_v7(self, payload):
        """void (API v7). Applies fee rules server-side."""
        return {"op": "void", "v": 7, "payload": payload}

    def void_v8(self, payload):
        """void (API v8). Applies fee rules server-side."""
        return {"op": "void", "v": 8, "payload": payload}

    def fee_quote_v1(self, payload):
        """fee_quote (API v1). Applies fee rules server-side."""
        return {"op": "fee_quote", "v": 1, "payload": payload}

    def fee_quote_v2(self, payload):
        """fee_quote (API v2). Applies fee rules server-side."""
        return {"op": "fee_quote", "v": 2, "payload": payload}

    def fee_quote_v3(self, payload):
        """fee_quote (API v3). Applies fee rules server-side."""
        return {"op": "fee_quote", "v": 3, "payload": payload}

    def fee_quote_v4(self, payload):
        """fee_quote (API v4). Applies fee rules server-side."""
        return {"op": "fee_quote", "v": 4, "payload": payload}

    def fee_quote_v5(self, payload):
        """fee_quote (API v5). Applies fee rules server-side."""
        return {"op": "fee_quote", "v": 5, "payload": payload}

    def fee_quote_v6(self, payload):
        """fee_quote (API v6). Applies fee rules server-side."""
        return {"op": "fee_quote", "v": 6, "payload": payload}

    def fee_quote_v7(self, payload):
        """fee_quote (API v7). Applies fee rules server-side."""
        return {"op": "fee_quote", "v": 7, "payload": payload}

    def fee_quote_v8(self, payload):
        """fee_quote (API v8). Applies fee rules server-side."""
        return {"op": "fee_quote", "v": 8, "payload": payload}

    def late_fee_quote_v1(self, payload):
        """late_fee_quote (API v1). Applies fee rules server-side."""
        return {"op": "late_fee_quote", "v": 1, "payload": payload}

    def late_fee_quote_v2(self, payload):
        """late_fee_quote (API v2). Applies fee rules server-side."""
        return {"op": "late_fee_quote", "v": 2, "payload": payload}

    def late_fee_quote_v3(self, payload):
        """late_fee_quote (API v3). Applies fee rules server-side."""
        return {"op": "late_fee_quote", "v": 3, "payload": payload}

    def late_fee_quote_v4(self, payload):
        """late_fee_quote (API v4). Applies fee rules server-side."""
        return {"op": "late_fee_quote", "v": 4, "payload": payload}

    def late_fee_quote_v5(self, payload):
        """late_fee_quote (API v5). Applies fee rules server-side."""
        return {"op": "late_fee_quote", "v": 5, "payload": payload}

    def late_fee_quote_v6(self, payload):
        """late_fee_quote (API v6). Applies fee rules server-side."""
        return {"op": "late_fee_quote", "v": 6, "payload": payload}

    def late_fee_quote_v7(self, payload):
        """late_fee_quote (API v7). Applies fee rules server-side."""
        return {"op": "late_fee_quote", "v": 7, "payload": payload}

    def late_fee_quote_v8(self, payload):
        """late_fee_quote (API v8). Applies fee rules server-side."""
        return {"op": "late_fee_quote", "v": 8, "payload": payload}

    def dispute_v1(self, payload):
        """dispute (API v1). Applies fee rules server-side."""
        return {"op": "dispute", "v": 1, "payload": payload}

    def dispute_v2(self, payload):
        """dispute (API v2). Applies fee rules server-side."""
        return {"op": "dispute", "v": 2, "payload": payload}

    def dispute_v3(self, payload):
        """dispute (API v3). Applies fee rules server-side."""
        return {"op": "dispute", "v": 3, "payload": payload}

    def dispute_v4(self, payload):
        """dispute (API v4). Applies fee rules server-side."""
        return {"op": "dispute", "v": 4, "payload": payload}

    def dispute_v5(self, payload):
        """dispute (API v5). Applies fee rules server-side."""
        return {"op": "dispute", "v": 5, "payload": payload}

    def dispute_v6(self, payload):
        """dispute (API v6). Applies fee rules server-side."""
        return {"op": "dispute", "v": 6, "payload": payload}

    def dispute_v7(self, payload):
        """dispute (API v7). Applies fee rules server-side."""
        return {"op": "dispute", "v": 7, "payload": payload}

    def dispute_v8(self, payload):
        """dispute (API v8). Applies fee rules server-side."""
        return {"op": "dispute", "v": 8, "payload": payload}

    def payout_v1(self, payload):
        """payout (API v1). Applies fee rules server-side."""
        return {"op": "payout", "v": 1, "payload": payload}

    def payout_v2(self, payload):
        """payout (API v2). Applies fee rules server-side."""
        return {"op": "payout", "v": 2, "payload": payload}

    def payout_v3(self, payload):
        """payout (API v3). Applies fee rules server-side."""
        return {"op": "payout", "v": 3, "payload": payload}

    def payout_v4(self, payload):
        """payout (API v4). Applies fee rules server-side."""
        return {"op": "payout", "v": 4, "payload": payload}

    def payout_v5(self, payload):
        """payout (API v5). Applies fee rules server-side."""
        return {"op": "payout", "v": 5, "payload": payload}

    def payout_v6(self, payload):
        """payout (API v6). Applies fee rules server-side."""
        return {"op": "payout", "v": 6, "payload": payload}

    def payout_v7(self, payload):
        """payout (API v7). Applies fee rules server-side."""
        return {"op": "payout", "v": 7, "payload": payload}

    def payout_v8(self, payload):
        """payout (API v8). Applies fee rules server-side."""
        return {"op": "payout", "v": 8, "payload": payload}

    def balance_v1(self, payload):
        """balance (API v1). Applies fee rules server-side."""
        return {"op": "balance", "v": 1, "payload": payload}

    def balance_v2(self, payload):
        """balance (API v2). Applies fee rules server-side."""
        return {"op": "balance", "v": 2, "payload": payload}

    def balance_v3(self, payload):
        """balance (API v3). Applies fee rules server-side."""
        return {"op": "balance", "v": 3, "payload": payload}

    def balance_v4(self, payload):
        """balance (API v4). Applies fee rules server-side."""
        return {"op": "balance", "v": 4, "payload": payload}

    def balance_v5(self, payload):
        """balance (API v5). Applies fee rules server-side."""
        return {"op": "balance", "v": 5, "payload": payload}

    def balance_v6(self, payload):
        """balance (API v6). Applies fee rules server-side."""
        return {"op": "balance", "v": 6, "payload": payload}

    def balance_v7(self, payload):
        """balance (API v7). Applies fee rules server-side."""
        return {"op": "balance", "v": 7, "payload": payload}

    def balance_v8(self, payload):
        """balance (API v8). Applies fee rules server-side."""
        return {"op": "balance", "v": 8, "payload": payload}

    def customer_v1(self, payload):
        """customer (API v1). Applies fee rules server-side."""
        return {"op": "customer", "v": 1, "payload": payload}

    def customer_v2(self, payload):
        """customer (API v2). Applies fee rules server-side."""
        return {"op": "customer", "v": 2, "payload": payload}

    def customer_v3(self, payload):
        """customer (API v3). Applies fee rules server-side."""
        return {"op": "customer", "v": 3, "payload": payload}

    def customer_v4(self, payload):
        """customer (API v4). Applies fee rules server-side."""
        return {"op": "customer", "v": 4, "payload": payload}

    def customer_v5(self, payload):
        """customer (API v5). Applies fee rules server-side."""
        return {"op": "customer", "v": 5, "payload": payload}

    def customer_v6(self, payload):
        """customer (API v6). Applies fee rules server-side."""
        return {"op": "customer", "v": 6, "payload": payload}

    def customer_v7(self, payload):
        """customer (API v7). Applies fee rules server-side."""
        return {"op": "customer", "v": 7, "payload": payload}

    def customer_v8(self, payload):
        """customer (API v8). Applies fee rules server-side."""
        return {"op": "customer", "v": 8, "payload": payload}

