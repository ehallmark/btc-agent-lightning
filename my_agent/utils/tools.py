from lightning_client.client import LightningClient
from langchain_core.tools import tool
import codecs


def lightning_tools(client: LightningClient):
    @tool
    def pay_invoice(payment_request: str):
        """Pay a payment request."""
        client.pay_invoice(payment_request)
        return "Payment sent."

    @tool
    def create_invoice(amount: int):
        """Create an invoice for the given amount and return the invoice payment request."""
        return client.create_invoice(amount)

    @tool
    def check_invoice_is_settled(r_hash_str: str):
        """Check if an invoice is settled."""
        r_hash = codecs.decode(r_hash_str, 'hex')
        return client.check_invoice_is_settled(r_hash)

    tools = [pay_invoice, create_invoice, check_invoice_is_settled]
    return tools