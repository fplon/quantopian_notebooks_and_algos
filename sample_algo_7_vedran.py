#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vedrans sample algo using estimates
"""

from quantopian.algorithm import attach_pipeline, pipeline_output

import quantopian.optimize as opt
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.filters import QTradableStocksUS
from quantopian.pipeline.domain import US_EQUITIES

import quantopian.pipeline.data.factset.estimates as fe

import pandas as pd
import numpy as np

def initialize(context):
    
    set_commission(commission.PerShare(cost = 0.000, min_trade_cost = 0))
    set_slippage(slippage.FixedSlippage(spread = 0))
    
    schedule_function(
        rebalance,
        date_rules.every_day(),
        time_rules.market_open(hours = 2),
    )

    attach_pipeline(make_pipeline(context), 'pipeline')
    
    schedule_function(
        record_positions,
        date_rules.every_day(),
        time_rules.market_close(),
    )

def create_factor():
    
    universe = QTradableStocksUS()
    
    fq1_eps_cons = fe.PeriodicConsensus.slice('EPS', 'qf', 1)
    fq1_eps_cons_up = fq1_eps_cons.up.latest
    fq1_eps_cons_down = fq1_eps_cons.down.latest
    
    alpha_factor = fq1_eps_cons_up - fq1_eps_cons_down
    
    screen = (
        universe 
        & ~alpha_factor.isnull() 
        & alpha_factor.isfinite()
    )
    
    return alpha_factor, screen


def make_pipeline(context): 
    
    alpha_factor, screen = create_factor()
    
    alpha_winsorized = alpha_factor.winsorize(0.01, 0.99, mask = screen)
    
    alpha_rank = alpha_winsorized.rank().zscore()
    
    pipe = Pipeline(
        columns = {'alpha_factor': alpha_rank,},
        screen = (screen), 
        domain = US_EQUITIES
    )

    return pipe


def rebalance(context, data):
    
    output = pipeline_output('pipeline')
    alpha_factor = output.alpha_factor
    log.info(alpha_factor)
    
    weights = alpha_factor / alpha_factor.abs().sum()
    
    order_optimal_portfolio(
        objective = opt.TargetWeights(weights),
        constraints = [],
    )
    
def record_positions(context, data): 
   
    pos = pd.Series()
    for position in context.portfolio.positions.values():
        pos.loc[position.sid] = position.amount
        
    pos /= pos.abs().sum()