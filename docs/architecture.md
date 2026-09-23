# AI Quantitative Trading Platform — Architecture

## 1. Architecture Overview

The AI Quantitative Trading Platform is an adaptive quantitative
cryptocurrency portfolio platform designed for systematic trading
across multiple execution timeframes.

The platform combines market data processing, quantitative feature
engineering, machine learning, strategy evaluation, portfolio
construction, risk management, adaptive allocation, paper trading,
and real-time webhook-based signal delivery.

The platform currently supports multiple execution timeframes:

- 5m
- 15m
- 30m
- 1h

and a predefined universe of 49 cryptocurrency trading pairs,
including BTCUSDT, ETHUSDT, SOLUSDT, and other liquid crypto assets.

The architecture is designed around the following principles:

1. Quantitative and systematic decision making
2. Multi-timeframe market intelligence
3. Pre-built strategy families
4. Portfolio-level diversification
5. Hierarchical risk management
6. Adaptive allocation
7. Separation of signal generation from trade execution
8. No custody or storage of user exchange API credentials
9. Production-oriented monitoring and observability
10. Modular architecture that can evolve with additional models,
   strategies, and timeframes

The platform is designed primarily as a signal-generation and
quantitative portfolio platform rather than as an exchange-account
management system.

---

# 2. High-Level Architecture

The platform is organized into several logical layers.


			 MARKET DATA
				  |
				  v
	 +------------------------+
	 | Data Processing &       |
	 | Normalization           |
	 +-----------+------------+
				 |
				 v
	 +------------------------+
	 | Feature Engineering     |
	 | & Quantitative Features |
	 +-----------+------------+
				 |
				 v
	 +------------------------+
	 | Market Structure AI     |
	 | & HTF Predictions       |
	 +-----------+------------+
				 |
				 v
	 +------------------------+
	 | Strategy / Family       |
	 | Evaluation Models       |
	 +-----------+------------+
				 |
				 v
	 +------------------------+
	 | Signal & Opportunity    |
	 | Evaluation              |
	 +-----------+------------+
				 |
				 v
	 +------------------------+
	 | Portfolio Engine        |
	 | & Allocation            |
	 +-----------+------------+
				 |
				 v
	 +------------------------+
	 | Risk Engine             |
	 | & Health Monitoring     |
	 +-----------+------------+
				 |
				 v
	 +------------------------+
	 | Signal Generation      |
	 +-----------+------------+
				 |
				 v
	 +------------------------+
	 | Webhook Dispatch       |
	 +-----------+------------+
				 |
				 v
	  External Execution Layer

				  

The architecture intentionally separates:

- Market data processing
- Quantitative analysis
- Machine learning inference
- Strategy evaluation
- Portfolio construction
- Risk management
- Signal generation
- Signal delivery
- External trade execution

This separation allows individual components to evolve without
requiring a redesign of the entire platform.

# 3. Quantitative Intelligence Pipeline

	Market Data
		 |
		 v
	Data Processing
		 |
		 v
	Feature Engineering
		 |
		 v
	Market Structure / HTF Models
		 |
		 v
	Strategy & Family Models
		 |
		 v
	Opportunity Evaluation
		 |
		 v
	Portfolio Constraints
		 |
		 v
	Risk Evaluation
		 |
		 v
	Signal Generation

# 3.1 Market Data

The platform consumes historical and live market data for the
supported cryptocurrency trading pairs.

The data pipeline provides the foundation for:

- Price analysis
- Volume analysis
- Volatility analysis
- Technical indicators
- Multi-timeframe features
- Machine learning inference
- Backtesting
- Paper trading
- Live signal generation

# 3.2 Feature Engineering
Raw market data is transformed into quantitative features used by
the machine learning and strategy evaluation layers.

Examples include:

- OHLCV features
- Volatility features
- ATR
- Bollinger Band features
- RSI
- EMA relationships
- EMA slopes
- ADX
- Volume features
- Momentum features
- Trend features
- Market structure features
- Higher-timeframe features

The feature pipeline is designed to maintain consistency between
historical research, backtesting, and production inference.

# 3.3 Machine Learning Models

Machine learning is used at multiple levels of the platform.

The architecture includes models for:

- Market structure
- Higher-timeframe market regime
- Strategy evaluation
- Strategy-family suitability
- Trading opportunity evaluation

The model output is not treated as an unconditional trading decision.

Instead, model predictions are combined with strategy logic,
portfolio constraints, opportunity information, and risk controls
before a signal is generated.

# 3.4 Signal Generation

A signal is generated only after passing through the relevant
quantitative and portfolio-level decision layers.

	ML Prediction
		  +
	Strategy Evaluation
		  +
	Market Context
		  +
	Opportunity
		  +
	Portfolio Constraints
		  +
	Risk Constraints
		  +
	Signal

# 4. Multi-Timeframe & Market Structure
The platform uses multiple execution timeframes:

- 5m
- 15m
- 30m
- 1h

The execution timeframe is evaluated together with higher-timeframe
market context.

The purpose of higher-timeframe models is to provide contextual
information about the broader market environment.

Examples include:

- Trend probability
- Range probability
- Reversal probability
- Market regime
- Higher-timeframe market quality

This allows the system to distinguish between a local trading setup
and the broader market environment in which that setup occurs.

For example, a short-term setup can be evaluated differently
depending on whether the higher timeframe indicates a trending,
ranging, or transitional market.

# 5. Strategy Architecture
The platform contains 25+ pre-built quantitative strategies organized
into strategy families.

The current strategy families are:

TREND_PULLBACK
TREND_CONTINUATION
TREND_REVERSION

BREAKOUT_CONTINUATION
COMPRESSION_BREAKOUT

RANGE_REJECTION
RANGE_REVERSION

LIQUIDITY_TRAP_REVERSAL

Each family can operate across the supported execution timeframes:

- 5m
- 15m
- 30m
- 1h

This creates:
	8 Strategy Families
			x
	4 Execution Timeframes
			=
	32 Family-Timeframe Combinations

For example:
TREND_PULLBACK_15m
BREAKOUT_CONTINUATION_30m
RANGE_REJECTION_30m
TREND_REVERSION_5m

# 5.1 Pre-Built Strategy Model
The platform does not provide users with an unrestricted strategy
builder.

Users select from the strategies and strategy families provided by
the platform.

The underlying proprietary strategy logic remains controlled by the
platform.

This creates a distinction between the platform and traditional
retail bot platforms where users commonly construct strategies using
their own indicator combinations and rules.

The user controls:

- Strategy selection
- Timeframe selection
- Trading-pair universe
- Capital allocation
- Risk parameters
- Portfolio composition

The platform controls the underlying strategy implementation.

# 6. Portfolio Architecture
A portfolio represents an independent quantitative investment
configuration.

Each portfolio has its own:

- Capital allocation
- Pair universe
- Strategy selection
- Strategy groups
- Risk configuration
- Equity curve
- Drawdown
- Trade history
- Performance statistics

A user can create multiple independent portfolios.

	User
	 |
	 +-- Portfolio 1
	 |
	 +-- Portfolio 2
	 |
	 +-- Portfolio 3
 
Each portfolio maintains independent performance statistics and
trading history while using a predefined allocation from the user's
overall capital.

# 6.1 Portfolio Hierarchy
	Portfolio
		|
		+-- Group
		|     |
		|     +-- Strategy Family
		|           |
		|           +-- Strategy
		|                 |
		|                 +-- Trading Pair
		|
		+-- Group
			  |
			  +-- Strategy Family
					|
					+-- Strategy
				

This hierarchy allows users to construct portfolios from different
strategy behaviours and execution timeframes.

# 6.2 Portfolio Groups
Users can create multiple groups within a portfolio.

For example:

	Group 1
	 |
	 +-- TREND_PULLBACK_15m
	 +-- BREAKOUT_CONTINUATION_30m
	 +-- RANGE_REJECTION_30m
	 +-- TREND_REVERSION_5m	 
	 Group 2
	 |
	 +-- COMPRESSION_BREAKOUT_30m
	 +-- BREAKOUT_CONTINUATION_1h
	 +-- LIQUIDITY_TRAP_REVERSAL_30m
	 +-- RANGE_REVERSION_1h
 
Groups provide an additional portfolio-construction layer between
individual strategy families and the overall portfolio.

# 6.3 Trading Pair Universe
Each portfolio can define its own trading-pair universe.
Example:

BTCUSDT
ETHUSDT
SOLUSDT
LINKUSDT
XRPUSDT
AVAXUSDT

Strategies operating within the portfolio use the configured
portfolio-level trading universe.

# 7. Risk Management Architecture
Risk management is implemented hierarchically.
	Portfolio Risk
		  |
		  +-- Group Risk
				 |
				 +-- Family Risk
						|
						+-- Trade Risk
					
The platform supports configurable risk parameters such as:

- Risk per trade
- Family maximum risk
- Group maximum risk
- Portfolio maximum risk
- Leverage
- Maximum drawdown
- Capital allocation

The risk engine acts as a control layer between strategy-generated
opportunities and final signal generation.

	Strategy Signal
		  |
		  v
	Portfolio Constraints
		  |
		  v
	Risk Engine
		  |
		  +---- Risk Allowed ----> Signal
		  |
		  +---- Risk Rejected ---> No Signal
	  
This prevents individual strategies from bypassing portfolio-level
risk constraints.

# 7.1 Symbol-Level Exposure Control
The platform applies a symbol-level position constraint.

Across the configured portfolio:

Only one active trade position is allowed per trading pair/symbol
at a time.

For example, if BTCUSDT already has an active position generated by
one strategy, another strategy cannot independently open another
BTCUSDT position simultaneously within the same portfolio.

This reduces unintended concentration from multiple strategies
generating correlated exposure to the same underlying asset.

# 7.2 Strategy Correlation
The platform also considers strategy correlation when constructing
portfolios.

Different strategies may produce similar positions even when their
underlying logic is different.

Therefore, portfolio construction aims to avoid excessive exposure
to highly correlated strategy combinations.

Risk controls are applied at multiple levels rather than relying
only on the diversification provided by having multiple strategies.


# 8. Health & Adaptive Allocation
The platform monitors strategy-family, group, and portfolio health.
The health architecture is:

	Family Performance
			|
			v
	Family Health Score
			|
			v
	Group Performance
			|
			v
	Group Health Score
			|
			v
	Portfolio Performance
			|
			v
	Portfolio Health Score
			|
			v
	Adaptive Allocation

# 8.1 Family Health
The Family Health Engine monitors the recent behaviour of a strategy
family.

Potential inputs include:

- Recent returns
- Win/loss behaviour
- Drawdown
- Expectancy
- Recent performance stability
- Other family-level performance metrics

The result is a Family Health Score.

The score is used by the adaptive allocation layer to determine
whether exposure to the family should remain unchanged, be reduced,
or be adjusted within predefined allocation limits.

# 8.2 Group Health

The Group Health Engine evaluates the recent behaviour of the
strategies and families contained within a group.

Conceptually:

	Family Performance
		   +
	Family Health
		   |
		   v
	Group Performance
		   |
		   v
	Group Health Score

This provides a higher-level view of the performance of a group rather
than evaluating every family independently.

# 8.3 Portfolio Health
The Portfolio Health Engine evaluates the overall operating condition
of a portfolio.

It considers portfolio-level information such as:

- Performance
- Drawdown
- Risk
- Exposure
- Group performance
- Family contribution
- Trading activity

The resulting Portfolio Health Score provides a consolidated view of
portfolio condition.

# 8.4 Health Score vs Opportunity Score

Health and opportunity represent different dimensions.

Health Score:
	How has this strategy family or group been performing recently?
	
Opportunity Score:
	How attractive is the current market environment for this strategy family?
	
The two signals can therefore be used independently or together.

	Recent Performance
		   |
		   v
	Health Score
		   |
		   |
	Current Market Environment
		   |
		   v
	Opportunity Score
		   |
		   +----------------+
							|
							v
					Adaptive Allocation
				
# 8.5 Adaptive Allocation

The adaptive allocation engine adjusts exposure within predefined
risk and allocation limits.

For example:

	Family A
	Health: Strong
	Opportunity: High
			|
			v
	Allocation maintained / increased within limits


	Family B
	Health: Deteriorating
	Opportunity: Low
			|
			v
	Allocation reduced within limits

	Adaptive allocation does not replace the risk engine.

	Instead:
	Adaptive Allocation
			|
			v
	Risk Constraints
			|
			v
	Final Exposure

This ensures that allocation changes remain subject to portfolio-level
risk controls.

# 9. Backtesting, Paper Trading & Live Signals

The platform provides a progression from historical research to live
signal delivery.

	Historical Data
		  |
		  v
	Backtesting
		  |
		  v
	Paper Trading
		  |
		  v
	Live Signal Generation
		  |
		  v
	Webhook Delivery

# 9.1 Backtesting

Users can evaluate portfolio configurations using historical data.

They can configure:

- Trading pairs
- Timeframes
- Strategies
- Strategy families
- Strategy groups
- Capital allocation
- Risk per trade
- Portfolio risk
- Other supported risk parameters

The backtesting system provides performance information such as:

- Return
- Win rate
- Profit factor
- Sharpe ratio
- Sortino ratio
- Maximum drawdown
- Equity curve
- Trade history

Backtesting is used to evaluate historical behaviour under defined
assumptions.

Historical performance does not guarantee future results.

# 9.2 Paper Trading
The platform provides live paper trading so users can observe how a
portfolio behaves under current market conditions.

Paper trading can display:

- Current positions
- Signal events
- Entry information
- Exit information
- Trade logs
- Portfolio performance
- Risk metrics
- Equity changes

This provides an intermediate validation stage between historical
backtesting and live signal consumption.

# 9.3 Live Signal Generation
After selecting a portfolio configuration, the platform evaluates
live market data against the configured strategy and risk framework.

	Live Market Data
		  |
		  v
	Feature Engineering
		  |
		  v
	ML / Market Structure
		  |
		  v
	Strategy Evaluation
		  |
		  v
	Opportunity Evaluation
		  |
		  v
	Portfolio Constraints
		  |
		  v
	Risk Engine
		  |
		  v
		Signal
	
# 10. Webhook & Execution Separation

A core architectural decision is the separation between signal
generation and trade execution.

The platform generates trading signals but does not require users to
provide exchange API keys to the platform.

Instead, signals are transmitted through webhooks.

	AI Quantitative Platform
			  |
			  v
	   Signal Generator
			  |
			  v
	   Webhook Dispatcher
			  |
			  +------> 3Commas
			  |
			  +------> Trading Platform
			  |
			  +------> User-Owned Endpoint
		  
This allows the platform to remain focused on:

- Market intelligence
- Strategy evaluation
- Portfolio construction
- Risk management
- Signal generation

while execution remains in the user's chosen execution environment.

# 10.1 Webhook Payloads
The platform can support:

Platform-Specific Payloads

Payloads designed for supported third-party execution platforms.

Generic Webhook Payloads

A generic JSON payload can be provided for users operating their own
execution infrastructure.

Signal payloads can contain information such as:

- Symbol
- Direction
- Timeframe
- Entry information
- Stop-loss parameters
- Take-profit parameters
- Strategy or family information
- Signal metadata

The execution platform remains responsible for interpreting the
payload and executing the trade.

# 11. Security, Integrity & Auditability
The architecture is designed to minimize the security boundary
between the signal platform and user trading accounts.

# 11.1 API Credential Separation

The platform does not require users to provide their exchange API
credentials for signal generation.

The architecture is:

	Signal Platform
		  |
		  | Webhook
		  v
	User Execution Platform
		  |
		  | API Credentials
		  v
	Exchange

The user's execution environment is responsible for managing
exchange authentication and account-level permissions.

# 11.2 Signal Integrity
Signals can be represented using cryptographic hashes.

A simplified flow is:
	Generated Signal
		   |
		   v
	Canonical Signal Representation
		   |
		   v
	Cryptographic Hash
		   |
		   v
	Tamper-Evident Record

The purpose is to provide an auditable representation of the signal
record.

A cryptographic hash or blockchain record can help demonstrate that
a recorded signal has not been modified after it was recorded.

It does not guarantee that:

The signal was correct
The signal was profitable
The strategy will continue to perform
Future signals will produce similar results

# 11.3 Risk and Drawdown Notifications
The platform can monitor configured drawdown thresholds.

When a portfolio reaches a predefined drawdown condition, the
platform can notify the user and recommend reviewing or reducing
risk exposure.

Because the platform does not directly manage the user's exchange
account, the user remains responsible for applying corresponding
risk changes in the execution environment.

# 12. Scalability & Future Architecture

The architecture is designed to support additional capabilities
without changing the core portfolio model.

Potential future extensions include:

**Additional Timeframes:**

The existing architecture can be extended to support timeframes such
as:

4H
1D

without redesigning the portfolio hierarchy.

**Additional Trading Pairs:**

The trading universe can be expanded as additional assets become
supported by the market-data and quantitative pipelines.

**Additional Strategy Families:**

New strategy families can be introduced while following the existing
family → group → portfolio architecture.

**Additional Machine Learning Models:**

The modular ML architecture allows additional models to be introduced
for:

- Market regime prediction
- Strategy suitability
- Opportunity prediction
- Volatility prediction
- Risk prediction
- Portfolio intelligence

**Future AI Portfolio Intelligence**

The architecture can later support optional AI-driven portfolio
intelligence layers.

**Family Health AI:**

**Potential capabilities:**
	- Predict family degradation
	- Estimate recovery behaviour
	- Estimate future expectancy
	- Detect early performance deterioration

**Portfolio AI**

**Potential capabilities:**
	- Identify complementary strategy-family combinations
	- Identify combinations associated with elevated drawdown
	- Identify market regimes favourable to specific portfolios
	- Suggest potential portfolio changes
	

# 13. Architectural Summary

The platform can be summarized as:

			 MARKET DATA
				  |
				  v
		FEATURE ENGINEERING
				  |
				  v
	   MARKET STRUCTURE AI
				  |
				  v
	STRATEGY / FAMILY MODELS
				  |
				  v
		OPPORTUNITY ENGINE
				  |
				  v
		 PORTFOLIO ENGINE
				  |
				  v
	  HEALTH / ALLOCATION
				  |
				  v
		   RISK ENGINE
				  |
				  v
		SIGNAL GENERATION
				  |
				  v
		WEBHOOK DISPATCH
				  |
				  v
	  EXTERNAL EXECUTION