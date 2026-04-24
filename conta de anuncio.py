# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

import os
from dotenv import load_dotenv
from facebook_business.adobjects.abstractobject import AbstractObject
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.api import FacebookAdsApi

load_dotenv()

# Carregue as credenciais do arquivo .env
# ATENÇÃO: O token antigo foi exposto e deve ser revogado imediatamente!
access_token = os.getenv("META_BUSINESS_ACCESS_TOKEN") # Use um token com permissão para Ads
app_id = os.getenv("META_APP_ID")
ad_account_id = os.getenv("META_AD_ACCOUNT_ID")

campaign_name = "My Quickstart Campaign"

params = {}
FacebookAdsApi.init(access_token=access_token)


# Create an ad campaign with objective OUTCOME_TRAFFIC

fields = []
params = {
    "name": campaign_name,
    "objective": "OUTCOME_TRAFFIC",
    "status": "PAUSED",
    "special_ad_categories": [],
}
campaign = AdAccount(ad_account_id).create_campaign(
    fields=fields,
    params=params,
)
campaign_id = campaign.get_id()

print("Your created campaign id is: " + campaign_id)
