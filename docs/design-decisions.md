# Design Decisions

# 1. Overview

This document records the major architectural and engineering decisions behind the quantitative trading platform.

The objective is to explain not only what was implemented, but why particular design choices were made.

The decisions focus on:

- Scalability
- Separation of concerns
- Quantitative correctness
- Production reliability
- Risk isolation
- Multi-user architecture
- ML consistency
- Data integrity
- Security
- Maintainability

Proprietary strategy logic, alpha-generating features, model weights, and production secrets are intentionally excluded.


# 2. Separate Control Plane from Quantitative Runtime

### Decision

Use Laravel for the control plane and Python for quantitative computation.

	Laravel
	   │
	   ├── Users
	   ├── Portfolio Configuration
	   ├── APIs
	   └── Administration
			  │
			  ▼
		   Redis
			  │
			  ▼
	Python Quantitative Runtime
	   │
	   ├── Features
	   ├── ML
	   ├── Strategy
	   ├── Portfolio
	   └── Risk
	   
	   
**Why**

The control plane and quantitative runtime have different responsibilities and technology requirements.

Python provides the ecosystem required for:

- Numerical computing
- Machine learning
- Time-series processing
- Quantitative analysis

Laravel provides a mature application layer for:

- User management
- APIs
- Configuration
- Business workflows

Keeping them separate reduces coupling and allows each layer to evolve independently.

# 3. Python for Quantitative Processing

Decision

Use Python as the primary quantitative computation environment.

Why

The quantitative pipeline depends on an extensive Python ecosystem for:

- Pandas
- NumPy
- Scikit-learn
- XGBoost
- Statistical processing
- ML experimentation
- Time-series analysis

This also keeps research and production inference within a consistent technical ecosystem.

# 4. MongoDB for Persistent Application State

Decision

Use MongoDB for persistent user, portfolio, configuration, and application-level records.

Why

The platform contains flexible and evolving structures such as:

- Portfolio configurations
- Strategy selections
- Groups
- Risk parameters
- Webhook configuration
- Backtest metadata
- Signal records
- Performance information

A document-oriented data model provides flexibility as the platform evolves.

MongoDB remains the persistent source of truth for configuration.

# 5. Redis for Runtime State

Decision

Use Redis as the high-speed runtime/cache layer.

Why

The quantitative runtime frequently requires access to changing information such as:

- Active portfolio configuration
- Current positions
- Risk state
- Allocation state
- Configuration versions
- Processing state

Querying the primary database for every market event would create unnecessary latency and database load.

Therefore:

	MongoDB
	   ↓
	Configuration Loader
	   ↓
	Redis
	   ↓
	Python Runtime
	
Redis is treated as a runtime layer rather than the permanent source of truth.


# 6. Shared Quantitative Computation

Decision

Perform market, feature, ML, strategy, and family-level calculations as shared computation wherever possible.

Why

The platform is designed as a multi-user SaaS system.

If the same market event were independently processed for every user:

	5,000 Users
	×
	Feature Engineering
	×
	ML Inference
	×
	Strategy Evaluation
	
the computational cost would grow unnecessarily

Instead:

	Market Event
		 ↓
	Shared Quantitative Processing
		 ↓
	Candidate Signal
		 ↓
	Portfolio Fan-Out
	
This allows expensive computations to be reused across users.

# 7. User-Specific Portfolio Processing

Decision

Perform portfolio, group, allocation, and risk evaluation separately for each user's portfolio.

Why

Users can configure different:

- Symbols
- Strategy families
- Groups
- Risk limits
- Allocations
- Leverage
- Drawdown limits
- Existing positions

Therefore, these decisions cannot be treated as globally shared calculations.

The architecture uses:

	Shared Intelligence
			↓
	Portfolio Router
			↓
	User Portfolio Evaluation
	
This provides a clear boundary between global market intelligence and user-specific decision making.


# 8. Separate Family Health from Group and Portfolio Health

Decision

Use three levels of health evaluation:

	Family Health
		 ↓
	Group Health
		 ↓
	Portfolio Health
	
Why

Family Health represents the behaviour of a strategy family across the platform and can therefore be calculated as shared intelligence.

Group Health depends on how an individual user has combined families into a group.

Portfolio Health evaluates the overall behaviour of the user's portfolio.

This hierarchy avoids recalculating global family behaviour independently for every user.


# 9. Separate Signal Generation from Risk

Decision

The strategy layer generates candidate opportunities, while the risk layer authorizes exposure.

	Strategy
	   ↓
	Candidate Signal
	   ↓
	Portfolio Context
	   ↓
	Risk Evaluation
	   ↓
	Approved Signal
	
Why

A strategy should not have authority to bypass portfolio risk controls.

This separation allows centralized control over:

- Position exposure
- Portfolio risk
- Drawdown
- Symbol concentration
- Family exposure
- Group exposure

It also makes the risk engine independently testable.

# 10. Multi-Timeframe Market Context

Decision

Use higher-timeframe information as context for lower-timeframe decisions.

Example:

	15m → 1h / 4h
	30m → 2h / 8h
	1h  → 4h / 1D
	
Why

Market behaviour at an execution timeframe can be strongly influenced by broader market structure.

Higher-timeframe information provides contextual information while allowing execution decisions to remain at the selected timeframe.

All higher-timeframe information must remain point-in-time correct.


# 11. Time-Series-Aware ML Validation

Decision

Use chronological validation rather than random dataset shuffling.

Why

Financial observations are time-dependent.

Randomly mixing future observations into training data can produce unrealistic validation results.

The ML pipeline therefore uses time-series-aware validation and chronological data processing.


# 12. Asynchronous Webhook Delivery

Decision

Separate signal generation from webhook delivery using a queue and worker architecture.

	Signal
	  ↓
	Webhook Queue
	  ↓
	Webhook Worker
	  ↓
	User Endpoint
	
Why

External endpoints can be:

- Slow
- Temporarily unavailable
- Rate limited
- Unreachable

Webhook delivery should not block the quantitative decision pipeline.

Asynchronous delivery allows retry and failure handling independently


# 13. Worker-Based Architecture

Decision

Use worker-based processing for workloads that can be executed asynchronously.

Logical worker responsibilities include:

- Family Health
- Group Health
- Portfolio Health
- Risk evaluation
- Webhook delivery

These can initially run on shared worker infrastructure and later be separated into independent worker pools when scale requires it.

Why

This provides:

- Fault isolation
- Retry handling
- Independent scaling
- Better workload management
- Clear service boundaries


# 14. Backtesting and Production Consistency

Decision

Keep the backtesting decision pipeline as close as practical to the production pipeline.

Why

A major source of quantitative-system failure is a difference between:

	Research / Backtest Logic
	
and:

	Production Logic
	
Using shared concepts and implementations where practical reduces research-to-production discrepancies.


# 15. Observability as a First-Class Concern

Decision

Production components should expose logs, metrics, health information, and traceable event identifiers.

Why

A distributed quantitative system is difficult to debug without visibility into:

	Market Event
		 ↓
	Feature Processing
		 ↓
	     ML
		 ↓
	  Strategy
		 ↓
	 Portfolio
		 ↓
	    Risk
		 ↓
	   Signal
		 ↓
	  Webhook
	  
Each stage should be observable enough to determine where a failure or unexpected result occurred.