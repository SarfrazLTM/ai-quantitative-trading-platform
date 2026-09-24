# Risk Management

## 1. Overview

The platform uses a multi-layered risk-management architecture to control exposure from individual trades through strategy families, groups, portfolios, and the overall trading account.

Risk management is intentionally separated from signal generation.

A strategy may generate a valid trading signal, but the signal is only allowed to become a trade after passing portfolio, exposure, allocation, and risk constraints.

The core principle is:

> A valid trading signal does not automatically imply that a trade should be taken.

The risk engine evaluates the proposed trade within the context of the user's current portfolio state, existing positions, configured risk limits, drawdown conditions, and available capital.

---

# 2. Risk Management Architecture

			TRADING SIGNAL
				   │
				   ▼
		  ┌──────────────────┐
		  │ Portfolio Check  │
		  └────────┬─────────┘
				   │
				   ▼
		  ┌──────────────────┐
		  │ Exposure Check   │
		  └────────┬─────────┘
				   │
				   ▼
		  ┌──────────────────┐
		  │ Family / Group   │
		  │ Risk Check       │
		  └────────┬─────────┘
				   │
				   ▼
		  ┌──────────────────┐
		  │ Drawdown Check   │
		  └────────┬─────────┘
				   │
				   ▼
		  ┌──────────────────┐
		  │ Position Sizing  │
		  └────────┬─────────┘
				   │
				   ▼
		  ┌──────────────────┐
		  │ Final Risk Check │
		  └────────┬─────────┘
				   │
			┌──────┴──────┐
			│             │
		  APPROVE        REJECT
			│
			▼
		  SIGNAL
		  
Risk controls can operate at multiple levels:

	Account
	   │
	   ├── Portfolio A
	   │      ├── Group A
	   │      │     ├── Family
	   │      │     └── Strategy
	   │      └── Group B
	   │
	   └── Portfolio B
			  ├── Group
			  └── Family
			  
			  
# 3. Risk Management Principles

The architecture follows several core principles:

1. Risk Before Execution

Risk validation occurs before a signal is dispatched for execution.

2. Layered Risk Controls

Risk is evaluated at multiple levels rather than relying on a single global limit.

3. Capital Preservation

The system prioritizes controlled exposure and drawdown management over maximizing the number of trades.

4. Portfolio Awareness

Every proposed trade is evaluated in the context of existing portfolio positions and exposure.

5. Adaptive Risk

Risk allocation can respond to portfolio and strategy-family health while remaining within predefined limits.

6. Fail-Safe Behaviour

If required risk information is unavailable or invalid, the system should reject or defer the trade rather than bypassing risk controls.


# 4. User Risk Configuration

Risk parameters are configurable at the portfolio level and are persisted as part of the user's portfolio configuration.

Typical parameters include:

- Selected trading pairs
- Selected strategy families
- Selected groups
- Base risk per trade
- Base family risk
- Base group risk
- Base portfolio risk
- Leverage
- Maximum drawdown
- Allocation constraints
- Webhook configuration

The configuration flow is:

	USER
	 │
	 ▼
	Laravel Control Plane
	 │
	 ▼
	Configuration Validation
	 │
	 ▼
	MongoDB
	 │
	 ▼
	Configuration Loader
	 │
	 ▼
	Redis Runtime Configuration
	 │
	 ▼
	Python Quant Runtime
	 │
	 ▼
	Risk Engine
	
MongoDB acts as the persistent configuration store, while Redis can provide fast runtime access to active configuration.


# 5. Risk Hierarchy

The platform applies risk controls across multiple levels.

	Account
	   │
	   ▼
	Portfolio
	   │
	   ▼
	Group
	   │
	   ▼
	Strategy Family
	   │
	   ▼
	Strategy
	   │
	   ▼
	Trade
	
This hierarchy allows the system to prevent concentration of risk even when individual strategies appear acceptable in isolation.


# 6. Trade-Level Risk

Trade-level risk represents the maximum amount of portfolio capital that can be exposed to a single trade according to the configured risk model.

The general relationship is:

	Portfolio Capital
		   │
		   ▼
	Risk Per Trade
		   │
		   ▼
	Allowed Trade Risk
		   │
		   ▼
	Stop-Loss Distance
		   │
		   ▼
	Position Size
	
The actual position size is constrained by additional portfolio and exposure limits.

This prevents position size from being determined solely by the trading signal.


# 7. Position Sizing

Position sizing converts risk constraints into an appropriate position quantity.

Conceptually:

	Risk Budget
		÷
	Stop-Loss Distance
		=
	Position Size
	
	
The calculated position is then checked against:

- Maximum allocation
- Leverage limits
- Portfolio exposure
- Symbol exposure
- Family allocation
- Group allocation
- Available capital

The final position size is therefore the result of both risk budget and portfolio constraints.


# 8. Portfolio-Level Risk

Each portfolio has an independent risk configuration.

Portfolio-level controls may include:

- Maximum portfolio risk
- Portfolio allocation
- Maximum drawdown
- Current drawdown
- Open trade exposure
- Capital utilization
- Maximum concurrent exposure

Conceptually:

	Portfolio Risk Budget
			│
			├── Group A
			├── Group B
			├── Group C
			└── Group D
			
The portfolio risk budget acts as a ceiling that downstream components must respect.


# 9. Group-Level Risk

A portfolio can contain multiple groups of strategy-family/timeframe combinations.

Group-level risk controls prevent one group from consuming excessive portfolio risk.

	Portfolio
		│
		├── Group A → Risk Budget
		│
		├── Group B → Risk Budget
		│
		└── Group C → Risk Budget
		
A trade can therefore be rejected even when the individual strategy has sufficient risk capacity if the containing group has already reached its risk limit.


# 10. Family-Level Risk

Strategy families represent a higher-level risk category.

Examples include:

- Trend Pullback
- Trend Continuation
- Trend Reversion
- Breakout Continuation
- Compression Breakout
- Range Rejection
- Range Reversion
- Liquidity Trap Reversal

Family-level allocation prevents multiple strategies within the same family from collectively exceeding the intended exposure.


	Strategy Family
		  │
		  ├── Strategy A
		  ├── Strategy B
		  └── Strategy C
				│
				▼
		   Family Risk Budget
		   
This is particularly important when several strategies respond to similar market conditions.


# 11. Symbol-Level Exposure

The platform also considers exposure at the trading-symbol level.

For example:

	BTCUSDT
	   │
	   ├── Trend Strategy
	   ├── Breakout Strategy
	   └── Reversion Strategy
	   
Although these may belong to different strategies or families, they can still create concentrated exposure to the same underlying asset.

A core portfolio rule is:

Only one active trade position per symbol across the relevant portfolio strategy groups.

This reduces unintended accumulation of correlated positions on the same asset.


# 12. Correlation and Concentration Risk

Diversification is not determined solely by the number of strategies.

Multiple strategies can generate similar exposure because they may:

- Trade the same symbol
- Trade correlated symbols
- Respond to the same market regime
- Use similar directional signals
- Belong to related strategy families

Therefore, the risk architecture considers concentration at multiple levels.


	Many Strategies
		  │
		  ▼
	Potentially Similar Exposure
		  │
		  ▼
	Portfolio Concentration
		  │
		  ▼
	Risk Control
	
The objective is to avoid treating correlated strategies as independent sources of risk.


# 13. Family Health

Family Health measures the recent performance and risk condition of a strategy family.

It can incorporate information such as:

- Recent performance
- Drawdown
- Win rate
- Profit factor
- Trade behaviour
- Stability
- Recent losses

Conceptually:

	Family Performance
		   +
	Family Risk State
		   +
	Recent Behaviour
		   │
		   ▼
	   Family Health
	   
Health answers the question:

"How has this strategy family been behaving recently?"

Health is different from market opportunity.


# 14. Adaptive Allocation

The platform can dynamically adjust capital allocation based on family and portfolio conditions.

The adaptive allocation layer operates within predefined risk boundaries.

Conceptually:

	Base Allocation
		  │
		  ▼
	Family Health
		  │
		  +
	Opportunity Score
		  │
		  +
	Portfolio State
		  │
		  ▼
	Adaptive Allocation
		  │
		  ▼
	Risk Constraints
		  │
		  ▼
	Final Allocation
	
	
# 15. Risk Budgets and Allocation Limits


Each level can have a maximum allocation or risk budget.

Conceptually:

	Portfolio Risk Limit
			│
			▼
	Group Risk Limit
			│
			▼
	Family Risk Limit
			│
			▼
	Trade Risk Limit
	

The effective trade risk must remain within all applicable constraints.


# 16. Drawdown Management

Drawdown is monitored at multiple levels.

The system can track:

- Trade-level losses
- Strategy drawdown
- Family drawdown
- Group drawdown
- Portfolio drawdown

Portfolio drawdown is particularly important because it represents the combined effect of all active strategies.

Conceptually:

	Peak Portfolio Equity
			│
			▼
	Current Equity
			│
			▼
	Current Drawdown
	
	
# 17. Drawdown Controller

A drawdown controller can modify the amount of risk available to new trades.

Conceptually:

	Normal Drawdown
		  │
		  ▼
	Normal Risk

	Elevated Drawdown
		  │
		  ▼
	Reduced Risk

	Maximum Drawdown
		  │
		  ▼
	Trading Restricted / Paused
	
The exact thresholds and proprietary risk formulas are intentionally not exposed in the public repository.


# 18. Risk Decision Flow

The complete risk decision process can be represented as:

				 SIGNAL
					│
					▼
			Is Portfolio Active?
					│
					▼
			Symbol Exposure Check
					│
					▼
			Portfolio Risk Check
					│
					▼
			  Group Risk Check
					│
					▼
			 Family Risk Check
					│
					▼
			  Drawdown Check
					│
					▼
			 Allocation Check
					│
					▼
			Position Size Check
					│
					▼
			  Final Risk Check
					│
			 ┌──────┴──────┐
			 │             │
		  APPROVE        REJECT
			 │
			 ▼
		   SIGNAL
		   

# 19. Risk Rejection

A signal can be rejected even when the underlying strategy generates a valid entry.

Possible rejection conditions include:

- Portfolio risk limit reached
- Group risk limit reached
- Family risk limit reached
- Symbol already has an active position
- Maximum drawdown condition reached
- Insufficient allocation capacity
- Invalid position size
- Invalid risk configuration
- Missing runtime configuration
- Leverage constraint exceeded
- Exposure constraint exceeded

This separation is important because signal generation and trade authorization are different responsibilities.


# 20. Risk Analytics

The platform can expose risk-related analytics at multiple levels.

Portfolio
- Current risk
- Maximum risk
- Current drawdown
- Maximum drawdown
- Open exposure
- Capital utilization

Group
- Group allocation
- Group exposure
- Group drawdown
- Active positions

Family
- Family allocation
- Family risk
- Family drawdown
- Health score
- Opportunity score

Symbol
- Current position
- Exposure
- Direction
- Allocation
- Related strategy exposure