#!/usr/bin/env python3
"""
Spanish Tax Calculator
Calculates personal income tax (IRPF) and social security contributions based on Spanish tax brackets.
"""

import argparse
import sys
from typing import List, Tuple, Optional
from dataclasses import dataclass

# Spanish IRPF tax brackets for 2024 (General State)
# Format: (min_income, max_income, rate)
STATE_TAX_BRACKETS = [
    (0, 12450, 0.19),
    (12450, 20200, 0.24),
    (20200, 35200, 0.30),
    (35200, 60000, 0.37),
    (60000, 300000, 0.45),
    (300000, float('inf'), 0.47),
]

# Regional IRPF tax brackets for 2024 (by Comunidad Autónoma)
# Format: (min_income, max_income, rate)
# These are applied in addition to state brackets
REGIONAL_TAX_BRACKETS = {
    'madrid': [
        (0, 12450, 0.09),
        (12450, 20200, 0.10),
        (20200, 35200, 0.11),
        (35200, 60000, 0.12),
        (60000, 300000, 0.13),
        (300000, float('inf'), 0.14),
    ],
    'catalonia': [
        (0, 12450, 0.10),
        (12450, 20200, 0.11),
        (20200, 35200, 0.12),
        (35200, 60000, 0.13),
        (60000, 300000, 0.14),
        (300000, float('inf'), 0.15),
    ],
    'andalusia': [
        (0, 12450, 0.10),
        (12450, 20200, 0.11),
        (20200, 35200, 0.12),
        (35200, 60000, 0.13),
        (60000, 300000, 0.14),
        (300000, float('inf'), 0.15),
    ],
    'valencia': [
        (0, 12450, 0.10),
        (12450, 20200, 0.11),
        (20200, 35200, 0.12),
        (35200, 60000, 0.13),
        (60000, 300000, 0.14),
        (300000, float('inf'), 0.15),
    ],
    'basque': [
        (0, 12450, 0.09),
        (12450, 20200, 0.10),
        (20200, 35200, 0.11),
        (35200, 60000, 0.12),
        (60000, 300000, 0.13),
        (300000, float('inf'), 0.14),
    ],
    'galicia': [
        (0, 12450, 0.10),
        (12450, 20200, 0.11),
        (20200, 35200, 0.12),
        (35200, 60000, 0.13),
        (60000, 300000, 0.14),
        (300000, float('inf'), 0.15),
    ],
    'castilla_leon': [
        (0, 12450, 0.09),
        (12450, 20200, 0.10),
        (20200, 35200, 0.11),
        (35200, 60000, 0.12),
        (60000, 300000, 0.13),
        (300000, float('inf'), 0.14),
    ],
    'canary_islands': [
        (0, 12450, 0.08),
        (12450, 20200, 0.09),
        (20200, 35200, 0.10),
        (35200, 60000, 0.11),
        (60000, 300000, 0.12),
        (300000, float('inf'), 0.13),
    ],
    'none': [],  # No regional tax
}

# Personal allowance (minimum personal exemption) - varies by age
PERSONAL_ALLOWANCE_UNDER_65 = 5550  # Under 65 years old
PERSONAL_ALLOWANCE_65_74 = 6700  # 65-74 years old
PERSONAL_ALLOWANCE_75_PLUS = 8100  # 75+ years old

# Dependent allowances (2024 rates)
# Children (descendientes)
ALLOWANCE_FIRST_CHILD = 2400  # First child
ALLOWANCE_SECOND_CHILD = 2700  # Second child
ALLOWANCE_THIRD_CHILD = 4000  # Third child
ALLOWANCE_FOURTH_PLUS_CHILD = 4500  # Fourth and subsequent children
ALLOWANCE_CHILD_UNDER_3 = 2800  # Additional for each child under 3 years old
ALLOWANCE_CHILD_DISABILITY_33 = 3000  # Additional for child with 33%+ disability
ALLOWANCE_CHILD_DISABILITY_65 = 12000  # Additional for child with 65%+ disability

# Ascendants (elderly parents/grandparents)
ALLOWANCE_ASCENDANT_65 = 1150  # Per ascendant over 65
ALLOWANCE_ASCENDANT_DISABILITY_33 = 3000  # Per ascendant with 33%+ disability
ALLOWANCE_ASCENDANT_DISABILITY_65 = 12000  # Per ascendant with 65%+ disability

# Large family (familia numerosa)
ALLOWANCE_LARGE_FAMILY_GENERAL = 2400  # General large family
ALLOWANCE_LARGE_FAMILY_SPECIAL = 4800  # Special large family (5+ children or 4+ with disability)

# Single parent (monoparental)
ALLOWANCE_SINGLE_PARENT = 2100  # Single parent family

# Disability (for taxpayer)
ALLOWANCE_DISABILITY_33 = 3000  # Taxpayer with 33%+ disability
ALLOWANCE_DISABILITY_65 = 12000  # Taxpayer with 65%+ disability
ALLOWANCE_DISABILITY_MOBILITY = 3000  # Taxpayer with mobility disability
ALLOWANCE_DISABILITY_DEPENDENCY = 12000  # Taxpayer requiring assistance

# Social Security rate (employee contribution)
# Typical rate is 6.35% of gross salary for employees
SOCIAL_SECURITY_RATE = 0.0635  # 6.35%

# Beckham Law (Special Tax Regime for Foreign Workers)
# Flat 24% tax rate on income up to €600,000
# Income above €600,000 is taxed at normal progressive rates
BECKHAM_LAW_THRESHOLD = 600000  # euros
BECKHAM_LAW_RATE = 0.24  # 24%

# Display and calculation constants
MONTHS_PER_YEAR = 12
PERCENTAGE_MULTIPLIER = 100
HEADER_WIDTH = 60
SUMMARY_LABEL_WIDTH = 25
SUMMARY_VALUE_WIDTH = 20
MONTHLY_LABEL_WIDTH = 20
MONTHLY_VALUE_WIDTH = 20
TABLE_WIDTH = 25 + 1 + 15 + 1 + 10 + 1 + 15

# Age thresholds for personal allowance
AGE_THRESHOLD_65 = 65
AGE_THRESHOLD_75 = 75
MAX_REASONABLE_AGE = 120

# Valid regions
VALID_REGIONS = ['madrid', 'catalonia', 'andalusia', 'valencia', 'basque',
                 'galicia', 'castilla_leon', 'canary_islands', 'none']


@dataclass
class TaxBreakdown:
    """Breakdown of tax calculation by bracket."""
    bracket_min: float
    bracket_max: float
    taxable_amount: float
    rate: float
    tax_amount: float


@dataclass
class DependentInfo:
    """Information about dependents and allowances."""
    children_under_3: int = 0
    children_3_plus: int = 0
    children_disability_33: int = 0  # Children with 33%+ disability
    children_disability_65: int = 0  # Children with 65%+ disability
    ascendants_65: int = 0  # Ascendants over 65
    ascendants_disability_33: int = 0  # Ascendants with 33%+ disability
    ascendants_disability_65: int = 0  # Ascendants with 65%+ disability
    large_family: bool = False
    large_family_special: bool = False
    single_parent: bool = False
    taxpayer_disability_33: bool = False
    taxpayer_disability_65: bool = False
    taxpayer_disability_mobility: bool = False
    taxpayer_disability_dependency: bool = False


@dataclass
class TaxResult:
    """Complete tax calculation result."""
    gross_income: float
    social_security_tax: float
    income_after_ss: float
    personal_allowance: float
    dependent_allowances: float  # Total allowances from dependents
    total_allowances: float  # Personal + dependent allowances
    taxable_income: float
    state_irpf_tax: float
    regional_irpf_tax: float
    irpf_tax: float  # Total IRPF (state + regional)
    total_deductions: float
    net_income: float
    effective_rate: float
    region: str
    beckham_law: bool
    beckham_law_tax: float  # Tax on income up to threshold
    beckham_law_excess_tax: float  # Tax on income above threshold (if any)
    taxpayer_age: int  # Taxpayer's age
    dependents: DependentInfo
    state_breakdown: List[TaxBreakdown]
    regional_breakdown: List[TaxBreakdown]


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


def format_currency_aligned(amount: float, width: int = 18) -> str:
    """Format amount as currency with Euro symbol, right-aligned to specified width."""
    formatted = f"€{amount:,.2f}".replace(',', ' ').replace('.', ',')
    return f"{formatted:>{width}}"


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


def _calculate_children_allowances(dependents: DependentInfo) -> float:
    """Calculate allowances for children based on order and age."""
    total = 0.0
    total_children = dependents.children_under_3 + dependents.children_3_plus

    # Base allowances by child order
    child_allowances = [
        ALLOWANCE_FIRST_CHILD,
        ALLOWANCE_SECOND_CHILD,
        ALLOWANCE_THIRD_CHILD,
    ]

    for i in range(min(total_children, 3)):
        total += child_allowances[i]
        # Add under-3 bonus for each child under 3
        if i < dependents.children_under_3:
            total += ALLOWANCE_CHILD_UNDER_3

    # Fourth and subsequent children
    for i in range(4, total_children + 1):
        total += ALLOWANCE_FOURTH_PLUS_CHILD
        if i <= dependents.children_under_3:
            total += ALLOWANCE_CHILD_UNDER_3

    # Additional under-3 allowances for children beyond the first 3
    if dependents.children_under_3 > 3:
        total += (dependents.children_under_3 - 3) * ALLOWANCE_CHILD_UNDER_3

    # Disability allowances for children
    total += dependents.children_disability_33 * ALLOWANCE_CHILD_DISABILITY_33
    total += dependents.children_disability_65 * ALLOWANCE_CHILD_DISABILITY_65

    return total


def _calculate_ascendant_allowances(dependents: DependentInfo) -> float:
    """Calculate allowances for ascendants (elderly parents/grandparents)."""
    return (
        dependents.ascendants_65 * ALLOWANCE_ASCENDANT_65 +
        dependents.ascendants_disability_33 * ALLOWANCE_ASCENDANT_DISABILITY_33 +
        dependents.ascendants_disability_65 * ALLOWANCE_ASCENDANT_DISABILITY_65
    )


def _calculate_family_status_allowances(dependents: DependentInfo) -> float:
    """Calculate allowances based on family status."""
    total = 0.0

    if dependents.large_family_special:
        total += ALLOWANCE_LARGE_FAMILY_SPECIAL
    elif dependents.large_family:
        total += ALLOWANCE_LARGE_FAMILY_GENERAL

    if dependents.single_parent:
        total += ALLOWANCE_SINGLE_PARENT
    
    return total


def _calculate_taxpayer_disability_allowance(dependents: DependentInfo) -> float:
    """Calculate disability allowance for taxpayer (highest priority only)."""
    if dependents.taxpayer_disability_dependency:
        return ALLOWANCE_DISABILITY_DEPENDENCY
    elif dependents.taxpayer_disability_65:
        return ALLOWANCE_DISABILITY_65
    elif dependents.taxpayer_disability_mobility:
        return ALLOWANCE_DISABILITY_MOBILITY
    elif dependents.taxpayer_disability_33:
        return ALLOWANCE_DISABILITY_33
    return 0.0


def calculate_dependent_allowances(dependents: DependentInfo) -> float:
    """Calculate total allowances from dependents and family situation."""
    return (
        _calculate_children_allowances(dependents) +
        _calculate_ascendant_allowances(dependents) +
        _calculate_family_status_allowances(dependents) +
        _calculate_taxpayer_disability_allowance(dependents)
    )


def calculate_bracket_tax(taxable_income: float, brackets: List[Tuple[float, float, float]]) -> Tuple[float, List[TaxBreakdown]]:
    """Calculate tax for given brackets and return tax amount and breakdown."""
    breakdown = []
    total_tax = 0.0
    remaining_income = taxable_income

    for bracket_min, bracket_max, rate in brackets:
        if remaining_income <= 0:
            break

        bracket_upper = min(bracket_max, taxable_income)

        if bracket_upper <= bracket_min:
            continue

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

    return total_tax, breakdown


def get_personal_allowance_by_age(age: Optional[int] = None) -> float:
    """Get personal allowance based on taxpayer age."""
    if age is None:
        return PERSONAL_ALLOWANCE_UNDER_65
    if age >= AGE_THRESHOLD_75:
        return PERSONAL_ALLOWANCE_75_PLUS
    elif age >= AGE_THRESHOLD_65:
        return PERSONAL_ALLOWANCE_65_74
    else:
        return PERSONAL_ALLOWANCE_UNDER_65


def _calculate_social_security(gross_income: float, social_security_rate: float) -> Tuple[float, float]:
    """Calculate social security tax and income after social security."""
    social_security_tax = gross_income * social_security_rate
    income_after_ss = gross_income - social_security_tax
    return social_security_tax, income_after_ss


def _calculate_beckham_law_tax(taxable_income: float) -> Tuple[float, float, float, List[TaxBreakdown]]:
    """Calculate tax under Beckham Law regime."""
    if taxable_income <= BECKHAM_LAW_THRESHOLD:
        beckham_law_tax = taxable_income * BECKHAM_LAW_RATE
        return beckham_law_tax, 0.0, beckham_law_tax, []

    # Income up to threshold: 24%
    beckham_law_tax = BECKHAM_LAW_THRESHOLD * BECKHAM_LAW_RATE
    # Income above threshold: normal progressive rates
    excess_income = taxable_income - BECKHAM_LAW_THRESHOLD
    beckham_law_excess_tax, state_breakdown = calculate_bracket_tax(excess_income, STATE_TAX_BRACKETS)
    total_irpf = beckham_law_tax + beckham_law_excess_tax
    return beckham_law_tax, beckham_law_excess_tax, total_irpf, state_breakdown


def _calculate_standard_irpf_tax(taxable_income: float, region: str) -> Tuple[float, float, float, List[TaxBreakdown], List[TaxBreakdown]]:
    """Calculate standard IRPF tax (state + regional)."""
    state_irpf_tax, state_breakdown = calculate_bracket_tax(taxable_income, STATE_TAX_BRACKETS)
    regional_brackets = REGIONAL_TAX_BRACKETS.get(region, REGIONAL_TAX_BRACKETS['none'])
    regional_irpf_tax, regional_breakdown = calculate_bracket_tax(taxable_income, regional_brackets)
    total_irpf = state_irpf_tax + regional_irpf_tax
    return state_irpf_tax, regional_irpf_tax, total_irpf, state_breakdown, regional_breakdown


def calculate_tax(gross_income: float, personal_allowance: Optional[float] = None, social_security_rate: float = SOCIAL_SECURITY_RATE, region: str = 'none', beckham_law: bool = False, dependents: Optional[DependentInfo] = None, taxpayer_age: Optional[int] = None) -> TaxResult:
    """
    Calculate Spanish IRPF tax (state + regional) and social security contributions based on progressive brackets.

    Args:
        gross_income: Annual gross income in euros
        personal_allowance: Personal allowance amount (if None, calculated from age)
        social_security_rate: Social security rate (default: 0.0635 = 6.35%)
        region: Spanish region (default: 'none'). Options: madrid, catalonia, andalusia, valencia, basque, galicia, castilla_leon, canary_islands, none
        beckham_law: Whether to apply Beckham Law (24% flat rate up to €600k) (default: False)
        dependents: DependentInfo object with information about dependents and family situation
        taxpayer_age: Taxpayer's age in years (affects personal allowance)

    Returns:
        TaxResult object with complete calculation breakdown
    """
    # Normalize region name
    region = region.lower()

    # Initialize dependents if not provided
    if dependents is None:
        dependents = DependentInfo()

    # Determine personal allowance (use age-based if age provided, otherwise use provided value or default)
    if personal_allowance is None:
        personal_allowance = get_personal_allowance_by_age(taxpayer_age)

    # Step 1: Calculate Social Security
    social_security_tax, income_after_ss = _calculate_social_security(gross_income, social_security_rate)

    # Step 2: Calculate allowances
    dependent_allowances = calculate_dependent_allowances(dependents)
    total_allowances = personal_allowance + dependent_allowances

    # Step 3: Calculate taxable income for IRPF
    # Note: Under Beckham Law, personal allowance typically doesn't apply
    if beckham_law:
        taxable_income = income_after_ss  # No allowances under Beckham Law
        total_allowances = 0
        dependent_allowances = 0
    else:
        taxable_income = max(0, income_after_ss - total_allowances)

    # Step 4: Calculate IRPF tax
    if beckham_law:
        beckham_law_tax, beckham_law_excess_tax, irpf_tax, state_breakdown = _calculate_beckham_law_tax(taxable_income)
        state_irpf_tax = irpf_tax
        regional_irpf_tax = 0.0
        regional_breakdown = []
    else:
        state_irpf_tax, regional_irpf_tax, irpf_tax, state_breakdown, regional_breakdown = _calculate_standard_irpf_tax(taxable_income, region)
        beckham_law_tax = 0.0
        beckham_law_excess_tax = 0.0

    # Step 5: Calculate total deductions and net income
    total_deductions = social_security_tax + irpf_tax
    net_income = gross_income - total_deductions
    effective_rate = (total_deductions / gross_income * PERCENTAGE_MULTIPLIER) if gross_income > 0 else 0

    return TaxResult(
        gross_income=gross_income,
        social_security_tax=social_security_tax,
        income_after_ss=income_after_ss,
        personal_allowance=personal_allowance if not beckham_law else 0,
        dependent_allowances=dependent_allowances if not beckham_law else 0,
        total_allowances=total_allowances if not beckham_law else 0,
        taxable_income=taxable_income,
        state_irpf_tax=state_irpf_tax,
        regional_irpf_tax=regional_irpf_tax,
        irpf_tax=irpf_tax,
        total_deductions=total_deductions,
        net_income=net_income,
        effective_rate=effective_rate,
        region=region,
        beckham_law=beckham_law,
        beckham_law_tax=beckham_law_tax,
        beckham_law_excess_tax=beckham_law_excess_tax,
        taxpayer_age=taxpayer_age,
        dependents=dependents,
        state_breakdown=state_breakdown,
        regional_breakdown=regional_breakdown
    )


def _format_region_display(region: str) -> str:
    """Format region name for display."""
    return region.replace('_', ' ').title() if region != 'none' else 'None (State only)'


def _print_header(result: TaxResult):
    """Print the header section of the results."""
    region_display = _format_region_display(result.region)
    regime_display = "Beckham Law (24% flat rate)" if result.beckham_law else "Standard IRPF"
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*HEADER_WIDTH}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}  Spanish Tax Calculation (IRPF + Social Security){Colors.ENDC}")
    if result.beckham_law:
        print(f"{Colors.BOLD}{Colors.HEADER}  Tax Regime: {regime_display}{Colors.ENDC}")
    else:
        print(f"{Colors.BOLD}{Colors.HEADER}  Region: {region_display}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*HEADER_WIDTH}{Colors.ENDC}\n")


def _get_personal_allowance_label(result: TaxResult) -> str:
    """Get the appropriate label for personal allowance based on age."""
    if result.taxpayer_age is None:
        return 'Personal Allowance:'
    if result.taxpayer_age >= AGE_THRESHOLD_75:
        return 'Personal Allowance (75+):'
    elif result.taxpayer_age >= AGE_THRESHOLD_65:
        return 'Personal Allowance (65-74):'
    return 'Personal Allowance:'


def _print_summary(result: TaxResult):
    """Print the summary section of the results."""
    print(f"{Colors.BOLD}{Colors.OKCYAN}Summary:{Colors.ENDC}")
    print(f"  {Colors.OKBLUE}{'Gross Income:':<{SUMMARY_LABEL_WIDTH}}{Colors.ENDC} {Colors.BOLD}{format_currency_aligned(result.gross_income, SUMMARY_VALUE_WIDTH)}{Colors.ENDC}")
    print(f"  {Colors.FAIL}{'Social Security:':<{SUMMARY_LABEL_WIDTH}}{Colors.ENDC} {Colors.FAIL}{format_currency_aligned(result.social_security_tax, SUMMARY_VALUE_WIDTH)}{Colors.ENDC}")
    print(f"  {Colors.OKBLUE}{'Income after SS:':<{SUMMARY_LABEL_WIDTH}}{Colors.ENDC} {format_currency_aligned(result.income_after_ss, SUMMARY_VALUE_WIDTH)}")

    if not result.beckham_law:
        allowance_label = _get_personal_allowance_label(result)
        print(f"  {Colors.OKBLUE}{allowance_label:<{SUMMARY_LABEL_WIDTH}}{Colors.ENDC} {format_currency_aligned(result.personal_allowance, SUMMARY_VALUE_WIDTH)}")
        if result.dependent_allowances > 0:
            print(f"  {Colors.OKBLUE}{'Dependent Allowances:':<{SUMMARY_LABEL_WIDTH}}{Colors.ENDC} {format_currency_aligned(result.dependent_allowances, SUMMARY_VALUE_WIDTH)}")
            print(f"  {Colors.OKBLUE}{'Total Allowances:':<{SUMMARY_LABEL_WIDTH}}{Colors.ENDC} {format_currency_aligned(result.total_allowances, SUMMARY_VALUE_WIDTH)}")

    print(f"  {Colors.OKBLUE}{'Taxable Income (IRPF):':<{SUMMARY_LABEL_WIDTH}}{Colors.ENDC} {format_currency_aligned(result.taxable_income, SUMMARY_VALUE_WIDTH)}")

    if result.beckham_law:
        print(f"  {Colors.FAIL}{'Beckham Law Tax (24%):':<{SUMMARY_LABEL_WIDTH}}{Colors.ENDC} {Colors.FAIL}{format_currency_aligned(result.beckham_law_tax, SUMMARY_VALUE_WIDTH)}{Colors.ENDC}")
        if result.beckham_law_excess_tax > 0:
            print(f"  {Colors.FAIL}{'Excess Tax (>€600k):':<{SUMMARY_LABEL_WIDTH}}{Colors.ENDC} {Colors.FAIL}{format_currency_aligned(result.beckham_law_excess_tax, SUMMARY_VALUE_WIDTH)}{Colors.ENDC}")
    else:
        print(f"  {Colors.FAIL}{'State IRPF Tax:':<{SUMMARY_LABEL_WIDTH}}{Colors.ENDC} {Colors.FAIL}{format_currency_aligned(result.state_irpf_tax, SUMMARY_VALUE_WIDTH)}{Colors.ENDC}")
        if result.regional_irpf_tax > 0:
            print(f"  {Colors.FAIL}{'Regional IRPF Tax:':<{SUMMARY_LABEL_WIDTH}}{Colors.ENDC} {Colors.FAIL}{format_currency_aligned(result.regional_irpf_tax, SUMMARY_VALUE_WIDTH)}{Colors.ENDC}")

    print(f"  {Colors.FAIL}{'Total IRPF Tax:':<{SUMMARY_LABEL_WIDTH}}{Colors.ENDC} {Colors.FAIL}{format_currency_aligned(result.irpf_tax, SUMMARY_VALUE_WIDTH)}{Colors.ENDC}")
    print(f"  {Colors.FAIL}{'Total Deductions:':<{SUMMARY_LABEL_WIDTH}}{Colors.ENDC} {Colors.BOLD}{Colors.FAIL}{format_currency_aligned(result.total_deductions, SUMMARY_VALUE_WIDTH)}{Colors.ENDC}")
    print(f"  {Colors.OKGREEN}{'Net Income:':<{SUMMARY_LABEL_WIDTH}}{Colors.ENDC} {Colors.BOLD}{Colors.OKGREEN}{format_currency_aligned(result.net_income, SUMMARY_VALUE_WIDTH)}{Colors.ENDC}")
    print(f"  {Colors.WARNING}{'Effective Tax Rate:':<{SUMMARY_LABEL_WIDTH}}{Colors.ENDC} {Colors.BOLD}{format_percentage(result.effective_rate / PERCENTAGE_MULTIPLIER):>{SUMMARY_VALUE_WIDTH}}{Colors.ENDC}\n")


def _print_bracket_table(breakdown: List[TaxBreakdown], title: str):
    """Print a bracket breakdown table."""
    print(f"{Colors.BOLD}{Colors.OKCYAN}{title}:{Colors.ENDC}\n")
    print(f"  {Colors.UNDERLINE}{'Bracket':<25} {'Amount':>15} {'Rate':>10} {'Tax':>15}{Colors.ENDC}")
    print(f"  {'-'*TABLE_WIDTH}")
    for bracket in breakdown:
        bracket_str = format_bracket_range(bracket.bracket_min, bracket.bracket_max)
        print(f"  {Colors.OKBLUE}{bracket_str:<25}{Colors.ENDC} "
              f"{format_currency_aligned(bracket.taxable_amount, 15)} "
              f"{format_percentage(bracket.rate):>10} "
              f"{Colors.FAIL}{format_currency_aligned(bracket.tax_amount, 15)}{Colors.ENDC}")
    print()


def _print_beckham_law_breakdown(result: TaxResult):
    """Print Beckham Law tax breakdown."""
    print(f"{Colors.BOLD}{Colors.OKCYAN}Beckham Law Tax Breakdown:{Colors.ENDC}\n")
    print(f"  {Colors.UNDERLINE}{'Income Range':<25} {'Amount':>15} {'Rate':>10} {'Tax':>15}{Colors.ENDC}")
    print(f"  {'-'*TABLE_WIDTH}")

    if result.beckham_law_excess_tax > 0:
        # Show both the flat rate portion and excess
        flat_amount = min(result.taxable_income, BECKHAM_LAW_THRESHOLD)
        print(f"  {Colors.OKBLUE}{'Up to €600,000':<25}{Colors.ENDC} "
              f"{format_currency_aligned(flat_amount, 15)} "
              f"{format_percentage(BECKHAM_LAW_RATE):>10} "
              f"{Colors.FAIL}{format_currency_aligned(result.beckham_law_tax, 15)}{Colors.ENDC}")
        excess_amount = result.taxable_income - BECKHAM_LAW_THRESHOLD
        print(f"  {Colors.OKBLUE}{'Above €600,000':<25}{Colors.ENDC} "
              f"{format_currency_aligned(excess_amount, 15)} "
              f"{Colors.WARNING}{'Progressive':>10}{Colors.ENDC} "
              f"{Colors.FAIL}{format_currency_aligned(result.beckham_law_excess_tax, 15)}{Colors.ENDC}")
        print()
        if result.state_breakdown:
            _print_bracket_table(result.state_breakdown, "Progressive Tax on Excess (>€600k)")
    else:
        # All income within threshold
        print(f"  {Colors.OKBLUE}{'All income':<25}{Colors.ENDC} "
              f"{format_currency_aligned(result.taxable_income, 15)} "
              f"{format_percentage(BECKHAM_LAW_RATE):>10} "
              f"{Colors.FAIL}{format_currency_aligned(result.beckham_law_tax, 15)}{Colors.ENDC}")
        print()


def _print_verbose_breakdown(result: TaxResult):
    """Print detailed tax bracket breakdown."""
    if result.beckham_law:
        _print_beckham_law_breakdown(result)
    else:
        if result.state_breakdown:
            _print_bracket_table(result.state_breakdown, "State IRPF Tax Breakdown")
        if result.regional_breakdown:
            region_display = _format_region_display(result.region)
            _print_bracket_table(result.regional_breakdown, f"Regional IRPF Tax Breakdown ({region_display})")


def _print_monthly_breakdown(result: TaxResult):
    """Print monthly breakdown of income and taxes."""
    print(f"{Colors.BOLD}{Colors.OKCYAN}Monthly Breakdown:{Colors.ENDC}")
    monthly_gross = result.gross_income / MONTHS_PER_YEAR
    monthly_ss = result.social_security_tax / MONTHS_PER_YEAR
    monthly_state_irpf = result.state_irpf_tax / MONTHS_PER_YEAR
    monthly_regional_irpf = result.regional_irpf_tax / MONTHS_PER_YEAR
    monthly_irpf = result.irpf_tax / MONTHS_PER_YEAR
    monthly_deductions = result.total_deductions / MONTHS_PER_YEAR
    monthly_net = result.net_income / MONTHS_PER_YEAR

    print(f"  {Colors.OKBLUE}{'Gross:':<{MONTHLY_LABEL_WIDTH}}{Colors.ENDC} {format_currency_aligned(monthly_gross, MONTHLY_VALUE_WIDTH)}")
    print(f"  {Colors.FAIL}{'Social Security:':<{MONTHLY_LABEL_WIDTH}}{Colors.ENDC} {format_currency_aligned(monthly_ss, MONTHLY_VALUE_WIDTH)}")
    print(f"  {Colors.FAIL}{'State IRPF:':<{MONTHLY_LABEL_WIDTH}}{Colors.ENDC} {format_currency_aligned(monthly_state_irpf, MONTHLY_VALUE_WIDTH)}")
    if result.regional_irpf_tax > 0:
        print(f"  {Colors.FAIL}{'Regional IRPF:':<{MONTHLY_LABEL_WIDTH}}{Colors.ENDC} {format_currency_aligned(monthly_regional_irpf, MONTHLY_VALUE_WIDTH)}")
    print(f"  {Colors.FAIL}{'Total IRPF:':<{MONTHLY_LABEL_WIDTH}}{Colors.ENDC} {format_currency_aligned(monthly_irpf, MONTHLY_VALUE_WIDTH)}")
    print(f"  {Colors.FAIL}{'Total Deductions:':<{MONTHLY_LABEL_WIDTH}}{Colors.ENDC} {format_currency_aligned(monthly_deductions, MONTHLY_VALUE_WIDTH)}")
    print(f"  {Colors.OKGREEN}{'Net:':<{MONTHLY_LABEL_WIDTH}}{Colors.ENDC} {format_currency_aligned(monthly_net, MONTHLY_VALUE_WIDTH)}")
    print()


def print_regional_rates():
    """Print IRPF tax rates by region in a table format."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}  Spanish IRPF Tax Rates by Region (2024){Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}\n")

    # Table header
    print(f"{Colors.BOLD}{Colors.UNDERLINE}{'Region':<20} {'Income Range':<25} {'State':>8} {'Regional':>10} {'Total':>8}{Colors.ENDC}")
    print(f"{'-'*80}")

    # Print state rates (same for all regions)
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}State IRPF Rates (applies to all regions):{Colors.ENDC}\n")
    for bracket_min, bracket_max, rate in STATE_TAX_BRACKETS:
        bracket_str = format_bracket_range(bracket_min, bracket_max)
        print(f"  {bracket_str:<25} {format_percentage(rate):>8}")

    # Print regional rates
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}Regional IRPF Rates (in addition to state rates):{Colors.ENDC}\n")

    # Sort regions for consistent display
    sorted_regions = sorted([r for r in VALID_REGIONS if r != 'none'])

    for region in sorted_regions:
        region_display = _format_region_display(region)
        brackets = REGIONAL_TAX_BRACKETS.get(region, [])
        if brackets:
            print(f"{Colors.BOLD}{Colors.OKBLUE}{region_display}:{Colors.ENDC}")
            for i, (bracket_min, bracket_max, regional_rate) in enumerate(brackets):
                bracket_str = format_bracket_range(bracket_min, bracket_max)
                # Match state bracket by index (they have the same structure)
                state_rate = STATE_TAX_BRACKETS[i][2]
                total_rate = state_rate + regional_rate
                print(f"  {bracket_str:<25} {format_percentage(state_rate):>8} "
                      f"{format_percentage(regional_rate):>10} {Colors.BOLD}{format_percentage(total_rate):>8}{Colors.ENDC}")
            print()

    # Summary table showing total rates by region
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}Total IRPF Rates by Region (State + Regional):{Colors.ENDC}\n")
    print(f"{Colors.BOLD}{Colors.UNDERLINE}{'Region':<20} {'Income Range':<25} {'Total Rate':>12}{Colors.ENDC}")
    print(f"{'-'*60}")

    for region in sorted_regions:
        region_display = _format_region_display(region)
        brackets = REGIONAL_TAX_BRACKETS.get(region, [])
        if brackets:
            for i, (bracket_min, bracket_max, regional_rate) in enumerate(brackets):
                bracket_str = format_bracket_range(bracket_min, bracket_max)
                # Match state bracket by index (they have the same structure)
                state_rate = STATE_TAX_BRACKETS[i][2]
                total_rate = state_rate + regional_rate
                print(f"  {region_display:<20} {bracket_str:<25} {Colors.BOLD}{format_percentage(total_rate):>12}{Colors.ENDC}")
        print()

    # Show "none" option
    print(f"{Colors.BOLD}{Colors.OKCYAN}State Only (no regional tax):{Colors.ENDC}\n")
    print(f"{Colors.BOLD}{Colors.UNDERLINE}{'Region':<20} {'Income Range':<25} {'Total Rate':>12}{Colors.ENDC}")
    print(f"{'-'*60}")
    for bracket_min, bracket_max, rate in STATE_TAX_BRACKETS:
        bracket_str = format_bracket_range(bracket_min, bracket_max)
        print(f"  {'None (State only)':<20} {bracket_str:<25} {Colors.BOLD}{format_percentage(rate):>12}{Colors.ENDC}")

    print()


def print_results(result: TaxResult, verbose: bool = False):
    """Print tax calculation results with colored output."""
    _print_header(result)
    _print_summary(result)

    if verbose:
        _print_verbose_breakdown(result)

    _print_monthly_breakdown(result)


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description='Calculate Spanish IRPF (Personal Income Tax) and Social Security',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 60000                    # Calculate tax for €60,000 annual income
  %(prog)s 50000 --verbose          # Show detailed bracket breakdown
  %(prog)s 45000 --allowance 7000   # Use custom personal allowance
  %(prog)s 35000 --monthly          # Input as monthly income
  %(prog)s 60000 --ss-rate 0.0635   # Use custom social security rate
  %(prog)s 60000 --region madrid    # Calculate for Madrid region
  %(prog)s 60000 --region catalonia # Calculate for Catalonia region
  %(prog)s 100000 --beckham-law     # Apply Beckham Law (24%% flat rate)

  # Dependents examples:
  %(prog)s 60000 --children-under-3 1 --children-3-plus 2
  %(prog)s 60000 --children-disability-65 1 --ascendants-65 2
  %(prog)s 60000 --large-family --single-parent
  %(prog)s 60000 --taxpayer-disability-65

  # Age examples:
  %(prog)s 60000 --age 68              # Age 68 (higher personal allowance)
  %(prog)s 60000 --age 75              # Age 75+ (highest personal allowance)

Available regions: madrid, catalonia, andalusia, valencia, basque, galicia, castilla_leon, canary_islands, none
        """
    )

    parser.add_argument(
        'income',
        type=float,
        nargs='?',
        default=None,
        help='Annual income in euros (or monthly if --monthly is used). Optional if --show-regions is used.'
    )

    parser.add_argument(
        '--monthly',
        action='store_true',
        help='Treat income as monthly instead of annual'
    )

    parser.add_argument(
        '--age',
        type=int,
        default=None,
        help='Taxpayer age in years (affects personal allowance: <65=€5,550, 65-74=€6,700, 75+=€8,100)'
    )

    parser.add_argument(
        '--allowance',
        type=float,
        default=None,
        help=f'Personal allowance amount (overrides age-based calculation if provided). Default: €{PERSONAL_ALLOWANCE_UNDER_65:,.0f} or age-based'
    )

    parser.add_argument(
        '--ss-rate',
        type=float,
        default=SOCIAL_SECURITY_RATE,
        help=f'Social security rate as decimal (default: {SOCIAL_SECURITY_RATE:.4f} = {SOCIAL_SECURITY_RATE*100:.2f}%%)'
    )

    parser.add_argument(
        '--region',
        type=str,
        default='none',
        choices=VALID_REGIONS,
        help=f'Spanish region for regional IRPF tax (default: none). Options: {", ".join(VALID_REGIONS)}'
    )

    parser.add_argument(
        '--beckham-law',
        action='store_true',
        help='Apply Beckham Law (24%% flat rate on income up to €600,000). Income above €600k taxed at normal progressive rates. Regional tax does not apply.'
    )

    # Dependent options
    parser.add_argument(
        '--children-under-3',
        type=int,
        default=0,
        help='Number of children under 3 years old'
    )

    parser.add_argument(
        '--children-3-plus',
        type=int,
        default=0,
        help='Number of children 3 years old or older'
    )

    parser.add_argument(
        '--children-disability-33',
        type=int,
        default=0,
        help='Number of children with 33%% or more disability'
    )

    parser.add_argument(
        '--children-disability-65',
        type=int,
        default=0,
        help='Number of children with 65%% or more disability'
    )

    parser.add_argument(
        '--ascendants-65',
        type=int,
        default=0,
        help='Number of ascendants (parents/grandparents) over 65 years old'
    )

    parser.add_argument(
        '--ascendants-disability-33',
        type=int,
        default=0,
        help='Number of ascendants with 33%% or more disability'
    )

    parser.add_argument(
        '--ascendants-disability-65',
        type=int,
        default=0,
        help='Number of ascendants with 65%% or more disability'
    )

    parser.add_argument(
        '--large-family',
        action='store_true',
        help='Large family status (general)'
    )

    parser.add_argument(
        '--large-family-special',
        action='store_true',
        help='Special large family status (5+ children or 4+ with disability)'
    )

    parser.add_argument(
        '--single-parent',
        action='store_true',
        help='Single parent family status'
    )

    parser.add_argument(
        '--taxpayer-disability-33',
        action='store_true',
        help='Taxpayer has 33%% or more disability'
    )

    parser.add_argument(
        '--taxpayer-disability-65',
        action='store_true',
        help='Taxpayer has 65%% or more disability'
    )

    parser.add_argument(
        '--taxpayer-disability-mobility',
        action='store_true',
        help='Taxpayer has mobility disability'
    )

    parser.add_argument(
        '--taxpayer-disability-dependency',
        action='store_true',
        help='Taxpayer requires assistance due to dependency'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed tax bracket breakdown'
    )

    parser.add_argument(
        '--show-regions',
        action='store_true',
        help='Show IRPF tax rates by region and exit'
    )

    args = parser.parse_args()

    # Handle --show-regions command
    if args.show_regions:
        print_regional_rates()
        sys.exit(0)

    # Validate that income is provided if not showing regions
    if args.income is None:
        print(f"{Colors.FAIL}Error: Income is required unless --show-regions is used{Colors.ENDC}", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    # Convert monthly to annual if needed
    annual_income = args.income * MONTHS_PER_YEAR if args.monthly else args.income

    # Validate input
    if annual_income < 0:
        print(f"{Colors.FAIL}Error: Income cannot be negative{Colors.ENDC}", file=sys.stderr)
        sys.exit(1)

    if args.ss_rate < 0 or args.ss_rate > 1:
        print(f"{Colors.FAIL}Error: Social security rate must be between 0 and 1{Colors.ENDC}", file=sys.stderr)
        sys.exit(1)

    if args.age is not None and (args.age < 0 or args.age > MAX_REASONABLE_AGE):
        print(f"{Colors.FAIL}Error: Age must be between 0 and {MAX_REASONABLE_AGE}{Colors.ENDC}", file=sys.stderr)
        sys.exit(1)

    # Build dependents info
    dependents = DependentInfo(
        children_under_3=args.children_under_3,
        children_3_plus=args.children_3_plus,
        children_disability_33=args.children_disability_33,
        children_disability_65=args.children_disability_65,
        ascendants_65=args.ascendants_65,
        ascendants_disability_33=args.ascendants_disability_33,
        ascendants_disability_65=args.ascendants_disability_65,
        large_family=args.large_family,
        large_family_special=args.large_family_special,
        single_parent=args.single_parent,
        taxpayer_disability_33=args.taxpayer_disability_33,
        taxpayer_disability_65=args.taxpayer_disability_65,
        taxpayer_disability_mobility=args.taxpayer_disability_mobility,
        taxpayer_disability_dependency=args.taxpayer_disability_dependency
    )

    # Calculate tax
    try:
        result = calculate_tax(annual_income, args.allowance, args.ss_rate, args.region, args.beckham_law, dependents, args.age)
        print_results(result, args.verbose)
    except Exception as e:
        print(f"{Colors.FAIL}Error calculating tax: {e}{Colors.ENDC}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
