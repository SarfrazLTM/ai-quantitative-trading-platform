# AI Quantitative Trading Platform
An AI-driven quantitative trading platform for systematic crypto market analysis, strategy evaluation, portfolio construction, risk management, and real-time signal generation.

## 1. Project Overview
This project is an AI-driven quantitative trading platform
designed for systematic cryptocurrency trading.

The platform processes real-time and historical market data,
transforms raw market data into quantitative features, analyzes
market structure, evaluates trading opportunities using machine
learning models, and applies portfolio and risk management before
generating trading signals.

The platform is designed as a production-oriented SaaS system,
with separate components for market data processing, quantitative
analysis, machine learning inference, portfolio construction,
risk management, and signal delivery.

## 2. Key Capabilities
- Market data processing
- Feature engineering
- Market structure analysis
- ML-based strategy evaluation
- Backtesting
- Portfolio construction
- Risk management
- Signal generation
- Webhook Delivery

## 3. System Architecture
[Architecture diagram]

## 4. End-to-End Data Flow
Market Data
    ↓
Feature Engineering
    ↓
Market Structure
    ↓
ML Models
    ↓
Strategy Decision
    ↓
Family/Group/Portfolio Risk Engine
    ↓
Signal
    ↓
Webhook

## 5. Machine Learning Pipeline
Historical Data
    ↓
Feature Engineering
    ↓
Training
    ↓
Time-Series Validation
    ↓
Evaluation
    ↓
Production Inference

## 6. Backtesting & Validation
#### 1. Data Integrity & Realistic Execution
No Lookahead: All calculations use only data available at the time of trading. Higher timeframe data is based on completed candles only.

Realistic Trading Costs:
Dynamic Slippage: Execution price impact adjusts based on market volatility (ATR), not fixed assumptions.
Exchange Fees: Maker/taker fees (0.02%/0.05%) and Eight-hour funding rates are included for 5x leveraged crypto positions.

#### 2. Proper ML Validation
Instead of standard K-Fold validation (which leaks future information):

Purged Cross-Validation: Removes overlapping trade outcomes and adds a buffer period between train/test splits to prevent data leakage and autocorrelation.

Forward Calibration: Probability calibrators are trained only on past data and applied to future unseen data.

#### 3. Performance by Market Regime
Strategy performance is analyzed across four market conditions to ensure alpha is consistent:

Strong Trends: Confirms the trend-following engine captures maximum profits.

Range/Liquidity Traps: Verifies that dynamic thresholds successfully avoid bad trades during choppy markets.

#### 4. Robustness Testing
To prove performance isn't from overfitting:

Monte Carlo Simulation: 5,000 random trade sequences to build drawdown confidence intervals (95%/99%).

Stress Testing: Costs are doubled (+200%) to find the breaking point where the strategy stops being profitable.

## 7. Risk Management
There are three types of risk levels
- Family Risk: Controls the maximum risk allocated across all strategies within a strategy family.
- Group Risk: Controls the maximum risk allocated to a user-defined group of strategy families.
- Portfolio Risk: Controls the maximum total risk allowed across the entire portfolio

## 8. Engineering Architecture
- Python services: Handle AI/ML models, strategy engines, signal generation, and quantitative processing.
- Laravel control plane: Manages users, portfolios, configuration, subscriptions, and platform administration.
- Redis: Provides high-speed caching, state management, queues, and inter-service communication.
- MongoDB: Stores signals, market intelligence, strategy results, and other high-volume data.
- Asynchronous Workers: execute computationally intensive and background tasks without blocking real-time signal processing.
- Service Separation: Separates core components into independent services for scalability, maintainability, and fault isolation.
- Monitoring & Resilience: Provides observability, health checks, error handling, retries, and recovery mechanisms across the platform.

## 9. Key Engineering Challenges
- avoiding look-ahead bias
- maintaining consistent features between research and production
- handling real-time data
- model inference reliability
- risk isolation
- scalable signal processing
- ML model probability score calibrators

## 10. Repository Structure
configs/ — Platform-level YAML configuration files and strategy settings.
diagrams/ — Architecture, component, and data-flow diagrams.
docs/ — Detailed technical documentation covering architecture, design, and workflows.
src/ — Core platform source code and major architectural components.
tests/ — Unit, integration, and system tests.
examples/ — Sample configurations, API payloads, workflows, and usage examples.

## 11. Project Status
The platform is currently under active development and includes
the core components required for a quantitative trading workflow.

### Implemented

- Market data ingestion and processing
- Multi-timeframe feature engineering
- Market structure analysis
- Machine learning model training and inference
- Strategy and strategy-family evaluation
- Historical backtesting
- Portfolio construction
- Position sizing and risk management
- Real-time signal generation
- Webhook-based signal delivery
- Asynchronous processing and service separation
- Production-oriented monitoring and resilience mechanisms

### Publicly Demonstrated

This repository demonstrates the system architecture, quantitative
engineering concepts, selected implementation patterns, ML pipeline,
backtesting methodology, risk-management architecture, and
production design decisions.

### Private / Not Included

Proprietary strategy logic, alpha-generating features, trained model
artifacts, production credentials, and certain production services
are intentionally excluded from this repository.

## 12. Detailed Documentation
- Architecture
- ML Pipeline
- Backtesting
- Risk Management
- Design Decisions

## 13. Disclaimer
Educational/research purposes, not financial advice.
