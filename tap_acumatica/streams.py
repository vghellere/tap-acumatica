"""Stream type classes for tap-acumatica."""

from __future__ import annotations

from typing import Any

import requests
from hotglue_singer_sdk import typing as th  # JSON Schema typing helpers
from typing_extensions import override

from tap_acumatica.client import AcumaticaStream

_SELECT_VALUE = th.ObjectType(
    th.Property("id", th.StringType),
    th.Property("description", th.StringType),
)

_ADDRESS = th.ObjectType(
    th.Property("id", th.StringType),
    th.Property("rowNumber", th.IntegerType),
    th.Property("note", th.StringType),
    th.Property("AddressLine1", th.StringType),
    th.Property("AddressLine2", th.StringType),
    th.Property("BuildingName", th.StringType),
    th.Property("BuildingNumber", th.StringType),
    th.Property("City", th.StringType),
    th.Property("Country", th.StringType),
    th.Property("Department", th.StringType),
    th.Property("DistrictName", th.StringType),
    th.Property("Floor", th.StringType),
    th.Property("PostalCode", th.StringType),
    th.Property("PostBox", th.StringType),
    th.Property("Room", th.StringType),
    th.Property("State", th.StringType),
    th.Property("StreetName", th.StringType),
    th.Property("SubDepartment", th.StringType),
    th.Property("TownLocationName", th.StringType),
    th.Property("UnitNumber", th.StringType),
    th.Property("custom", th.ObjectType()),
)

_CONTACT = th.ObjectType(
    th.Property("id", th.StringType),
    th.Property("rowNumber", th.IntegerType),
    th.Property("note", th.StringType),
    th.Property("Active", th.BooleanType),
    th.Property("Address", _ADDRESS),
    th.Property("Attention", th.StringType),
    th.Property("BusinessAccount", th.StringType),
    th.Property("CompanyName", th.StringType),
    th.Property("ContactClass", th.StringType),
    th.Property("ContactID", th.IntegerType),
    th.Property("ContactMethod", th.StringType),
    th.Property("DateOfBirth", th.DateTimeType),
    th.Property("DisplayName", th.StringType),
    th.Property("DoNotCall", th.BooleanType),
    th.Property("DoNotEmail", th.BooleanType),
    th.Property("DoNotFax", th.BooleanType),
    th.Property("DoNotMail", th.BooleanType),
    th.Property("Duplicate", th.StringType),
    th.Property("DuplicateFound", th.BooleanType),
    th.Property("Email", th.StringType),
    th.Property("Fax", th.StringType),
    th.Property("FaxType", th.StringType),
    th.Property("FirstName", th.StringType),
    th.Property("Gender", th.StringType),
    th.Property("Image", th.StringType),
    th.Property("JobTitle", th.StringType),
    th.Property("LanguageOrLocale", th.StringType),
    th.Property("LastModifiedDateTime", th.DateTimeType),
    th.Property("LastName", th.StringType),
    th.Property("MaritalStatus", _SELECT_VALUE),
    th.Property("MiddleName", th.StringType),
    th.Property("NoMarketing", th.BooleanType),
    th.Property("NoMassMail", th.BooleanType),
    th.Property("NoteID", th.StringType),
    th.Property("OverrideAccountAddress", th.BooleanType),
    th.Property("Owner", th.StringType),
    th.Property("OwnerEmployeeName", th.StringType),
    th.Property("ParentAccount", th.StringType),
    th.Property("Phone1", th.StringType),
    th.Property("Phone1Type", th.StringType),
    th.Property("Phone2", th.StringType),
    th.Property("Phone2Type", th.StringType),
    th.Property("Phone3", th.StringType),
    th.Property("Phone3Type", th.StringType),
    th.Property("Reason", th.StringType),
    th.Property("Source", th.StringType),
    th.Property("SourceCampaign", th.StringType),
    th.Property("SpouseOrPartnerName", th.StringType),
    th.Property("Status", _SELECT_VALUE),
    th.Property("Synchronize", th.BooleanType),
    th.Property("Title", th.StringType),
    th.Property("Type", th.StringType),
    th.Property("WebSite", th.StringType),
    th.Property("Workgroup", th.StringType),
    th.Property("WorkgroupDescription", th.StringType),
    th.Property("custom", th.ObjectType()),
)

_ATTRIBUTE = th.ObjectType(
    th.Property("id", th.StringType),
    th.Property("rowNumber", th.IntegerType),
    th.Property("note", th.StringType),
    th.Property("AttributeDescription", th.StringType),
    th.Property("AttributeID", th.StringType),
    th.Property("RefNoteID", th.StringType),
    th.Property("Required", th.BooleanType),
    th.Property("Value", th.StringType),
    th.Property("ValueDescription", th.StringType),
    th.Property("custom", th.ObjectType()),
)

_PAYMENT_INSTRUCTION = th.ObjectType(
    th.Property("id", th.StringType),
    th.Property("rowNumber", th.IntegerType),
    th.Property("note", th.StringType),
    th.Property("Description", th.StringType),
    th.Property("LocationID", th.IntegerType),
    th.Property("PaymentInstructionsID", th.StringType),
    th.Property("PaymentMethod", th.StringType),
    th.Property("Value", th.StringType),
    th.Property("custom", th.ObjectType()),
)

_CUSTOMER_CONTACT = th.ObjectType(
    th.Property("id", th.StringType),
    th.Property("rowNumber", th.IntegerType),
    th.Property("note", th.StringType),
    th.Property("Contact", _CONTACT),
    th.Property("ContactID", th.IntegerType),
    th.Property("custom", th.ObjectType()),
)


class CompaniesStream(AcumaticaStream):
    """Stream for ``companies``."""

    name = "companies"
    path = "/CompaniesStructure"
    rest_method = "PUT"
    records_jsonpath = "$.Results[*]"
    primary_keys = ["id"]
    replication_key = None
    expand = "Results"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("BaseCurrencyID", th.StringType),
        th.Property("CompanyID", th.StringType),
        th.Property("CompanyName", th.StringType),
        th.Property("CompanyStatus", th.BooleanType),
        th.Property("CompanyType", th.StringType),
    ).to_dict()

    @override
    def prepare_request_payload(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict:
        """Send an empty inquiry body so Acumatica returns company branches."""
        self._seen_ids: set[str] = set()
        return {}

    @override
    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        """Keep one record per company and drop branch fields."""
        row = super().post_process(row, context)
        record_id = row["id"]
        if record_id in self._seen_ids:
            return None
        self._seen_ids.add(record_id)
        return {
            "id": row["id"],
            "BaseCurrencyID": row["BaseCurrencyID"],
            "CompanyID": row["CompanyID"],
            "CompanyName": row["CompanyName"],
            "CompanyStatus": row["CompanyStatus"],
            "CompanyType": row["CompanyType"],
        }

    @override
    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Any | None,
    ) -> None:
        """The inquiry returns every company branch in one response."""
        return None


class AccountsStream(AcumaticaStream):
    """Stream for ``accounts``."""

    name = "accounts"
    path = "/Account"
    primary_keys = ["id"]
    replication_key = "LastModifiedDateTime"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("rowNumber", th.IntegerType),
        th.Property("note", th.StringType),
        th.Property("AccountCD", th.StringType),
        th.Property("AccountClass", th.StringType),
        th.Property("AccountGroup", th.StringType),
        th.Property("AccountID", th.IntegerType),
        th.Property("Active", th.BooleanType),
        th.Property("CashAccount", th.BooleanType),
        th.Property("ChartOfAccountsOrder", th.IntegerType),
        th.Property("ConsolidationAccount", th.StringType),
        th.Property("CreatedDateTime", th.DateTimeType),
        th.Property("CurrencyID", th.StringType),
        th.Property("Description", th.StringType),
        th.Property("LastModifiedDateTime", th.DateTimeType),
        th.Property("PostOption", _SELECT_VALUE),
        th.Property("RequireUnits", th.BooleanType),
        th.Property("RevaluationRateType", th.StringType),
        th.Property("Secured", th.BooleanType),
        th.Property("TaxCategory", th.StringType),
        th.Property("Type", th.StringType),
        th.Property("UseDefaultSubaccount", th.BooleanType),
        th.Property("custom", th.ObjectType()),
    ).to_dict()


class VendorsStream(AcumaticaStream):
    """Stream for ``vendors``."""

    name = "vendors"
    path = "/Vendor"
    primary_keys = ["id"]
    replication_key = "LastModifiedDateTime"
    expand = (
        "Attributes,"
        "Contacts($expand=Contact($expand=Address)),"
        "MainContact($expand=Address),"
        "PaymentInstructions,"
        "PrimaryContact($expand=Address),"
        "RemittanceContact($expand=Address),"
        "ShippingContact($expand=Address)"
    )
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("rowNumber", th.IntegerType),
        th.Property("note", th.StringType),
        th.Property("AccountRef", th.StringType),
        th.Property("APAccount", th.StringType),
        th.Property("APSubaccount", th.StringType),
        th.Property("Attributes", th.ArrayType(_ATTRIBUTE)),
        th.Property("CashAccount", th.StringType),
        th.Property("Contacts", th.ArrayType(_CUSTOMER_CONTACT)),
        th.Property("CreatedDateTime", th.DateTimeType),
        th.Property("CurrencyID", th.StringType),
        th.Property("CurrencyRateType", th.StringType),
        th.Property("EnableCurrencyOverride", th.BooleanType),
        th.Property("EnableRateOverride", th.BooleanType),
        th.Property("F1099Box", th.StringType),
        th.Property("F1099Vendor", th.BooleanType),
        th.Property("FATCA", th.BooleanType),
        th.Property("FOBPoint", th.StringType),
        th.Property("ForeignEntity", th.BooleanType),
        th.Property("LandedCostVendor", th.BooleanType),
        th.Property("LastModifiedDateTime", th.DateTimeType),
        th.Property("LeadTimedays", th.IntegerType),
        th.Property("LegalName", th.StringType),
        th.Property("LocationName", th.StringType),
        th.Property("MainContact", _CONTACT),
        th.Property("MaxReceipt", th.NumberType),
        th.Property("MinReceipt", th.NumberType),
        th.Property("ParentAccount", th.StringType),
        th.Property("PaymentBy", th.StringType),
        th.Property("PaymentInstructions", th.ArrayType(_PAYMENT_INSTRUCTION)),
        th.Property("PaymentLeadTimedays", th.IntegerType),
        th.Property("PaymentMethod", th.StringType),
        th.Property("PaySeparately", th.BooleanType),
        th.Property("PrimaryContact", _CONTACT),
        th.Property("PrintOrders", th.BooleanType),
        th.Property("ReceiptAction", th.StringType),
        th.Property("ReceivingBranch", th.StringType),
        th.Property("RemittanceAddressOverride", th.BooleanType),
        th.Property("RemittanceContact", _CONTACT),
        th.Property("RemittanceContactOverride", th.BooleanType),
        th.Property("SendOrdersbyEmail", th.BooleanType),
        th.Property("ShippingAddressOverride", th.BooleanType),
        th.Property("ShippingContact", _CONTACT),
        th.Property("ShippingContactOverride", th.BooleanType),
        th.Property("ShippingTerms", th.StringType),
        th.Property("ShipVia", th.StringType),
        th.Property("Status", _SELECT_VALUE),
        th.Property("TaxRegistrationID", th.StringType),
        th.Property("TaxZone", th.StringType),
        th.Property("Terms", th.StringType),
        th.Property("ThresholdReceipt", th.NumberType),
        th.Property("VendorClass", th.StringType),
        th.Property("VendorID", th.StringType),
        th.Property("VendorIsTaxAgency", th.BooleanType),
        th.Property("VendorName", th.StringType),
        th.Property("Warehouse", th.StringType),
        th.Property("custom", th.ObjectType()),
    ).to_dict()

