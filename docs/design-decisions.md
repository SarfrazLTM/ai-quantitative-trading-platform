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

	Sarfraz

	Niwaas

	Aaleyah