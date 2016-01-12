# -*- coding: utf-8 -*-
import urllib
from flask import flash, render_template, request, Blueprint, redirect, url_for, g, jsonify, make_response

from my_trio import app, auth, constants
from my_trio.decorators import change_password_required
from my_trio.controllers.invoices.invoices import InvoicesController
from my_trio.controllers.invoices.csv_loader import CSVDownloadingController
from config import TRIO_URL, TRIO_SECRET, RECORDS_PER_PAGE
from my_trio.trio import TrioApi
from my_trio.utils import prepare_for_urlencode

invoices_page = Blueprint('invoices', __name__, template_folder="templates", static_url_path='/static2')


@app.context_processor
def username():
    return {
        'username': g.user.email.split('@')[0] if g.user else None
    }


@app.template_filter()
def clean_querystring(request_args, *keys_to_remove, **new_values):
    querystring = prepare_for_urlencode(request_args, ["shop_currency", "ps_currency", "status", "paymethod"])
    for key in keys_to_remove:
        querystring.pop(key, None)
    querystring.update(new_values)
    return urllib.urlencode(querystring.items(), True)


@app.template_filter()
def format_string(data, end=15):
    if data:
        string = str(data)
        if len(string) > end:
            return string[:12] + '...'
        return string


@app.template_filter()
def format_amount(value):
    return '%.2f' % value


@app.route('/<lang_code>/invoices/', methods=['GET'])
@auth.login_required
@change_password_required
def invoices(account):
    result = InvoicesController(request, account).call()

    if not result.result:
        flash(result.message)
        invoices = []
        currencies = {}
        pay_methods = {}
        args = {}
        pages_count = 0
    else:
        invoices = result.data.invoices
        currencies = result.data.currencies
        pay_methods = result.data.pay_methods
        args = dict(result.data.args.items())
        pages_count = result.data.pages_count

    return render_template('invoices/invoices_new.html',
                           invoices=invoices,
                           pages_count=pages_count,
                           currencies=currencies,
                           pay_methods=pay_methods,
                           statuses=constants.InvoiceStatus.AllStatuses,
                           status_classes=constants.InvoiceStatus.StatusesClasses,
                           url=url_for('invoices', lang_code=g.current_lang, **args),
                           args=args,
                           **args)


@app.route('/ok/', methods=['GET', 'POST'])
def ok():
    return make_response('OK', 200)


@app.route('/<lang_code>/invoices/<invoice_id>/invoice_notify/', methods=['GET'])
@auth.login_required
@change_password_required
def invoice_notify(account, invoice_id):
    # TODO add controller
    r = TrioApi(TRIO_URL, TRIO_SECRET).invoice_notify(invoice_id)
    return jsonify(data=r.data)


@app.route('/<lang_code>/invoices/download/', methods=['GET'])
@auth.login_required
@change_password_required
def csv_download(account):
    result = CSVDownloadingController(request, account).call()

    if not result.result:
        flash(result.message)
        return redirect(url_for('invoices', lang_code=g.current_lang))
    return result.data
