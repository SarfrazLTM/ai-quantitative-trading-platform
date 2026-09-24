# Backtesting Framework

# 1. Overview

The platform includes a historical backtesting framework designed to evaluate systematic trading strategies, strategy families, portfolio configurations, and risk-management rules using historical market data.

The backtesting engine attempts to reproduce the decision-making process that would have occurred during live trading while maintaining strict chronological ordering and avoiding future information leakage.

Backtesting is used for:

- Strategy evaluation
- Strategy-family evaluation
- Portfolio construction
- Risk analysis
- Position-sizing evaluation
- Drawdown analysis
- Performance comparison
- Model evaluation
- Parameter validation
- Research-to-production validation

The backtesting framework is designed to evaluate trading behaviour rather than optimize solely for a single performance metric.

Proprietary strategy rules, alpha-generating logic, feature formulas, and production model artifacts are intentionally excluded from this repository.

# 2. Backtesting Architecture

		HISTORICAL MARKET DATA
				 │
				 ▼
		  DATA VALIDATION
				 │
				 ▼
		MULTI-TIMEFRAME DATA
				 │
				 ▼
		FEATURE ENGINEERING
				 │
				 ▼
		 ML MODEL INFERENCE
				 │
				 ▼
		  MARKET CONTEXT
				 │
				 ▼
		STRATEGY / FAMILY LOGIC
				 │
				 ▼
		 PORTFOLIO ENGINE
				 │
				 ▼
		    RISK ENGINE
				 │
				 ▼
		POSITION MANAGEMENT
				 │
				 ▼
		 TRADE SIMULATION
				 │
				 ▼
		PERFORMANCE ENGINE
				 │
				 ▼
		  BACKTEST REPORT
		  
		  
# 3. Backtesting Objectives

The primary objective of backtesting is to answer:

"How would this trading system have behaved if the same decision process had been applied to historical market data?"

The framework evaluates more than whether a strategy generated profitable trades.

It also evaluates:

- Risk-adjusted returns
- Drawdown behaviour
- Trade frequency
- Consecutive losses
- Portfolio exposure
- Capital utilization
- Strategy interaction
- Recovery characteristics
- Performance stability
- Behaviour across different market regimes


# 4. Historical Data
The backtesting engine operates on historical market data for supported cryptocurrency trading pairs and timeframes.

Typical inputs include:

- OHLCV data
- Multiple trading pairs
- Multiple execution timeframes
- Higher-timeframe market data
- Volume information
- Derived market features
- ML model predictions

Historical data must be chronologically ordered before entering the simulation.

Conceptually:

	Historical Data
		  │
		  ▼
	Data Validation
		  │
		  ▼
	Timestamp Alignment
		  │
		  ▼
	Multi-Timeframe Synchronization
		  │
		  ▼
	Backtest Dataset
	
# 5. Multi-Timeframe Backtesting
The platform supports multi-timeframe decision making.

For example:

	Execution Timeframe: 30m

	30m → Execution Context
	2H  → Intermediate Context
	8H  → Higher-Timeframe Context
	
Higher-timeframe information must only become available to the backtest after the corresponding higher-timeframe candle has actually closed.

This is critical to prevent future information from being accidentally introduced into lower-timeframe decisions.

# 6. Point-in-Time Data Processing

Backtesting must operate on information that would have been available at each historical timestamp.

For a decision made at time T:

	Allowed Information

	Data available before T
			+
	Data available at T
			↓
	    Decision
		
The following must not influence the decision:

	Future candles
	Future indicators
	Future ML predictions
	Future trade outcomes
	Future portfolio information
	
# 7. Look-Ahead Bias Prevention

Look-ahead bias occurs when information from the future is unintentionally used to make a historical trading decision.

Examples include:

- Using a candle before it has closed
- Using future returns as a feature
- Computing indicators using future observations
- Using future higher-timeframe information
- Normalizing data using the complete historical dataset
- Training models using observations that occur after the simulated decision
- Selecting parameters based on the entire backtest period

The backtesting framework is designed to prevent these forms of leakage through chronological processing and appropriate dataset construction.

# 8. ML Model Integration

When ML models are used during a backtest, the model must behave as it would have behaved in live trading.

Conceptually:

	Historical Timestamp T
			│
			▼
	Available Market Data
			│
			▼
	Feature Generation
			│
			▼
	Model Inference
			│
			▼
	   Prediction
			│
			▼
	Trading Decision
	
The backtester should not use future observations to generate historical predictions.

Where model retraining is simulated, training data must end before the prediction timestamp.


# 9. Strategy Evaluation

Strategies are evaluated using the same available market information that would have existed at the historical decision point.

The general flow is:

	Market State
		 ↓
	Strategy Conditions
		 ↓
	ML / Market Context
		 ↓
	Entry Decision
		 ↓
	Risk Validation
		 ↓
	Position Creation
	
Different strategy families can be evaluated independently or as part of a portfolio.

Examples of strategy families include:

- Trend Pullback
- Trend Continuation
- Trend Reversion
- Breakout Continuation
- Compression Breakout
- Range Rejection
- Range Reversion
- Liquidity Trap Reversal

The exact strategy implementation is intentionally excluded from the public repository.

# 10. Portfolio Backtesting

The framework supports portfolio-level backtesting in addition to individual strategy testing.

A portfolio can contain multiple strategy-family and timeframe combinations.

Conceptually:

	Portfolio
	   │
	   ├── Strategy / Family A
	   ├── Strategy / Family B
	   ├── Strategy / Family C
	   └── Strategy / Family D
	   
Each portfolio can have its own:

- Capital allocation
- Pair universe
- Strategy selection
- Risk profile
- Position-sizing configuration
- Portfolio risk limit
- Performance statistics
- Equity curve
- Drawdown history
- Trade history

This allows the system to evaluate interactions between strategies rather than treating every strategy independently.


# 11. Position and Exposure Controls

The backtesting engine incorporates portfolio-level exposure rules.

Examples include:

- Risk per trade
- Maximum portfolio risk
- Position sizing
- Maximum allocation
- Symbol-level exposure
- Family-level exposure
- Portfolio drawdown limits
- Leverage constraints

A signal is therefore not automatically converted into a trade.

The general decision flow is:

	Signal
	  │
	  ▼
	Portfolio Validation
	  │
	  ▼
	Exposure Validation
	  │
	  ▼
	Risk Validation
	  │
	  ▼
	Position Sizing
	  │
	  ▼
	Simulated Trade
	
# 12. Position Sizing
Position sizing converts the configured risk level into an appropriate trade size.

Conceptually:

	Portfolio Capital
		   │
		   ▼
	Risk Per Trade
		   │
		   ▼
	Stop-Loss Distance
		   │
		   ▼
	Position Size
		   │
		   ▼
	Leverage / Exposure Constraints
	
The backtester uses the same risk-management assumptions intended for production wherever possible.

This helps maintain consistency between historical evaluation and live operation.

# 13. Trade Simulation

Once a trade is accepted, the backtesting engine simulates its lifecycle.

A simplified flow is

	Entry
	  │
	  ▼
	Open Position
	  │
	  ├── Stop Loss
	  │
	  ├── Take Profit
	  │
	  └── Exit Condition
	  │
	  ▼
	Closed Position
	  │
	  ▼
	Performance Calculation
	
Each simulated trade records relevant information such as:

- Symbol
- Direction
- Entry timestamp
- Entry price
- Position size
- Stop loss
- Take profit
- Exit timestamp
- Exit price
- Gross P&L
- Trading costs
- Net P&L
- Return
- Holding period
- Strategy
- Strategy family
- Timeframe

# 14. Trading Costs

Backtesting should account for realistic trading costs.

Depending on the execution model, these may include:

- Trading fees
- Slippage
- Funding costs
- Spread assumptions
- Other execution costs

Ignoring transaction costs can materially overstate historical performance, particularly for systems with high trade frequency.

Therefore, performance should be evaluated using both:

# 15. Equity Curve

The equity curve tracks portfolio value throughout the simulation.

Example:

	Initial Capital
		  │
		  ▼
	Trade P&L
		  │
		  ▼
	Updated Equity
		  │
		  ▼
	Next Trade
		  │
		  ▼
	Updated Equity
		  │
		  ▼
		 ...
		 
The equity curve is used to evaluate:

- Growth
- Drawdowns
- Recovery periods
- Volatility
- Performance stability
- Capital utilization

The final return alone is not considered sufficient to evaluate a trading system.

# 16. Drawdown Analysis

Maximum drawdown is a key risk metric.

For an equity curve:

	Peak Equity
		 │
		 ▼
	   Decline
		 │
		 ▼
	Trough Equity
	
The framework measures:

- Maximum drawdown
- Current drawdown
- Drawdown duration
- Recovery period
- Recovery characteristics

Drawdown analysis helps determine whether historical returns were achieved with an acceptable level of capital risk.

# 17. Performance Metrics

The backtesting framework can calculate multiple performance metrics.

Return Metrics
- Initial capital
- Final equity
- Net profit/loss
- Return on capital
- Annualized return

Trade Metrics
- Total trades
- Winning trades
- Losing trades
- Win rate
- Average win
- Average loss
- Maximum consecutive wins
- Maximum consecutive losses

Risk Metrics
- Maximum drawdown
- Current drawdown
- Drawdown duration
- Recovery period
- Ulcer Index

Risk-Adjusted Metrics
- Sharpe ratio
- Sortino ratio
- Calmar ratio
- Recovery factor
- Profit factor

Metrics should be interpreted together rather than relying on a single headline number.


# 18. Strategy-Level Analytics

Individual strategies can be evaluated independently.

Typical statistics include:

	Strategy
	 ├── Return
	 ├── Win Rate
	 ├── Profit Factor
	 ├── Sharpe
	 ├── Max Drawdown
	 ├── Trade Count
	 ├── Average Trade
	 └── Recovery Characteristics
	 
# 19. Strategy-Family Analytics

Strategies can also be aggregated into higher-level families.

For example:

	TREND_CONTINUATION
		   │
		   ├── Strategy A
		   ├── Strategy B
		   └── Strategy C
		   
Family-level analysis can measure:

- Contribution to portfolio return
- Family win rate
- Profit factor
- Drawdown
- Trade frequency
- Current performance
- Historical stability

This supports portfolio construction and adaptive allocation.


# 20. Market Regime Analysis
Backtest results can be segmented according to different market conditions.

Examples include:

- Trending markets
- Ranging markets
- High-volatility periods
- Low-volatility periods
- Expansion periods
- Contraction periods

This allows the platform to study whether a strategy's historical behaviour changes across different market environments.

# 21. Portfolio Correlation and Exposure

Combining multiple profitable strategies does not automatically create a diversified portfolio.

Strategies may produce correlated positions or similar market exposure.

The portfolio backtester therefore considers:

- Symbol overlap
- Strategy overlap
- Family overlap
- Directional exposure
- Concurrent positions
- Portfolio risk
- Correlated strategy behaviour

A portfolio-level view is important because several individually profitable strategies can still create excessive combined exposure.


# 22. Backtest Configuration

A backtest can be configured using parameters such as:

	Backtest Period
	Trading Pairs
	Execution Timeframe
	Strategy / Family
	Initial Capital
	Risk Per Trade
	Maximum Portfolio Risk
	Leverage
	Position Sizing
	Stop-Loss Configuration
	Take-Profit Configuration
	Trading Costs
	
The configuration should be stored alongside the resulting backtest so that results can be reproduced and compared.


# 23. Walk-Forward Evaluation

Historical performance should ideally be evaluated using a walk-forward methodology.

Conceptually:

	Training
	──────────────►
	Validation
		   ──────────────►
						 Test
							  ──────────────►

				  Roll Forward
				  
The process can then repeat across multiple historical windows.

Walk-forward evaluation helps determine whether performance remains consistent when the model or strategy is evaluated on unseen future periods.


# 24. Out-of-Sample Evaluation

A backtest should distinguish between:

- Training data
- Validation data
- Test data
- Out-of-sample periods

The final evaluation period should not influence model or strategy selection.

This provides a more realistic estimate of how the system may behave on previously unseen market conditions.


# 25. Overfitting and Backtest Bias

A strong historical result does not necessarily imply that a strategy will perform similarly in live markets.

Potential sources of overfitting include:


- Excessive parameter optimization
- Repeated testing against the same historical period
- Selecting strategies based only on past return
- Data leakage
- Survivorship bias
- Unrealistic execution assumptions
- Ignoring transaction costs
- Excessive strategy selection after observing results

The backtesting process should therefore emphasize robustness and out-of-sample behaviour.

# 26. Backtest Reproducibility

Each backtest should be reproducible from its configuration and relevant data/model versions.

A reproducible backtest should identify:

	Backtest
	 ├── Dataset Version
	 ├── Feature Version
	 ├── Model Version
	 ├── Strategy Version
	 ├── Portfolio Configuration
	 ├── Risk Configuration
	 ├── Cost Assumptions
	 └── Backtest Period
	 
# 27. Backtesting vs Live Trading

Backtesting attempts to simulate the live decision process, but it cannot perfectly reproduce real-world execution.

Differences may arise from:

- Market impact
- Slippage
- Latency
- Liquidity
- Funding changes
- Exchange behaviour
- Data quality
- Network failures
- Order execution differences

Therefore:

	Backtest
		↓
	Paper Trading
		↓
	Controlled Live Deployment
	
should be treated as progressively more realistic stages of system validation.