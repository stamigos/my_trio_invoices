# -*- coding: utf-8 -*-
import datetime

from flask_peewee.utils import PaginatedQuery

from my_trio.controllers import _Controller, ServiceException, currencies, invoice_pay_methods
from my_trio.models import Shop, Account, Invoice as Invoice_model, InvoicePayway, PayMethod, Currency
from my_trio.entities import Invoice
from my_trio.constants import SELECT_LIMIT
from my_trio.utils import Struct
from config import RECORDS_PER_PAGE


class BaseInvoicesController(_Controller):
    def _select(self, form, account, csv=False):
        select_result = Invoice_model.select().join(Shop).join(Account).where(Account.id == account.id)

        if form.get('shop_id'):
            select_result = select_result.where(Shop.id == form['shop_id'])

        if form.get('invoice_id'):
            select_result = select_result.where(Invoice_model.id == form['invoice_id'])

        if form.get('shop_invoice_id'):
            select_result = select_result.where(Invoice_model.shop_invoice_id == form['shop_invoice_id'])

        if form.getlist('paymethod') and form.getlist('paymethod')[0] != '':
            select_result = select_result.join(InvoicePayway,
                                               on=InvoicePayway.id == Invoice_model.payway).join(PayMethod).where(PayMethod.id << form.getlist('paymethod'))

        if form.getlist('shop_currency') and form.getlist('shop_currency')[0] != '':
            select_result = select_result.where(Invoice_model.shop_currency << form.getlist('shop_currency'))

        if form.getlist('status') and form.getlist('status')[0] != '':
            select_result = select_result.where(Invoice_model.status << form.getlist('status'))

        if form.getlist('ps_currency') and form.getlist('ps_currency')[0] != '':
            select_result = select_result.where(Invoice_model.ps_currency << form.getlist('ps_currency'))

        if form.get('created_from'):
            created_from = self._try_parse_datetime(form['created_from'])
            select_result = select_result.where(Invoice_model.created > created_from)

        if form.get('created_to'):
            created_to = self._try_parse_datetime(form["created_to"])
            select_result = select_result.where(Invoice_model.created < created_to)

        if not csv:
            pages_count = PaginatedQuery(select_result.order_by(Invoice_model.id.desc()).limit(SELECT_LIMIT), RECORDS_PER_PAGE).get_pages()
            return Struct(invoices=[Invoice(inv) for inv in PaginatedQuery(select_result.order_by(Invoice_model.id.desc()).limit(SELECT_LIMIT), RECORDS_PER_PAGE).get_list()],
                          pages_count=pages_count)

        return [Invoice(inv) for inv in select_result.order_by(Invoice_model.id.desc()).limit(SELECT_LIMIT)]


