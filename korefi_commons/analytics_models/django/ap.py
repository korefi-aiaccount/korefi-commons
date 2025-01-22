from django.db import models
import uuid


class ApBillHeader(models.Model):
    bill_hdr_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    organisation_id = models.IntegerField()
    vendor_id = models.IntegerField()
    bill_number = models.CharField(max_length=255)
    bill_currency_code = models.BigIntegerField()
    bill_amount = models.FloatField()
    bill_amount_lc = models.FloatField()
    bill_date = models.DateField()
    bill_type = models.BigIntegerField()
    description = models.CharField(max_length=255)
    payment_terms_id = models.BigIntegerField()
    due_date = models.DateField()
    payment_status = models.CharField(max_length=255)
    exchange_rate = models.FloatField()
    paid_amount_lc = models.FloatField()
    created_time = models.DateField()
    created_by = models.CharField(max_length=255)
    last_update_date = models.DateField()
    last_updated_by = models.CharField(max_length=255)
    account_id = models.BigIntegerField()

    class Meta:
        db_table = "ap_bill_header_h"


class ApBillLines(models.Model):
    bill_hdr = models.ForeignKey(ApBillHeader, on_delete=models.CASCADE)
    bill_line_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    item_description = models.CharField(max_length=255)
    quantity = models.FloatField()
    line_amount = models.FloatField()
    unit_price = models.FloatField()
    created_time = models.DateField()
    created_by = models.CharField(max_length=255)
    last_update_date = models.DateField()
    last_updated_by = models.CharField(max_length=255)
    item_id = models.BigIntegerField()
    item = models.CharField(max_length=255)
    line_amount_lc = models.FloatField()
    line_status = models.CharField(max_length=255)
    account_id = models.BigIntegerField()

    class Meta:
        db_table = "ap_bill_lines_h"
