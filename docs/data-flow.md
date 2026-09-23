# AI Quantitative Trading Platform — Data Flow

## 1. Overview

The data-flow architecture describes how market data moves through the
quantitative trading platform, from historical and live market-data
ingestion through feature engineering, machine learning inference,
strategy evaluation, portfolio and risk controls, signal generation,
and webhook delivery.

The platform maintains two closely related data flows:

1. Research and training flow
2. Production and live-signal flow

The research flow is responsible for preparing data and developing
models, while the production flow uses validated models to process
live market data and generate signals.

The overall flow is:

	Market Data
		↓
	Data Processing
		↓
	Feature Engineering
		↓
	Market Structure / HTF Intelligence
		↓
	Strategy Evaluation
		↓
	Portfolio Evaluation
		↓
	Risk Evaluation
		↓
	Signal Generation
		↓
	Webhook Delivery
		↓
	External Execution Platform
	
# 2. Data Sources
The platform works with historical and live market data for the
supported cryptocurrency trading-pair universe.

The current platform supports:

49 cryptocurrency trading pairs
- 5m execution timeframe
- 15m execution timeframe
- 30m execution timeframe
- 1h execution timeframe

Examples of supported pairs include:

	BTCUSDT
	ETHUSDT
	SOLUSDT
	LINKUSDT
	XRPUSDT
	AVAXUSDT
	
Market data provides the foundation for:

- Historical research
- Feature engineering
- Model training
- Backtesting
- Paper trading
- Live signal generation
- Performance analysis

# 3. Historical Data Flow
Historical market data is used for model development, strategy
evaluation, and backtesting.

	Historical Market Data
			↓
	Data Validation
			↓
	Data Cleaning / Normalization
			↓
	Timeframe Processing
			↓
	Feature Engineering
			↓
	Training / Backtesting Dataset
	
The historical pipeline is designed to maintain consistent
transformations between research and production wherever the same
features are required.

This reduces the risk of discrepancies between features used during
model development and features generated during live inference.

# 4. Live Market Data Flow
	Live Market Data
			↓
	Data Validation
			↓
	Normalization
			↓
	Timeframe Processing
			↓
	Feature Generation
			↓
	Current Market State
	
The resulting market state is then passed to the quantitative
intelligence pipeline.

The live pipeline is designed to process multiple trading pairs and
multiple execution timeframes independently.

# 5. User Portfolio Configuration Flow
User portfolio configuration is maintained separately from the market
data pipeline.

The user configures the portfolio through the application control
plane. These settings are persisted in MongoDB and made available to
the Python quantitative runtime through a low-latency runtime
configuration layer such as Redis.

The configuration includes:

- Trading-pair selection
- Strategy-family selection
- Group selection
- Base family risk
- Base group risk
- Base risk per trade
- Base portfolio risk
- Leverage configuration
- Maximum drawdown
- Webhook configuration
- Portfolio allocation
- Portfolio status

The logical flow is:

	User
	  ↓
	Laravel Control Plane
	  ↓
	Configuration Validation
	  ↓
	MongoDB
	  ↓
	Runtime Configuration Cache
	  ↓
	Python Quantitative Runtime

MongoDB acts as the persistent source of truth, while Redis can be
used as a low-latency runtime configuration layer.

Configuration versions should be used to ensure that the Python
runtime is operating against a consistent portfolio configuration.

                         USER
                           |
                           v
                 Laravel Control Plane
                           |
                     Validate / Save
                           |
                           v
                       MongoDB
                           |
                  Persistent State
                           |
                           v
                 Configuration Loader
                           |
                           v
                         Redis
                           |
                  Runtime Configuration
                           |
                           v
                 Python Quant Runtime

# 6. Multi-Timeframe Data Flow
The platform does not evaluate a trading opportunity using only the
execution timeframe.

The execution timeframe is combined with higher-timeframe market
context.

Conceptually:

			 Market Data
				  |
	+---------------+---------------+
	|               |               |
	↓               ↓               ↓
	Execution       Higher TF       Higher TF
	Timeframe       Context 1       Context 2
	|               |               |
	+---------------+---------------+
				  |
				  ↓
		 Feature Engineering
				  |
				  ↓
		Market Context Vector
		
The exact higher-timeframe relationships depend on the execution
configuration and model architecture.

Higher-timeframe models can provide information such as:

- Trend probability
- Range probability
- Reversal probability
- Market regime
- Market quality

This context is provided to downstream strategy and signal-evaluation
components.

# 7. Feature Engineering Data Flow
Raw market data is transformed into quantitative features.

	OHLCV Data
		↓
	Technical Indicators
		↓
	Volatility Features
		↓
	Momentum Features
		↓
	Trend Features
		↓
	Volume Features
		↓
	Market Structure Features
		↓
	Higher-Timeframe Features
		↓
	Model Feature Vector
	
Examples of quantitative features include:

- ATR
- Bollinger Bands
- RSI
- EMA relationships
- EMA slopes
- ADX
- Volume-derived features
- Volatility measures
- Momentum measures
- Market structure features
- Higher-timeframe features

The feature vector becomes the primary input to the machine learning
and strategy-evaluation layers.

# 8. Machine Learning Data Flow

The machine learning layer operates on the engineered feature set.

The production inference flow is:

	Feature Vector
		  ↓
	Market Structure Models
		  ↓
	Higher-Timeframe Predictions
		  ↓
	Strategy / Family Models
		  ↓
	Model Outputs
	
Market structure models provide contextual information about the
current market environment.

Strategy and strategy-family models evaluate the suitability of
available trading opportunities.

A model prediction is not automatically converted into a trade.

Instead, model outputs are passed to subsequent strategy, portfolio,
and risk layers.

# 9. Strategy Evaluation Data Flow
The strategy layer combines current market information with model
outputs and the selected strategy configuration.

	Market Features
		   +
	HTF Predictions
		   +
	Strategy Configuration
		   +
	Current Market State
		   ↓
	Strategy Evaluation
		   ↓
	Candidate Trading Opportunity
	
The platform contains multiple pre-built strategies organized into
strategy families.

Users select from the available strategies and families rather than
creating arbitrary strategy logic.

The strategy layer therefore produces a candidate opportunity rather
than bypassing the portfolio and risk architecture.

# 10. Health and Adaptive Allocation Data Flow
Trade results and portfolio performance continuously generate
performance information.

	Trade Results
		  ↓
	Performance Metrics
		  ↓
	Family Health
		  ↓
	Group Health
		  ↓
	Portfolio Health
	
These health measurements can then influence adaptive allocation.

	Family Health
		  +
	Group Health
		  +
	Portfolio Health
		  +
	Current Opportunity
		  ↓
	Adaptive Allocation
	
The purpose of adaptive allocation is to adjust exposure within
predefined allocation and risk boundaries.

For example:

	Strong Family Health
			↓
	Allocation maintained / increased
			↓
	Within Risk Limits


	Deteriorating Family Health
			↓
	Allocation reduced
			↓
	Within Risk Limits
	
Adaptive allocation therefore operates inside the portfolio and risk
framework rather than independently overriding it.

# 11. Risk Data Flow
Risk controls are evaluated after candidate opportunities are
identified and before final signal delivery.

	Candidate Signal
		   ↓
	Trade Risk Check
		   ↓
	Family Risk Check
		   ↓
	Group Risk Check
		   ↓
	Portfolio Risk Check
		   ↓
	Exposure Check
		   ↓
	Drawdown Check
		   ↓
	Risk Decision
	
The risk engine can evaluate parameters such as:

- Risk per trade
- Family maximum risk
- Group maximum risk
- Portfolio maximum risk
- Leverage
- Maximum drawdown
- Existing exposure

The final decision is:

	Risk Approved
		  ↓
	Signal Generation
	
or:

	Risk Rejected
		  ↓
	No Signal
	
Risk management therefore acts as an independent control layer rather
than relying entirely on individual strategy logic.

# 12. Symbol-Level Exposure Flow
The platform applies a symbol-level exposure constraint.

Within a configured portfolio:
Only one active trade position is allowed per trading pair/symbol
at a time.

Conceptually:

	Multiple Strategy Signals
			  ↓
		Same Symbol?
			  ↓
		  Exposure Check
		   /         \
		  /           \
	Existing        No Existing
	Position        Position
	   ↓                ↓
	Reject /        Continue
	Filter
	
This reduces unintended concentration when multiple strategies
generate signals for the same underlying asset.

# 13. Signal Generation Flow
After passing through strategy, portfolio, health, allocation, and risk
layers, an approved opportunity becomes a trading signal.

	Market Data
		 +
	Features
		 +
	ML Predictions
		 +
	Strategy Evaluation
		 +
	Portfolio State
		 +
	Health / Allocation
		 +
	Risk State
		 ↓
	Signal Generation
		 ↓
	Signal Payload
	
The resulting payload can contain information such as:

- Symbol
- Direction
- Timeframe
- Entry information
- Stop-loss parameters
- Take-profit parameters
- Strategy or family information
- Signal metadata

# 14. Webhook Data Flow
The platform separates signal generation from execution.
	Signal Generator
		   ↓
	Signal Validation
		   ↓
	Payload Construction
		   ↓
	Webhook Dispatcher
		   ↓
	User Webhook Endpoint
		   ↓
	External Execution Platform
	
Two types of webhook integration can be supported.

**Platform-Specific Webhook:**

Payloads can be formatted for supported third-party execution
platforms.

	Signal
	  ↓
	Platform-Specific JSON
	  ↓
	Third-Party Execution Platform
	
**Generic Webhook:**

Users can also receive a generic JSON payload through their own
webhook endpoint.

	Signal
	  ↓
	Generic JSON
	  ↓
	User-Owned Endpoint
	  ↓
	User Execution Infrastructure
	
The signal platform therefore remains independent of the user's
execution environment.

# 15 Data Storage and Runtime State
Different categories of data require different storage and access
patterns.

At a logical level, the platform manages:

	Market Data
		 ↓
	Historical / Time-Series Storage

	Runtime Market State
		 ↓
	Runtime Data Store

	Model Outputs
		 ↓
	Inference / Runtime State

	Signals
		 ↓
	Signal Records

	Portfolio State
		 ↓
	Portfolio / Performance Storage

	Trade History
		 ↓
	Trade Records

	Audit Information
		 ↓
	Tamper-Evident Hash Records
	
The exact database schema and internal storage implementation are
intentionally abstracted from this public architecture document.

# 16. End-to-End Production Data Flow
The complete live data flow can be summarized as:

                         MARKET DATA
                              |
                              v
                      DATA PROCESSING
                              |
                              v
                    FEATURE ENGINEERING
                              |
                              v
                 MULTI-TIMEFRAME CONTEXT
                              |
                              v
                   MARKET STRUCTURE AI
                              |
                              v
                  STRATEGY / FAMILY AI
                              |
                              v
                     OPPORTUNITY SCORE
                              |
                              v
                    PORTFOLIO ENGINE
                              |
                              v
               HEALTH & ADAPTIVE ALLOCATION
                              |
                              v
                        RISK ENGINE
                              |
                              v
                    SIGNAL GENERATION
                              |
                              v
                    PAPER TRADING / LIVE
                              |
                              v
                     WEBHOOK DISPATCH
                              |
                              v
                EXTERNAL EXECUTION PLATFORM
                              |
                              v
                       TRADE RESULT
                              |
                              v
                   PERFORMANCE METRICS
                              |
                              v
					HEALTH / ALLOCATION FEEDBACK
					
					
The architecture therefore forms a continuous quantitative feedback
loop rather than a one-way signal-generation pipeline.

The system separates market intelligence, strategy evaluation,
portfolio construction, risk management, and execution while allowing
performance information to flow back into portfolio health and
adaptive allocation.