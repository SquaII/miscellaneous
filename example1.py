
def mark_expired_bills(fn):
    def func(self, *args, **kw):
        bills = fn(self, *args, **kw)
        timestamp = time()
        iterable = [bills] if not isinstance(bills, list) else bills
        for bill in iterable:
            if bill.status == BILL_STATUS_CODES['unpaid'] and bill.expire_date < timestamp:
                bill.status = BILL_STATUS_CODES['expired']
                bill.save()

        return bills
    return func


class BillManager(ModelManager):

    @mark_expired_bills
    def get_by_uid(self, uid):

        """ Получение счета по его уникальному номеру """

        return self.query().filter(self.model.bill_uid == uid).first()

    @mark_expired_bills
    def get_by_number(self, bill_number):

        """ Получение счета по его номеру """

        return self.query().filter(self.model.bill_number == bill_number).first()

    @mark_expired_bills
    def get_by_date(self, from_date, to_date, ps_shortcut):

        """ Получение списка счетов """

        return self.query().filter(self.model.create_date >= from_date,
                                   self.model.create_date <= to_date,
                                   or_(self.model.sender_ps == ps_shortcut,
                                       self.model.recipient_ps == ps_shortcut)).all()

    def get_last_bill_number(self):

        """ Получение номера последнего созданного счета """

        return (self.query()
                .with_entities(self.model.bill_number)
                .order_by(desc(self.model.bill_number))
                .limit(1)
                .scalar()
                )

    @mark_expired_bills
    def get_sender_account_bills(self, account_id):

        """ Получение счетов """

        from geepay.modules.api import PAYMENT_SYSTEMS

        return (self.query()
                .filter(self.model.sender_uid == str(account_id),
                        self.model.sender_ps == PAYMENT_SYSTEMS['geepay'])
                .all()
                )
