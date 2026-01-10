#!/usr/bin/env python3
"""
Spanish IRPF (Personal Income Tax) Calculator
Calculates personal income tax based on Spanish tax brackets.
"""

import argparse
import sys
from typing import List, Tuple
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


# Spanish IRPF tax brackets for 2024 (General State)
# Format: (min_income, max_income, rate)
TAX_BRACKETS = [
    (0, 12450, 0.19),
    (12450, 20200, 0.24),
    (20200, 35200, 0.30),
    (35200, 60000, 0.37),
    (60000, 300000, 0.45),
    (300000, float('inf'), 0.47),
]

# Personal allowance (minimum personal exemption)
PERSONAL_ALLOWANCE = 5550  # euros per year


@dataclass
class TaxBreakdown:
    """Breakdown of tax calculation by bracket."""
    bracket_min: float
    bracket_max: float
    taxable_amount: float
    rate: float
    tax_amount: float


@dataclass
class TaxResult:
    """Complete tax calculation result."""
    gross_income: float
    personal_allowance: float
    taxable_income: float
    total_tax: float
    net_income: float
    effective_rate: float
    breakdown: List[TaxBreakdown]


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def format_currency(amount: float) -> str:
    """Format amount as currency with Euro symbol."""
    return f"€{amount:,.2f}".replace(',', ' ').replace('.', ',')


def format_percentage(rate: float) -> str:
    """Format rate as percentage."""
    return f"{rate * 100:.2f}%"


def format_bracket_range(min_val: float, max_val: float = None) -> str:
    """Format bracket range with European number formatting."""
    min_str = f"€{min_val:,.0f}".replace(',', ' ')
    if max_val is None:
        return f"{min_str} - ∞"
    max_str = f"€{max_val:,.0f}".replace(',', ' ')
    return f"{min_str} - {max_str}"


def calculate_tax(gross_income: float, personal_allowance: float = PERSONAL_ALLOWANCE) -> TaxResult:
    """
    Calculate Spanish IRPF tax based on progressive brackets.

    Args:
        gross_income: Annual gross income in euros
        personal_allowance: Personal allowance amount (default: 5550)

    Returns:
        TaxResult object with complete calculation breakdown
    """
    # Calculate taxable income (after personal allowance)
    taxable_income = max(0, gross_income - personal_allowance)

    breakdown = []
    total_tax = 0.0
    remaining_income = taxable_income

    # Calculate tax for each bracket
    for bracket_min, bracket_max, rate in TAX_BRACKETS:
        if remaining_income <= 0:
            break

        # Calculate how much of remaining income falls in this bracket
        bracket_upper = min(bracket_max, taxable_income)

        if bracket_upper <= bracket_min:
            continue

        # Income in this bracket
        income_in_bracket = min(remaining_income, bracket_upper - bracket_min)

        if income_in_bracket > 0:
            tax_in_bracket = income_in_bracket * rate
            total_tax += tax_in_bracket

            breakdown.append(TaxBreakdown(
                bracket_min=bracket_min,
                bracket_max=bracket_max if bracket_max != float('inf') else None,
                taxable_amount=income_in_bracket,
                rate=rate,
                tax_amount=tax_in_bracket
            ))

            remaining_income -= income_in_bracket

    # Calculate net income and effective rate
    net_income = gross_income - total_tax
    effective_rate = (total_tax / gross_income * 100) if gross_income > 0 else 0

    return TaxResult(
        gross_income=gross_income,
        personal_allowance=personal_allowance,
        taxable_income=taxable_income,
        total_tax=total_tax,
        net_income=net_income,
        effective_rate=effective_rate,
        breakdown=breakdown
    )


def print_results(result: TaxResult, verbose: bool = False):
    """Print tax calculation results with colored output."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}  Spanish IRPF Tax Calculation{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

    # Summary section
    print(f"{Colors.BOLD}{Colors.OKCYAN}Summary:{Colors.ENDC}")
    print(f"  {Colors.OKBLUE}Gross Income:{Colors.ENDC}        {Colors.BOLD}{format_currency(result.gross_income)}{Colors.ENDC}")
    print(f"  {Colors.OKBLUE}Personal Allowance:{Colors.ENDC}  {format_currency(result.personal_allowance)}")
    print(f"  {Colors.OKBLUE}Taxable Income:{Colors.ENDC}      {format_currency(result.taxable_income)}")
    print(f"  {Colors.FAIL}Total Tax:{Colors.ENDC}            {Colors.BOLD}{Colors.FAIL}{format_currency(result.total_tax)}{Colors.ENDC}")
    print(f"  {Colors.OKGREEN}Net Income:{Colors.ENDC}          {Colors.BOLD}{Colors.OKGREEN}{format_currency(result.net_income)}{Colors.ENDC}")
    print(f"  {Colors.WARNING}Effective Tax Rate:{Colors.ENDC}  {Colors.BOLD}{format_percentage(result.effective_rate / 100)}{Colors.ENDC}\n")

    if verbose and result.breakdown:
        print(f"{Colors.BOLD}{Colors.OKCYAN}Tax Breakdown by Bracket:{Colors.ENDC}\n")
        print(f"  {Colors.UNDERLINE}{'Bracket':<25} {'Amount':<15} {'Rate':<10} {'Tax':<15}{Colors.ENDC}")
        print(f"  {'-'*65}")

        for i, bracket in enumerate(result.breakdown, 1):
            bracket_str = format_bracket_range(bracket.bracket_min, bracket.bracket_max)
            print(f"  {Colors.OKBLUE}{bracket_str:<25}{Colors.ENDC} "
                  f"{format_currency(bracket.taxable_amount):<15} "
                  f"{format_percentage(bracket.rate):<10} "
                  f"{Colors.FAIL}{format_currency(bracket.tax_amount)}{Colors.ENDC}")

        print()

    # Monthly breakdown
    print(f"{Colors.BOLD}{Colors.OKCYAN}Monthly Breakdown:{Colors.ENDC}")
    monthly_gross = result.gross_income / 12
    monthly_tax = result.total_tax / 12
    monthly_net = result.net_income / 12
    print(f"  {Colors.OKBLUE}Gross:{Colors.ENDC}  {format_currency(monthly_gross)}")
    print(f"  {Colors.FAIL}Tax:{Colors.ENDC}   {format_currency(monthly_tax)}")
    print(f"  {Colors.OKGREEN}Net:{Colors.ENDC}    {format_currency(monthly_net)}")
    print()


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description='Calculate Spanish IRPF (Personal Income Tax)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 60000                    # Calculate tax for €60,000 annual income
  %(prog)s 50000 --verbose          # Show detailed bracket breakdown
  %(prog)s 45000 --allowance 7000   # Use custom personal allowance
  %(prog)s 35000 --monthly          # Input as monthly income
        """
    )

    parser.add_argument(
        'income',
        type=float,
        help='Annual income in euros (or monthly if --monthly is used)'
    )

    parser.add_argument(
        '--monthly',
        action='store_true',
        help='Treat income as monthly instead of annual'
    )

    parser.add_argument(
        '--allowance',
        type=float,
        default=PERSONAL_ALLOWANCE,
        help=f'Personal allowance amount (default: €{PERSONAL_ALLOWANCE:,.0f})'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed tax bracket breakdown'
    )

    args = parser.parse_args()

    # Convert monthly to annual if needed
    if args.monthly:
        annual_income = args.income * 12
    else:
        annual_income = args.income

    # Validate input
    if annual_income < 0:
        print(f"{Colors.FAIL}Error: Income cannot be negative{Colors.ENDC}", file=sys.stderr)
        sys.exit(1)

    # Calculate tax
    try:
        result = calculate_tax(annual_income, args.allowance)
        print_results(result, args.verbose)
    except Exception as e:
        print(f"{Colors.FAIL}Error calculating tax: {e}{Colors.ENDC}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
