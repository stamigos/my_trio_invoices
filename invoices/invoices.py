# -*- coding: utf-8 -*-
from my_trio.constants import OperationType
from my_trio.controllers.invoices import BaseInvoicesController, ServiceException, invoice_pay_methods, currencies
from my_trio.utils import Struct


class InvoicesController(BaseInvoicesController):
    def __init__(self, request, account):
        super(InvoicesController, self).__init__(request, OperationType.SelectInvoice, "SelectInvoice", account)

    def _call(self):
        self.need_log = False
        account = self.account
        args = self._form_args(self.request)
        result = self._select(self.request.args, account, csv=False)
        pages_count = result.pages_count

        return Struct(invoices=result.invoices,
                      pages_count=pages_count,
                      page=self._get_page(),
                      currencies=currencies,
                      pay_methods=invoice_pay_methods,
                      args=args)

    def _get_page(self):
        curr_page = self.request.args.get('page')
        if curr_page and curr_page.isdigit():
            return int(curr_page)
        return 1

    def _form_args(self, request):
        args = dict(request.args.items())
        if request.args.get("paymethod"):
            args["paymethod"] = request.args.getlist("paymethod")
        if request.args.get("shop_currency"):
            args["shop_currency"] = request.args.getlist("shop_currency")
        if request.args.get("ps_currency"):
            args["ps_currency"] = request.args.getlist("ps_currency")
        if request.args.get("status"):
            args["status"] = request.args.getlist("status")
        return args
