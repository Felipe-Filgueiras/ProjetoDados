#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

class DefaultConfig:
    """ Bot Configuration """

    PORT = 3979
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    API_BASE_URL = "http://localhost:8080/api" 
    CLU_ENDPOINT = "https://bothotellinguagem.cognitiveservices.azure.com/"
    CLU_KEY = "DwkY1s1Q2fnL9LrRhO4pFyHFIneWw5xxJ9y18yxvUrOsFmsjs0XxJQQJ99BKACBsN54XJ3w3AAAaACOGv8RJ"
    CLU_PROJECT = "ProjetoCloudHotel"
    CLU_DEPLOYMENTNAME = "ReservaHotel"