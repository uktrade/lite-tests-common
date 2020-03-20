from pytest import fixture
from faker import Faker

fake = Faker()

from ..tools.utils import get_lite_client, Timer


def save_application_data_to_context(lite_client, context):
    context.app_id = lite_client.context["application_id"]
    context.case_id = lite_client.context["application_id"]
    context.reference_code = lite_client.context["reference_code"]
    context.end_user = lite_client.context.get("end_user")
    context.consignee = lite_client.context.get("consignee")
    context.third_party = lite_client.context.get("third_party")
    context.ultimate_end_user = lite_client.context.get("ultimate_end_user")


@fixture
def apply_for_standard_application(driver, api_client_config, context):
    timer = Timer()
    lite_client = get_lite_client(context, api_client_config)
    lite_client.api_client.auth_exporter_user(lite_client.context["org_id"])
    context.app_name = fake.bs()
    context.good_value = 1.21

    draft_id = lite_client.applications.add_draft(
        draft={
            "name": context.app_name,
            "application_type": "siel",
            "export_type": "permanent",
            "have_you_been_informed": "yes",
            "reference_number_on_information_form": "1234",
        },
        good={
            "good_id": "",
            "quantity": 1234,
            "unit": "MTR",
            "value": context.good_value,
            "is_good_incorporated": True,
            "is_good_pv_graded": "no",
        },
        end_user={
            "name": fake.name(),
            "address": fake.street_address() + fake.state() + fake.postcode(),
            "country": "GB",
            "sub_type": "government",
            "website": fake.uri(),
            "type": "end_user",
        },
        ultimate_end_user={
            "name": fake.name(),
            "address": fake.street_address() + fake.state() + fake.postcode(),
            "country": "GB",
            "sub_type": "commercial",
            "website": fake.uri(),
            "type": "ultimate_end_user",
        },
        consignee={
            "name": fake.name(),
            "address": fake.street_address() + fake.state() + fake.postcode(),
            "country": "GB",
            "sub_type": "government",
            "website": fake.uri(),
            "type": "consignee",
        },
        third_party={
            "name": fake.name(),
            "address": fake.street_address() + fake.state() + fake.postcode(),
            "country": "UA",
            "sub_type": "government",
            "role": "agent",
            "website": fake.uri(),
            "type": "third_party",
        },
        end_use_details={
            "intended_end_use": "intended end use",
            "is_military_end_use_controls": False,
            "is_informed_wmd": False,
            "is_suspected_wmd": False,
            "is_eu_military": False,
        },
    )
    lite_client.applications.submit_application(draft_id)
    save_application_data_to_context(lite_client, context)
    context.good_id = lite_client.context.get("good_id")
    timer.print_time("apply_for_standard_application")


@fixture(scope="module")
def add_an_ecju_query(driver, api_client_config, context):
    lite_client = get_lite_client(context, api_client_config)
    lite_client.api_client.auth_exporter_user(lite_client.context["org_id"])
    lite_client.ecju_queries.add_ecju_query(context.case_id)


@fixture(scope="function")
def apply_for_clc_query(driver, api_client_config, context):
    lite_client = get_lite_client(context, api_client_config)
    lite_client.api_client.auth_exporter_user(lite_client.context["org_id"])
    lite_client.goods_queries.add_goods_clc_query(lite_client.goods)
    context.clc_case_id = lite_client.context["case_id"]


@fixture(scope="function")
def apply_for_grading_query(driver, api_client_config, context):
    lite_client = get_lite_client(context, api_client_config)
    lite_client.api_client.auth_exporter_user(lite_client.context["org_id"])
    lite_client.goods_queries.add_goods_grading_query(lite_client.goods)
    context.clc_case_id = lite_client.context["case_id"]


# The below is currently not used due to bug LT-1808 but willl need to be used for internal HMRC tests when fixed.
@fixture(scope="function")
def apply_for_hmrc_query(driver, api_client_config, context):
    lite_client = get_lite_client(context, api_client_config)
    lite_client.api_client.auth_exporter_user(lite_client.context["hmrc_org_id"])
    draft_id = lite_client.applications.add_hmrc_draft(
        draft={
            "application_type": "cre",
            "organisation": lite_client.context["org_id"],
            "hmrc_organisation": lite_client.context["hmrc_org_id"],
        },
        end_user={
            "name": fake.name(),
            "address": fake.street_address() + fake.state() + fake.postcode(),
            "country": "GB",
            "sub_type": "government",
            "website": fake.uri(),
            "type": "end_user",
        },
    )
    lite_client.applications.submit_application(draft_id)
    context.case_id = lite_client.context["case_id"]


@fixture(scope="module")
def apply_for_eua_query(driver, api_client_config, context):
    lite_client = get_lite_client(context, api_client_config)
    lite_client.api_client.auth_exporter_user(lite_client.context["org_id"])
    lite_client.parties.add_eua_query()
    context.eua_id = lite_client.context["end_user_advisory_id"]
    context.eua_reference_code = lite_client.context["end_user_advisory_reference_code"]


@fixture(scope="module")
def apply_for_open_application(driver, api_client_config, context):
    timer = Timer()
    lite_client = get_lite_client(context, api_client_config)
    lite_client.api_client.auth_exporter_user(lite_client.context["org_id"])

    context.app_name = fake.bs()

    draft_id = lite_client.applications.add_open_draft(
        draft={
            "name": context.app_name,
            "application_type": "oiel",
            "export_type": "permanent",
            "have_you_been_informed": "yes",
            "reference_number_on_information_form": "1234",
        },
        end_use_details={
            "intended_end_use": "intended end use",
            "is_military_end_use_controls": False,
            "is_informed_wmd": False,
            "is_suspected_wmd": False,
        },
    )
    lite_client.applications.submit_application(draft_id)
    save_application_data_to_context(lite_client, context)
    context.country = lite_client.context["country"]
    timer.print_time("apply_for_open_application")


def _apply_for_mod_clearance(
    type, has_end_user, has_consignee, has_ultimate_end_user, has_third_party, has_location, api_client_config, context
):
    lite_client = get_lite_client(context, api_client_config)
    lite_client.api_client.auth_exporter_user(lite_client.context["org_id"])
    context.app_name = fake.bs()
    draft_id = lite_client.applications.add_draft(
        draft={
            "name": context.app_name,
            "application_type": type,
            "clearance_level": "uk_official" if type == "f680" else None,
        },
        end_user={
            "name": fake.name(),
            "address": fake.street_address() + fake.state() + fake.postcode(),
            "country": "GB",
            "sub_type": "government",
            "website": fake.uri(),
            "type": "end_user",
            "clearance_level": "uk_official" if type == "f680" else None,
        },
        ultimate_end_user={
            "name": fake.name(),
            "address": fake.street_address() + fake.state() + fake.postcode(),
            "country": "GB",
            "sub_type": "commercial",
            "website": fake.uri(),
            "type": "ultimate_end_user",
            "clearance_level": "uk_official" if type == "f680" else None,
        },
        consignee={
            "name": fake.name(),
            "address": fake.street_address() + fake.state() + fake.postcode(),
            "country": "GB",
            "sub_type": "government",
            "website": fake.uri(),
            "type": "consignee",
            "clearance_level": "uk_official" if type == "f680" else None,
        },
        third_party={
            "name": fake.name(),
            "address": fake.street_address() + fake.state() + fake.postcode(),
            "country": "UA",
            "sub_type": "government",
            "role": "agent",
            "website": fake.uri(),
            "type": "third_party",
            "clearance_level": "uk_official" if type == "f680" else None,
        },
        has_end_user=has_end_user,
        has_consignee=has_consignee,
        has_ultimate_end_user=has_ultimate_end_user,
        has_third_party=has_third_party,
        has_location=has_location,
        f680_clearance_types=["market_survey"] if type == "f680" else None,
        end_use_details={"intended_end_use": "intended end use"} if type == "f680" else None,
    )
    if type == "exhc":
        lite_client.applications.post_exhibition_details(draft_id=draft_id, data=None)
    lite_client.applications.submit_application(draft_id)
    save_application_data_to_context(lite_client, context)


@fixture(scope="module")
def apply_for_exhibition_clearance(driver, api_client_config, context):
    _apply_for_mod_clearance(
        type="exhc",
        has_consignee=False,
        has_ultimate_end_user=False,
        has_end_user=False,
        has_third_party=False,
        has_location=False,
        api_client_config=api_client_config,
        context=context,
    )


@fixture(scope="module")
def apply_for_f680_clearance(driver, api_client_config, context):
    _apply_for_mod_clearance(
        type="f680",
        has_end_user=True,
        has_third_party=True,
        has_consignee=False,
        has_ultimate_end_user=False,
        has_location=False,
        api_client_config=api_client_config,
        context=context,
    )


@fixture(scope="module")
def apply_for_gifting_clearance(driver, api_client_config, context):
    _apply_for_mod_clearance(
        type="gift",
        has_end_user=True,
        has_third_party=True,
        has_consignee=False,
        has_ultimate_end_user=False,
        has_location=False,
        api_client_config=api_client_config,
        context=context,
    )
