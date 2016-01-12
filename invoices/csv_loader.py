# -*- coding: utf-8 -*-
from flask import make_response, Response

from my_trio.constants import OperationType
from my_trio.controllers.invoices import BaseInvoicesController, ServiceException


class CSVDownloadingController(BaseInvoicesController):
    def __init__(self, request, account):
        super(CSVDownloadingController, self).__init__(request, OperationType.SelectInvoice, "SelectInvoice", account)

    def _call(self):
        self.need_log = False
        account = self.account
        invoices = self._select(self.request.args, account, csv=True)

        return self.download_csv(invoices)

    def download_csv(self, invoices):
        def generate_csv():
            csv = "invoice_id; shop_invoice_id; description; " \
                  "status; shop_id; shop_amount; shop_refund; " \
                  "shop_currency; paymethod; client_price; " \
                  "ps_currency; created; processed \n"

            for invoice in invoices:
                csv += "{invoice_id}; {shop_invoice_id}; {description}; " \
                       "{status}; {shop_id}; {shop_amount}; {shop_refund}; " \
                       "{shop_currency}; {paymethod}; {client_price}; " \
                       "{ps_currency}; {created}; {processed};\n".format(invoice_id=invoice.id,
                                                                         shop_invoice_id=invoice.shop_invoice_id.encode('cp1251') if invoice.shop_invoice_id else '',
                                                                         description=invoice.description.encode('cp1251') if invoice.description else '',
                                                                         status=invoice.status,
                                                                         shop_id=invoice.shop_id,
                                                                         shop_amount=invoice.shop_amount,
                                                                         shop_refund=invoice.shop_refund,
                                                                         shop_currency=invoice.shop_currency,
                                                                         paymethod=invoice.payway.encode('cp1251') if invoice.payway else '',
                                                                         client_price=invoice.client_price,
                                                                         ps_currency=invoice.ps_currency,
                                                                         created=invoice.created,
                                                                         processed=invoice.processed)
            yield csv

        return Response(generate_csv(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=invoices.csv"})
