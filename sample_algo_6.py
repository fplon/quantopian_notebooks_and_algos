#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 21:30:15 2020

@author: finlayoneill
"""


QUARTER_STARTS = [1,4,7,10]

def initialize(context):
    # Algorithm will call rebalance once at the start of each month.
    schedule_function(
        rebalance,
        date_rules.month_start(),
        time_rules.market_open()
    )

def rebalance(context,data):

    # If the current month number is not in QUARTER_STARTS,
    # don't do anything.
    month_number = get_datetime().date().month
    if month_number not in QUARTER_STARTS:
        return

    # Rest of rebalance logic goes here.