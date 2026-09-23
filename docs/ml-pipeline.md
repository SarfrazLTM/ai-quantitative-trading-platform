# Machine Learning Pipeline

## 1. Overview

The platform uses machine learning as a quantitative decision-support layer within a multi-timeframe systematic trading architecture.

The ML pipeline transforms historical market data into engineered features, generates training labels, trains time-series-aware models, validates their performance, and deploys versioned models for real-time inference.

The production ML pipeline is designed to support:

- Market structure prediction
- Higher-timeframe market context
- Strategy and strategy-family evaluation
- Probability-based decision making
- Multi-timeframe quantitative analysis
- Real-time signal generation
- Continuous model evaluation and improvement

Proprietary strategy rules, alpha-generating features, model weights, thresholds, and production model artifacts are intentionally excluded from this repository.

# 2. ML Pipeline Architecture

			 HISTORICAL MARKET DATA
					   │
					   ▼
			   DATA PREPROCESSING
					   │
					   ▼
			   FEATURE ENGINEERING
					   │
					   ▼
				LABEL GENERATION
					   │
					   ▼
				TRAINING DATASET
					   │
					   ▼
				 MODEL TRAINING
					   │
					   ▼
			  TIME-SERIES VALIDATION
					   │
					   ▼
				MODEL EVALUATION
					   │
					   ▼
				MODEL VERSIONING
					   │
					   ▼
				PRODUCTION MODEL
					   │
					   │
		 ┌─────────────┴─────────────┐
		 │                           │
		 ▼                           ▼
	LIVE MARKET DATA            MODEL ARTIFACT
		 │                           │
		 ▼                           │
	FEATURE ENGINEERING              │
		 │                           │
		 └──────────────┬────────────┘
						▼
				   ML INFERENCE
						│
						▼
				MODEL PREDICTIONS
						│
						▼
			STRATEGY / FAMILY ENGINE
						│
						▼
				PORTFOLIO ENGINE
						│
						▼
				   RISK ENGINE
						│
						▼
					 SIGNAL
					 
# 3. Data Preparation
Historical OHLCV market data is collected for supported cryptocurrency trading pairs and multiple timeframes.

The data preparation stage is responsible for:

- Timestamp normalization
- Missing-data handling
- Duplicate detection
- OHLCV validation
- Chronological ordering
- Timeframe alignment
- Data consistency checks
- Removal of invalid observations

The pipeline preserves chronological ordering because financial time-series data must not be treated as independently and identically distributed observations.

# 4. Feature Engineering
Raw market data is transformed into quantitative features used by the ML models.
Feature categories include:

Price and Trend Features
- Returns
- Moving averages
- EMA relationships
- EMA slopes
- Price distance from moving averages
- Trend persistence

Volatility Features
- ATR
- Normalized ATR
- Bollinger Band width
- Volatility expansion/contraction
- Volatility regime characteristics

Momentum Features
- RSI
- Momentum measurements
- Rate of change
- Trend strength

Volume Features
- Volume moving averages
- Relative volume
- Volume expansion
- Volume-based market activity

Market Structure Features
- Trend characteristics
- Range characteristics
- Breakout conditions
- Reversal characteristics
- Multi-timeframe context

Higher-Timeframe Features

The system incorporates higher-timeframe information into lower-timeframe decision making.

Examples include:

	Execution Timeframe → Higher-Timeframe Context
	
	5m → 30m / 2h
	15m → 1h / 4h
	30m → 2h / 8h
	1h  → 4h / 1D
	
The exact feature definitions and proprietary transformations are intentionally excluded from the public repository.

# 5. Label Generation

Training labels are generated from future market behaviour over predefined evaluation horizons.

The objective is to teach models to estimate future market conditions or trade-related outcomes rather than simply reproduce historical indicator values.

Depending on the model, targets may represent:

- Market direction
- Trend probability
- Reversal probability
- Strategy suitability
- Expected trade outcome
- Strategy-family suitability

Label generation is performed chronologically to prevent future information from leaking into the feature set.

# 6. Multi-Timeframe Machine Learning

The platform uses a hierarchical multi-timeframe approach.

Rather than evaluating an execution timeframe in isolation, models can incorporate information from higher timeframes.

For example:

	30m Execution
		  │
		  ├── 30m Market Features
		  │
		  ├── 2H Market Context
		  │
		  └── 8H Market Context
		  
Higher-timeframe models provide contextual predictions that can be consumed by downstream models and decision engines.

This allows the system to distinguish between:

- Local market behaviour
- Intermediate market structure
- Higher-timeframe regime/context


# 7. Model Architecture
The platform primarily uses tree-based machine learning models for structured quantitative features.

The current implementation uses models from the XGBoost ecosystem together with scikit-learn components.

Examples include:

- XGBClassifier
- XGBRegressor
- MultiOutputRegressor
- TimeSeriesSplit

Different models can serve different levels of the quantitative decision pipeline.

Conceptually:

	Market Data
		│
		▼
	Feature Engineering
		│
		▼
	Market Structure Models
		│
		▼
	Higher-Timeframe Predictions
		│
		▼
	Strategy / Family Models
		│
		▼
	Decision / Composite Layer
	
The architecture allows models to remain independently trainable and versioned.


# 8. Training Pipeline
The training workflow follows a reproducible sequence:

	Raw Historical Data
			↓
	Data Validation
			↓
	Feature Engineering
			↓
	Label Generation
			↓
	Dataset Construction
			↓
	Time-Series Split
			↓
	Model Training
			↓
	Validation
			↓
	Evaluation
			↓
	Model Selection
			↓
	Model Versioning
	
Training is performed independently from production inference.

This separation prevents experimental training workflows from directly affecting the live signal-generation pipeline.


# 9. Time-Series Validation

Traditional random train/test splitting is avoided for time-dependent market data.

The platform uses chronological validation techniques such as:

	Training Period
	───────────────────────►
						 Validation Period
						 ─────────────────►
										  Future
										  
Time-series cross-validation is used to evaluate whether models generalize across different historical market periods.

This helps reduce:

- Look-ahead bias
- Temporal leakage
- Unrealistic validation results

The validation process is designed to better approximate how a model would behave when deployed on future unseen market data.

# 10. Model Evaluation

Models are evaluated using metrics appropriate to their prediction objective.

Depending on the model, evaluation may include:

**Classification**
- Accuracy
- Precision
- Recall
- F1 score
- Confusion matrix
- Probability quality

**Regression**
- MAE
- RMSE
- Prediction error
- Directional usefulness

Trading-Oriented Evaluation

Model predictions are ultimately evaluated within the broader trading workflow.

Relevant measurements may include:

- Strategy return
- Win rate
- Profit factor
- Sharpe ratio
- Sortino ratio
- Maximum drawdown
- Recovery characteristics
- Trade distribution

Model accuracy alone is not considered sufficient evidence of trading usefulness.

# 11. Probability-Based Predictions

The ML layer produces probabilities or continuous prediction scores rather than relying exclusively on binary decisions.

Conceptually:

	Model
	  │
	  ▼
	Prediction
	  │
	  ├── Trend Probability
	  ├── Reversal Probability
	  ├── Strategy Suitability
	  └── Trade Outcome Probability
	  
These predictions are consumed by downstream quantitative components.

The final trading decision can combine:

- ML predictions
- Market structure
- Strategy suitability
- Portfolio constraints
- Risk conditions
- Current market state

This creates a separation between prediction and decision making.


# 12. Training vs Production Inference

Training and inference are deliberately separated.

Research / Training Environment

	Historical Data
		  ↓
	Feature Engineering
		  ↓
	Label Generation
		  ↓
	Model Training
		  ↓
	Validation
		  ↓
	Evaluation
		  ↓
	Model Version
	
Production Environment

	Live Market Data
		  ↓
	Feature Engineering
		  ↓
	Load Approved Model
		  ↓
	Inference
		  ↓
	Predictions
		  ↓
	Strategy / Portfolio Decision
		  ↓
	Risk Validation
		  ↓
	Signal
	
The production environment should use an approved model version rather than dynamically retraining models during live signal generation.

# 13. Model Versioning

Models are treated as versioned production artifacts.

A model version should be associated with relevant metadata such as:

- Model type
- Training period
- Feature set version
- Target definition
- Training configuration
- Validation results
- Evaluation period
- Model artifact version
- Deployment status

This makes model behaviour reproducible and allows previous model versions to be identified and compared.

# 14. Production Inference
During live operation, the ML system receives market data from the quantitative runtime.

The inference flow is:

	Live Market Data
		   ↓
	Timeframe Processing
		   ↓
	Feature Engineering
		   ↓
	Feature Validation
		   ↓
	Model Inference
		   ↓
	ML Predictions
		   ↓
	Strategy / Family Evaluation
		   ↓
	Portfolio Evaluation
		   ↓
	Risk Engine
		   ↓
	Signal Generation
	
Inference must use the same feature definitions and transformations expected by the trained model.

This is critical to prevent training-serving skew.

# 15. ML Safety and Failure Handling

ML predictions are treated as one component of the trading decision rather than an unconditional trading command.

The downstream system can apply additional controls such as:

- Prediction thresholds
- Market-state filters
- Portfolio constraints
- Family health conditions
- Drawdown controls
- Symbol exposure limits
- Risk-per-trade limits
- Maximum portfolio risk
- Signal validation

If an ML model or dependent service becomes unavailable, the system should fail safely rather than generate uncontrolled trading signals.


# 16. Model Monitoring

Production models should be monitored for changes in behaviour and data quality.

Monitoring areas include:

- Feature availability
- Feature distribution
- Prediction distribution
- Model confidence
- Model performance
- Data drift
- Prediction drift
- Error rates
- Inference latency
- Model version

Monitoring allows the system to identify when a model may no longer represent current market conditions.

# 17. Research-to-Production Lifecycle
The complete lifecycle is:

	Research
	   ↓
	Feature Engineering
	   ↓
	Label Design
	   ↓
	Model Training
	   ↓
	Time-Series Validation
	   ↓
	Backtesting
	   ↓
	Model Evaluation
	   ↓
	Model Versioning
	   ↓
	Paper Trading
	   ↓
	Production Deployment
	   ↓
	Live Monitoring
	   ↓
	Performance Analysis
	   ↓
	Model Improvement
