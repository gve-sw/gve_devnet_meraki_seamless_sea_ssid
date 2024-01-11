"""
Copyright (c) 2023 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Mark Orszycki  <morszyck@cisco.com>"
__copyright__ = "Copyright (c) 2023 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

from fastapi import FastAPI
import uvicorn
from routes import router as webhook_router
# from meraki_funcs import *
from meraki_funcs import MerakiOps

from logrr import lm
from config import config


def create_app() -> FastAPI:
    fastapi_app = FastAPI()

    @fastapi_app.on_event("startup")
    async def on_startup():
        lm.print_start_panel(config.APP_NAME)
        lm.display_config_table(config)

        # Initialize Meraki Dashboard
        # fastapi_app.state.meraki_dashboard = get_meraki_dashboard()
        fastapi_app.state.meraki_operations = MerakiOps()


    @fastapi_app.on_event("shutdown")
    async def on_shutdown():
        lm.print_exit_panel()

    fastapi_app.include_router(webhook_router)
    return fastapi_app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="warning", reload=True)
