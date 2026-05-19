from __future__ import annotations

import io
from typing import TYPE_CHECKING

from django.template.loader import render_to_string
from weasyprint import HTML

if TYPE_CHECKING:
    from apps.orders.models import Order


class InvoiceService:
    @staticmethod
    def generate_pdf(order: "Order") -> bytes:
        html_string = render_to_string("emails/invoice.html", {"order": order})
        html = HTML(string=html_string)
        pdf_file = io.BytesIO()
        html.write_pdf(pdf_file)
        return pdf_file.getvalue()

    @staticmethod
    def generate_and_store(order: "Order") -> str:
        from django.core.files.base import ContentFile
        from django.core.files.storage import default_storage
        from django.conf import settings

        pdf = InvoiceService.generate_pdf(order)
        path = f"{settings.CASSA_INVOICE_PDF_STORAGE}invoice-{order.number}.pdf"
        default_storage.save(path, ContentFile(pdf))
        return path
