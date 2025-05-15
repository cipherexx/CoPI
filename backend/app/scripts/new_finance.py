import yfinance as yf
import pandas as pd
import numpy as np
from scipy import stats

def financial_analysis_score(ticker_symbol):
    """
    Calculate a comprehensive financial analysis score for a company.
    
    Parameters:
    ticker_symbol (str): The ticker symbol of the company
    
    Returns:
    dict: Dictionary containing overall score and component scores
    """
    try:
        # Initialize the ticker object
        ticker = yf.Ticker(ticker_symbol)
        
        # Get financial data
        balance_sheet = ticker.balance_sheet
        income_stmt = ticker.income_stmt
        cash_flow = ticker.cashflow
        
        # Check if we have enough data
        if balance_sheet.empty:
            print(f"Insufficient balance sheet data for {ticker_symbol}")
            return None
            
        # Calculate scores
        profitability_score = calculate_profitability_score(ticker, balance_sheet, income_stmt)
        capitalization_score = calculate_capitalization_score(ticker, balance_sheet)
        coverage_score = calculate_coverage_score(ticker, balance_sheet, income_stmt, cash_flow)
        efficiency_score = calculate_efficiency_score(ticker, balance_sheet, income_stmt)
        cost_structure_score = calculate_cost_structure_score(ticker, income_stmt)
        
        # Calculate weighted overall score
        weights = {
            'profitability': 0.30,
            'capitalization': 0.30,
            'coverage': 0.25,
            'efficiency': 0.075,
            'cost_structure': 0.075
        }
        
        scores = {
            'profitability': profitability_score,
            'capitalization': capitalization_score,
            'coverage': coverage_score,
            'efficiency': efficiency_score,
            'cost_structure': cost_structure_score
        }
        
        # Filter out None values
        valid_scores = {k: v for k, v in scores.items() if v is not None}
        valid_weights = {k: weights[k] for k in valid_scores.keys()}
        
        # Normalize weights to sum to 1
        if valid_weights:
            weight_sum = sum(valid_weights.values())
            valid_weights = {k: v/weight_sum for k, v in valid_weights.items()}
            
            # Calculate overall score
            overall_score = sum(valid_scores[k] * valid_weights[k] for k in valid_scores.keys())
        else:
            overall_score = None
        
        return {
            'overall_score': overall_score,
            'profitability_score': profitability_score,
            'capitalization_score': capitalization_score,
            'coverage_score': coverage_score,
            'efficiency_score': efficiency_score,
            'cost_structure_score': cost_structure_score
        }
        
    except Exception as e:
        print(f"Error analyzing {ticker_symbol}: {str(e)}")
        return None

def normalize_to_scale(value, min_val=0, max_val=10, lower_bound=0, upper_bound=10):
    """
    Normalize a value to a scale from min_val to max_val
    with bounds to prevent extreme outliers
    """
    if value is None:
        return None
    
    # Apply sigmoid normalization for smoother distribution
    normalized = 10 / (1 + np.exp(-0.5 * (value - 5)))
    
    # Ensure the value is within bounds
    return max(min(normalized, upper_bound), lower_bound)

def safe_get(df, row_name, col_idx=0, default=None):
    """Safely get a value from a dataframe, return default if not found"""
    try:
        if row_name in df.index:
            return df.loc[row_name, df.columns[col_idx]]
        return default
    except:
        return default

def calculate_profitability_score(ticker, balance_sheet, income_stmt):
    """Calculate profitability score based on reliable profitability metrics"""
    try:
        # Check if income statement is available
        if income_stmt is None or income_stmt.empty:
            # Use only balance sheet data
            latest_year = balance_sheet.columns[0]
            prev_year = balance_sheet.columns[1] if len(balance_sheet.columns) > 1 else None
            
            if prev_year is None:
                return None  # Need at least two years of data
                
            # Calculate retained earnings growth
            retained_earnings_current = safe_get(balance_sheet, 'Retained Earnings', 0)
            retained_earnings_prev = safe_get(balance_sheet, 'Retained Earnings', 1)
            
            if retained_earnings_current is not None and retained_earnings_prev is not None:
                # For retained earnings, negative values should result in low scores
                if retained_earnings_current < 0:
                    # Negative retained earnings should get a low score
                    # The more negative, the lower the score
                    normalized_growth = 3 * np.exp(retained_earnings_current / abs(retained_earnings_prev)) if retained_earnings_prev != 0 else 2
                    return max(0, min(normalized_growth, 5))  # Cap at 5 for negative retained earnings
                else:
                    # Positive growth in retained earnings is good
                    retained_earnings_growth = (retained_earnings_current - retained_earnings_prev) / abs(retained_earnings_prev) if retained_earnings_prev != 0 else 0
                    # Normalize to 0-10 scale
                    normalized_growth = 5 + 5 * np.tanh(retained_earnings_growth)
                    return normalized_growth
            
            # If retained earnings not available, use total equity growth
            equity_current = safe_get(balance_sheet, 'Total Equity Gross Minority Interest', 0) or safe_get(balance_sheet, 'Stockholders Equity', 0)
            equity_prev = safe_get(balance_sheet, 'Total Equity Gross Minority Interest', 1) or safe_get(balance_sheet, 'Stockholders Equity', 1)
            
            if equity_current is not None and equity_prev is not None and equity_prev != 0:
                if equity_current < 0:
                    # Negative equity should get a low score
                    return max(0, 3 - abs(equity_current / equity_prev))
                else:
                    equity_growth = (equity_current - equity_prev) / abs(equity_prev)
                    normalized_growth = 5 + 5 * np.tanh(equity_growth)
                    return normalized_growth
                
            return None
        
        # If income statement is available
        latest_year = income_stmt.columns[0]
        
        # Get key metrics that are commonly available
        net_income = safe_get(income_stmt, 'Net Income', 0)
        total_revenue = safe_get(income_stmt, 'Total Revenue', 0)
        
        # Get balance sheet items
        total_assets = safe_get(balance_sheet, 'Total Assets', 0)
        total_equity = safe_get(balance_sheet, 'Total Equity Gross Minority Interest', 0) or safe_get(balance_sheet, 'Stockholders Equity', 0)
        
        # Calculate profitability ratios
        metrics = []
        weights = []
        
        # Return on Assets (ROA)
        if net_income is not None and total_assets is not None and total_assets != 0:
            roa = net_income / total_assets
            # For negative ROA, score should be proportionally lower
            if roa < 0:
                # Negative ROA gets a score between 0-3 based on severity
                normalized_roa = max(0, 3 + 3 * np.tanh(roa * 5))
            else:
                normalized_roa = 5 + 5 * np.tanh(roa * 5)  # Scale ROA for better distribution
            metrics.append(normalized_roa)
            weights.append(0.35)
            
        # Return on Equity (ROE)
        if net_income is not None and total_equity is not None and total_equity != 0:
            roe = net_income / total_equity
            # Handle negative cases specially
            if net_income < 0:
                if total_equity < 0:
                    # Negative income and negative equity - both bad signals
                    normalized_roe = 1  # Very low score
                else:
                    # Negative income with positive equity - clear loss
                    normalized_roe = max(0, 3 + 3 * np.tanh(roe * 3))
            elif total_equity < 0:
                # Positive income with negative equity - unusual but concerning
                normalized_roe = 3  # Low score
            else:
                # Normal positive case
                normalized_roe = 5 + 5 * np.tanh(roe * 3)
            metrics.append(normalized_roe)
            weights.append(0.35)
            
        # Net Profit Margin
        if net_income is not None and total_revenue is not None and total_revenue != 0:
            net_margin = net_income / total_revenue
            # For negative margin, score should be proportionally lower
            if net_margin < 0:
                # Negative margin gets a score between 0-3 based on severity
                normalized_margin = max(0, 3 + 3 * np.tanh(net_margin * 10))
            else:
                normalized_margin = 5 + 5 * np.tanh(net_margin * 10)
            metrics.append(normalized_margin)
            weights.append(0.30)
            
        # If we have at least one metric
        if metrics:
            # Normalize weights to sum to 1
            weight_sum = sum(weights)
            weights = [w / weight_sum for w in weights]
            
            # Calculate weighted score
            profitability_score = sum(m * w for m, w in zip(metrics, weights))
            
            # Additional check: if net income is negative, cap the score at 4
            if net_income is not None and net_income < 0:
                profitability_score = min(profitability_score, 4.0)
                
            return profitability_score
        
        return None
        
    except Exception as e:
        print(f"Error calculating profitability score: {str(e)}")
        return None


def calculate_capitalization_score(ticker, balance_sheet):
    """Calculate capitalization score based on reliable balance sheet metrics"""
    try:
        latest_year = balance_sheet.columns[0]
        
        # Extract key balance sheet metrics that are commonly available
        total_assets = safe_get(balance_sheet, 'Total Assets')
        total_equity = safe_get(balance_sheet, 'Total Equity Gross Minority Interest') or safe_get(balance_sheet, 'Stockholders Equity')
        total_debt = safe_get(balance_sheet, 'Total Debt') or safe_get(balance_sheet, 'Long Term Debt And Capital Lease Obligation')
        current_assets = safe_get(balance_sheet, 'Current Assets')
        current_liabilities = safe_get(balance_sheet, 'Current Liabilities')
        working_capital = safe_get(balance_sheet, 'Working Capital') or (current_assets - current_liabilities if current_assets is not None and current_liabilities is not None else None)
        
        metrics = []
        weights = []
        
        # Equity to Assets ratio (higher is better)
        if total_equity is not None and total_assets is not None and total_assets != 0:
            equity_to_assets = total_equity / total_assets
            # For negative equity, score should be lower
            if equity_to_assets < 0:
                normalized_equity_ratio = 2 * np.tanh(equity_to_assets)  # Negative score for negative equity
            else:
                normalized_equity_ratio = 5 + 5 * np.tanh(equity_to_assets * 2)  # Scale for better distribution
            metrics.append(normalized_equity_ratio)
            weights.append(0.40)
            
        # Debt to Assets ratio (lower is better)
        if total_debt is not None and total_assets is not None and total_assets != 0:
            debt_to_assets = total_debt / total_assets
            normalized_debt_ratio = 10 - 10 * np.tanh(debt_to_assets)  # Invert so lower debt gets higher score
            metrics.append(normalized_debt_ratio)
            weights.append(0.30)
            
        # Working Capital to Assets ratio (higher is better)
        if working_capital is not None and total_assets is not None and total_assets != 0:
            wc_to_assets = working_capital / total_assets
            normalized_wc_ratio = 5 + 5 * np.tanh(wc_to_assets * 3)  # Scale for better distribution
            metrics.append(normalized_wc_ratio)
            weights.append(0.30)
            
        # If we have at least one metric
        if metrics:
            # Normalize weights to sum to 1
            weight_sum = sum(weights)
            weights = [w / weight_sum for w in weights]
            
            # Calculate weighted score
            capitalization_score = sum(m * w for m, w in zip(metrics, weights))
            return capitalization_score
        
        return None
        
    except Exception as e:
        print(f"Error calculating capitalization score: {str(e)}")
        return None

def calculate_coverage_score(ticker, balance_sheet, income_stmt, cash_flow):
    """Calculate coverage score based on reliable coverage metrics"""
    try:
        # If income statement is not available, we can't calculate coverage ratios
        if income_stmt is None or income_stmt.empty:
            return None
            
        latest_year = income_stmt.columns[0]
        
        # Get key metrics
        total_debt = safe_get(balance_sheet, 'Total Debt') or safe_get(balance_sheet, 'Long Term Debt And Capital Lease Obligation')
        current_liabilities = safe_get(balance_sheet, 'Current Liabilities')
        operating_income = safe_get(income_stmt, 'Operating Income')
        net_income = safe_get(income_stmt, 'Net Income')
        
        # Try to get operating cash flow
        operating_cash_flow = None
        if cash_flow is not None and not cash_flow.empty:
            operating_cash_flow = safe_get(cash_flow, 'Operating Cash Flow')
        
        metrics = []
        weights = []
        
        # Debt to Income ratio (lower is better)
        if total_debt is not None and net_income is not None and net_income != 0:
            debt_to_income = total_debt / net_income
            # For negative income, score should be lower
            if net_income < 0:
                normalized_debt_income = 2  # Low score for negative income
            else:
                normalized_debt_income = 10 - 5 * np.tanh(debt_to_income / 5)  # Scale for better distribution
            metrics.append(normalized_debt_income)
            weights.append(0.35)
            
        # Operating Income to Current Liabilities (higher is better)
        if operating_income is not None and current_liabilities is not None and current_liabilities != 0:
            income_to_liabilities = operating_income / current_liabilities
            normalized_income_liabilities = 5 + 5 * np.tanh(income_to_liabilities)
            metrics.append(normalized_income_liabilities)
            weights.append(0.35)
            
        # Cash Flow to Debt ratio (higher is better)
        if operating_cash_flow is not None and total_debt is not None and total_debt != 0:
            cf_to_debt = operating_cash_flow / total_debt
            normalized_cf_debt = 5 + 5 * np.tanh(cf_to_debt * 2)
            metrics.append(normalized_cf_debt)
            weights.append(0.30)
            
        # If we have at least one metric
        if metrics:
            # Normalize weights to sum to 1
            weight_sum = sum(weights)
            weights = [w / weight_sum for w in weights]
            
            # Calculate weighted score
            coverage_score = sum(m * w for m, w in zip(metrics, weights))
            return coverage_score
        
        return None
        
    except Exception as e:
        print(f"Error calculating coverage score: {str(e)}")
        return None

def calculate_efficiency_score(ticker, balance_sheet, income_stmt):
    """Calculate efficiency score based on reliable efficiency metrics"""
    try:
        # If income statement is not available, we can't calculate efficiency ratios
        if income_stmt is None or income_stmt.empty:
            return None
            
        latest_year = income_stmt.columns[0]
        prev_year = income_stmt.columns[1] if len(income_stmt.columns) > 1 else None
        
        # Get key metrics
        total_assets = safe_get(balance_sheet, 'Total Assets')
        total_revenue = safe_get(income_stmt, 'Total Revenue')
        accounts_receivable = safe_get(balance_sheet, 'Accounts Receivable') or safe_get(balance_sheet, 'Net Receivables')
        inventory = safe_get(balance_sheet, 'Inventory')
        
        metrics = []
        weights = []
        
        # Asset Turnover (higher is better)
        if total_revenue is not None and total_assets is not None and total_assets != 0:
            asset_turnover = total_revenue / total_assets
            normalized_asset_turnover = 5 + 5 * np.tanh(asset_turnover - 0.5)  # Adjust baseline
            metrics.append(normalized_asset_turnover)
            weights.append(0.50)
            
        # Accounts Receivable Turnover (higher is better)
        if total_revenue is not None and accounts_receivable is not None and accounts_receivable != 0:
            ar_turnover = total_revenue / accounts_receivable
            normalized_ar_turnover = 5 + 5 * np.tanh((ar_turnover - 6) / 5)  # Adjust baseline
            metrics.append(normalized_ar_turnover)
            weights.append(0.25)
            
        # Revenue Growth (if we have previous year data)
        if prev_year is not None:
            current_revenue = total_revenue
            prev_revenue = safe_get(income_stmt, 'Total Revenue', 1)
            
            if current_revenue is not None and prev_revenue is not None and prev_revenue != 0:
                revenue_growth = (current_revenue - prev_revenue) / prev_revenue
                normalized_growth = 5 + 5 * np.tanh(revenue_growth * 5)  # Scale for better distribution
                metrics.append(normalized_growth)
                weights.append(0.25)
            
        # If we have at least one metric
        if metrics:
            # Normalize weights to sum to 1
            weight_sum = sum(weights)
            weights = [w / weight_sum for w in weights]
            
            # Calculate weighted score
            efficiency_score = sum(m * w for m, w in zip(metrics, weights))
            return efficiency_score
        
        return None
        
    except Exception as e:
        print(f"Error calculating efficiency score: {str(e)}")
        return None

def calculate_cost_structure_score(ticker, income_stmt):
    """Calculate cost structure score based on reliable cost metrics"""
    try:
        # If income statement is not available, we can't calculate cost structure ratios
        if income_stmt is None or income_stmt.empty:
            return None
            
        latest_year = income_stmt.columns[0]
        
        # Get key metrics
        total_revenue = safe_get(income_stmt, 'Total Revenue')
        gross_profit = safe_get(income_stmt, 'Gross Profit')
        operating_income = safe_get(income_stmt, 'Operating Income')
        net_income = safe_get(income_stmt, 'Net Income')
        
        metrics = []
        weights = []
        
        # Gross Margin (higher is better)
        if gross_profit is not None and total_revenue is not None and total_revenue != 0:
            gross_margin = gross_profit / total_revenue
            normalized_gross_margin = 5 + 5 * np.tanh((gross_margin - 0.3) * 5)  # Adjust baseline
            metrics.append(normalized_gross_margin)
            weights.append(0.40)
            
        # Operating Margin (higher is better)
        if operating_income is not None and total_revenue is not None and total_revenue != 0:
            operating_margin = operating_income / total_revenue
            normalized_operating_margin = 5 + 5 * np.tanh((operating_margin - 0.1) * 10)  # Adjust baseline
            metrics.append(normalized_operating_margin)
            weights.append(0.30)
            
        # Net Margin (higher is better)
        if net_income is not None and total_revenue is not None and total_revenue != 0:
            net_margin = net_income / total_revenue
            normalized_net_margin = 5 + 5 * np.tanh((net_margin - 0.05) * 15)  # Adjust baseline
            metrics.append(normalized_net_margin)
            weights.append(0.30)
            
        # If we have at least one metric
        if metrics:
            # Normalize weights to sum to 1
            weight_sum = sum(weights)
            weights = [w / weight_sum for w in weights]
            
            # Calculate weighted score
            cost_structure_score = sum(m * w for m, w in zip(metrics, weights))
            return cost_structure_score
        
        return None
        
    except Exception as e:
        print(f"Error calculating cost structure score: {str(e)}")
        return None

# Example usage
def analyze_company(ticker_symbol):
    """Analyze a company and print its financial analysis scores"""
    results = financial_analysis_score(ticker_symbol)
    
    if results:
        print(f"\nFinancial Analysis for {ticker_symbol}")
        print("=" * 50)
        
        if results['overall_score'] is not None:
            print(f"Overall Score: {results['overall_score']:.2f}/10")
        else:
            print("Overall Score: N/A")
            
        print("-" * 50)
        
        components = [
            ("Profitability Score (30%)", results['profitability_score']),
            ("Capitalization Score (30%)", results['capitalization_score']),
            ("Coverage Score (25%)", results['coverage_score']),
            ("Efficiency Score (7.5%)", results['efficiency_score']),
            ("Cost Structure Score (7.5%)", results['cost_structure_score'])
        ]
        
        for name, score in components:
            if score is not None:
                print(f"{name}: {score:.2f}/10")
            else:
                print(f"{name}: N/A")
    else:
        print(f"Could not analyze {ticker_symbol}")
    
    return results
