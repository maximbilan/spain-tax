#!/usr/bin/env python3
"""
Unit tests for Spanish Tax Calculator
"""

import unittest
from tax_calculator import (
    calculate_tax,
    calculate_dependent_allowances,
    calculate_bracket_tax,
    get_personal_allowance_by_age,
    DependentInfo,
    TaxResult,
    STATE_TAX_BRACKETS,
    REGIONAL_TAX_BRACKETS,
    PERSONAL_ALLOWANCE_UNDER_65,
    PERSONAL_ALLOWANCE_65_74,
    PERSONAL_ALLOWANCE_75_PLUS,
    SOCIAL_SECURITY_RATE,
    BECKHAM_LAW_THRESHOLD,
    BECKHAM_LAW_RATE,
    ALLOWANCE_FIRST_CHILD,
    ALLOWANCE_SECOND_CHILD,
    ALLOWANCE_THIRD_CHILD,
    ALLOWANCE_FOURTH_PLUS_CHILD,
    ALLOWANCE_CHILD_UNDER_3,
    ALLOWANCE_CHILD_DISABILITY_33,
    ALLOWANCE_CHILD_DISABILITY_65,
    ALLOWANCE_ASCENDANT_65,
    ALLOWANCE_ASCENDANT_DISABILITY_33,
    ALLOWANCE_ASCENDANT_DISABILITY_65,
    ALLOWANCE_LARGE_FAMILY_GENERAL,
    ALLOWANCE_LARGE_FAMILY_SPECIAL,
    ALLOWANCE_SINGLE_PARENT,
    ALLOWANCE_DISABILITY_33,
    ALLOWANCE_DISABILITY_65,
    ALLOWANCE_DISABILITY_MOBILITY,
    ALLOWANCE_DISABILITY_DEPENDENCY,
    AUTONOMO_MIN_BASE_MONTHLY,
    AUTONOMO_MAX_BASE_MONTHLY,
    AUTONOMO_FULL_RATE,
    AUTONOMO_REDUCED_RATE_MONTHS_1_12,
    AUTONOMO_REDUCED_RATE_MONTHS_13_24,
    AUTONOMO_DEFAULT_BASE_PERCENTAGE,
    AUTONOMO_GENERAL_EXPENSE_RATE,
)


class TestPersonalAllowanceByAge(unittest.TestCase):
    """Test personal allowance calculation based on age."""

    def test_under_65(self):
        """Test personal allowance for taxpayers under 65."""
        self.assertEqual(get_personal_allowance_by_age(30), PERSONAL_ALLOWANCE_UNDER_65)
        self.assertEqual(get_personal_allowance_by_age(64), PERSONAL_ALLOWANCE_UNDER_65)

    def test_65_to_74(self):
        """Test personal allowance for taxpayers 65-74."""
        self.assertEqual(get_personal_allowance_by_age(65), PERSONAL_ALLOWANCE_65_74)
        self.assertEqual(get_personal_allowance_by_age(70), PERSONAL_ALLOWANCE_65_74)
        self.assertEqual(get_personal_allowance_by_age(74), PERSONAL_ALLOWANCE_65_74)

    def test_75_plus(self):
        """Test personal allowance for taxpayers 75+."""
        self.assertEqual(get_personal_allowance_by_age(75), PERSONAL_ALLOWANCE_75_PLUS)
        self.assertEqual(get_personal_allowance_by_age(80), PERSONAL_ALLOWANCE_75_PLUS)

    def test_none_age(self):
        """Test personal allowance when age is None."""
        self.assertEqual(get_personal_allowance_by_age(None), PERSONAL_ALLOWANCE_UNDER_65)

    def test_age_boundary_64_to_65(self):
        """Test exact boundary between age groups."""
        self.assertEqual(get_personal_allowance_by_age(64), PERSONAL_ALLOWANCE_UNDER_65)
        self.assertEqual(get_personal_allowance_by_age(65), PERSONAL_ALLOWANCE_65_74)

    def test_age_boundary_74_to_75(self):
        """Test exact boundary between 65-74 and 75+ groups."""
        self.assertEqual(get_personal_allowance_by_age(74), PERSONAL_ALLOWANCE_65_74)
        self.assertEqual(get_personal_allowance_by_age(75), PERSONAL_ALLOWANCE_75_PLUS)


class TestDependentAllowances(unittest.TestCase):
    """Test dependent allowance calculations."""

    def test_no_dependents(self):
        """Test with no dependents."""
        dependents = DependentInfo()
        self.assertEqual(calculate_dependent_allowances(dependents), 0.0)

    def test_first_child(self):
        """Test allowance for first child."""
        dependents = DependentInfo(children_3_plus=1)
        self.assertEqual(calculate_dependent_allowances(dependents), ALLOWANCE_FIRST_CHILD)

    def test_first_child_under_3(self):
        """Test allowance for first child under 3."""
        dependents = DependentInfo(children_under_3=1)
        expected = ALLOWANCE_FIRST_CHILD + ALLOWANCE_CHILD_UNDER_3
        self.assertEqual(calculate_dependent_allowances(dependents), expected)

    def test_second_child(self):
        """Test allowance for second child."""
        dependents = DependentInfo(children_3_plus=2)
        expected = ALLOWANCE_FIRST_CHILD + ALLOWANCE_SECOND_CHILD
        self.assertEqual(calculate_dependent_allowances(dependents), expected)

    def test_third_child(self):
        """Test allowance for third child."""
        dependents = DependentInfo(children_3_plus=3)
        expected = ALLOWANCE_FIRST_CHILD + ALLOWANCE_SECOND_CHILD + ALLOWANCE_THIRD_CHILD
        self.assertEqual(calculate_dependent_allowances(dependents), expected)

    def test_fourth_child(self):
        """Test allowance for fourth child."""
        dependents = DependentInfo(children_3_plus=4)
        expected = (ALLOWANCE_FIRST_CHILD + ALLOWANCE_SECOND_CHILD + ALLOWANCE_THIRD_CHILD +
                    ALLOWANCE_FOURTH_PLUS_CHILD)
        self.assertEqual(calculate_dependent_allowances(dependents), expected)

    def test_multiple_children_mixed_ages(self):
        """Test allowances for multiple children with mixed ages."""
        dependents = DependentInfo(children_under_3=1, children_3_plus=2)
        expected = (ALLOWANCE_FIRST_CHILD + ALLOWANCE_CHILD_UNDER_3 +  # First child (under 3)
                    ALLOWANCE_SECOND_CHILD +  # Second child
                    ALLOWANCE_THIRD_CHILD)  # Third child
        self.assertEqual(calculate_dependent_allowances(dependents), expected)

    def test_child_disability_33(self):
        """Test allowance for child with 33%+ disability."""
        dependents = DependentInfo(children_disability_33=1)
        self.assertEqual(calculate_dependent_allowances(dependents), ALLOWANCE_CHILD_DISABILITY_33)

    def test_child_disability_65(self):
        """Test allowance for child with 65%+ disability."""
        dependents = DependentInfo(children_disability_65=1)
        self.assertEqual(calculate_dependent_allowances(dependents), ALLOWANCE_CHILD_DISABILITY_65)

    def test_ascendant_65(self):
        """Test allowance for ascendant over 65."""
        dependents = DependentInfo(ascendants_65=1)
        self.assertEqual(calculate_dependent_allowances(dependents), ALLOWANCE_ASCENDANT_65)

    def test_ascendant_disability_33(self):
        """Test allowance for ascendant with 33%+ disability."""
        dependents = DependentInfo(ascendants_disability_33=1)
        self.assertEqual(calculate_dependent_allowances(dependents), ALLOWANCE_ASCENDANT_DISABILITY_33)

    def test_ascendant_disability_65(self):
        """Test allowance for ascendant with 65%+ disability."""
        dependents = DependentInfo(ascendants_disability_65=1)
        self.assertEqual(calculate_dependent_allowances(dependents), ALLOWANCE_ASCENDANT_DISABILITY_65)

    def test_multiple_ascendants(self):
        """Test allowances for multiple ascendants."""
        dependents = DependentInfo(ascendants_65=2, ascendants_disability_33=1)
        expected = (2 * ALLOWANCE_ASCENDANT_65 + ALLOWANCE_ASCENDANT_DISABILITY_33)
        self.assertEqual(calculate_dependent_allowances(dependents), expected)

    def test_large_family(self):
        """Test allowance for large family."""
        dependents = DependentInfo(large_family=True)
        self.assertEqual(calculate_dependent_allowances(dependents), ALLOWANCE_LARGE_FAMILY_GENERAL)

    def test_large_family_special(self):
        """Test allowance for special large family (takes precedence over general)."""
        dependents = DependentInfo(large_family_special=True)
        self.assertEqual(calculate_dependent_allowances(dependents), ALLOWANCE_LARGE_FAMILY_SPECIAL)

    def test_large_family_special_precedence(self):
        """Test that special large family takes precedence over general."""
        dependents = DependentInfo(large_family=True, large_family_special=True)
        # Special should take precedence
        self.assertEqual(calculate_dependent_allowances(dependents), ALLOWANCE_LARGE_FAMILY_SPECIAL)

    def test_single_parent(self):
        """Test allowance for single parent."""
        dependents = DependentInfo(single_parent=True)
        self.assertEqual(calculate_dependent_allowances(dependents), ALLOWANCE_SINGLE_PARENT)

    def test_taxpayer_disability_33(self):
        """Test allowance for taxpayer with 33%+ disability."""
        dependents = DependentInfo(taxpayer_disability_33=True)
        self.assertEqual(calculate_dependent_allowances(dependents), ALLOWANCE_DISABILITY_33)

    def test_taxpayer_disability_65(self):
        """Test allowance for taxpayer with 65%+ disability."""
        dependents = DependentInfo(taxpayer_disability_65=True)
        self.assertEqual(calculate_dependent_allowances(dependents), ALLOWANCE_DISABILITY_65)

    def test_taxpayer_disability_mobility(self):
        """Test allowance for taxpayer with mobility disability."""
        dependents = DependentInfo(taxpayer_disability_mobility=True)
        self.assertEqual(calculate_dependent_allowances(dependents), ALLOWANCE_DISABILITY_MOBILITY)

    def test_taxpayer_disability_dependency(self):
        """Test allowance for taxpayer requiring assistance."""
        dependents = DependentInfo(taxpayer_disability_dependency=True)
        self.assertEqual(calculate_dependent_allowances(dependents), ALLOWANCE_DISABILITY_DEPENDENCY)

    def test_taxpayer_disability_priority(self):
        """Test that taxpayer disability allowances follow priority (dependency > 65% > mobility > 33%)."""
        # Dependency has highest priority
        dependents = DependentInfo(taxpayer_disability_dependency=True, taxpayer_disability_65=True,
                                   taxpayer_disability_mobility=True, taxpayer_disability_33=True)
        self.assertEqual(calculate_dependent_allowances(dependents), ALLOWANCE_DISABILITY_DEPENDENCY)

        # 65% has priority over mobility and 33%
        dependents = DependentInfo(taxpayer_disability_65=True, taxpayer_disability_mobility=True,
                                   taxpayer_disability_33=True)
        self.assertEqual(calculate_dependent_allowances(dependents), ALLOWANCE_DISABILITY_65)

        # Mobility has priority over 33%
        dependents = DependentInfo(taxpayer_disability_mobility=True, taxpayer_disability_33=True)
        self.assertEqual(calculate_dependent_allowances(dependents), ALLOWANCE_DISABILITY_MOBILITY)

    def test_complex_scenario(self):
        """Test complex scenario with multiple allowances."""
        dependents = DependentInfo(
            children_under_3=1,
            children_3_plus=1,
            children_disability_33=1,
            ascendants_65=2,
            large_family=True,
            taxpayer_disability_33=True
        )
        expected = (
            ALLOWANCE_FIRST_CHILD + ALLOWANCE_CHILD_UNDER_3 +  # First child under 3
            ALLOWANCE_SECOND_CHILD +  # Second child
            ALLOWANCE_CHILD_DISABILITY_33 +  # Child disability
            2 * ALLOWANCE_ASCENDANT_65 +  # Two ascendants
            ALLOWANCE_LARGE_FAMILY_GENERAL +  # Large family
            ALLOWANCE_DISABILITY_33  # Taxpayer disability
        )
        self.assertEqual(calculate_dependent_allowances(dependents), expected)


class TestBracketTaxCalculation(unittest.TestCase):
    """Test tax bracket calculation."""

    def test_single_bracket(self):
        """Test tax calculation for income in single bracket."""
        brackets = [(0, 10000, 0.10)]
        tax, breakdown = calculate_bracket_tax(5000, brackets)
        self.assertEqual(tax, 500.0)
        self.assertEqual(len(breakdown), 1)
        self.assertEqual(breakdown[0].taxable_amount, 5000.0)
        self.assertEqual(breakdown[0].rate, 0.10)
        self.assertEqual(breakdown[0].tax_amount, 500.0)

    def test_multiple_brackets(self):
        """Test tax calculation across multiple brackets."""
        brackets = [
            (0, 10000, 0.10),
            (10000, 20000, 0.20),
            (20000, 30000, 0.30),
        ]
        tax, breakdown = calculate_bracket_tax(25000, brackets)
        expected_tax = (10000 * 0.10 + 10000 * 0.20 + 5000 * 0.30)
        self.assertAlmostEqual(tax, expected_tax, places=2)
        self.assertEqual(len(breakdown), 3)

    def test_zero_income(self):
        """Test tax calculation for zero income."""
        brackets = [(0, 10000, 0.10)]
        tax, breakdown = calculate_bracket_tax(0, brackets)
        self.assertEqual(tax, 0.0)
        self.assertEqual(len(breakdown), 0)

    def test_income_below_first_bracket(self):
        """Test tax calculation for income below first bracket."""
        brackets = [(10000, 20000, 0.10)]
        tax, breakdown = calculate_bracket_tax(5000, brackets)
        self.assertEqual(tax, 0.0)
        self.assertEqual(len(breakdown), 0)

    def test_infinite_upper_bound(self):
        """Test tax calculation with infinite upper bound."""
        brackets = [(0, float('inf'), 0.10)]
        tax, breakdown = calculate_bracket_tax(100000, brackets)
        self.assertEqual(tax, 10000.0)
        self.assertEqual(len(breakdown), 1)
        self.assertIsNone(breakdown[0].bracket_max)

    def test_exact_bracket_boundary(self):
        """Test tax calculation at exact bracket boundaries."""
        brackets = [
            (0, 10000, 0.10),
            (10000, 20000, 0.20),
        ]
        # At first bracket boundary
        tax, breakdown = calculate_bracket_tax(10000, brackets)
        self.assertAlmostEqual(tax, 1000.0, places=2)
        self.assertEqual(len(breakdown), 1)
        # Just above first bracket boundary
        tax, breakdown = calculate_bracket_tax(10001, brackets)
        expected = 10000 * 0.10 + 1 * 0.20
        self.assertAlmostEqual(tax, expected, places=2)
        self.assertEqual(len(breakdown), 2)

    def test_state_brackets_exact_values(self):
        """Test exact tax calculation using real state brackets."""
        # Test income at €12,450 (first bracket boundary)
        tax, breakdown = calculate_bracket_tax(12450, STATE_TAX_BRACKETS)
        expected = 12450 * 0.19
        self.assertAlmostEqual(tax, expected, places=2)

        # Test income at €20,200 (second bracket boundary)
        tax, breakdown = calculate_bracket_tax(20200, STATE_TAX_BRACKETS)
        expected = 12450 * 0.19 + (20200 - 12450) * 0.24
        self.assertAlmostEqual(tax, expected, places=2)


class TestStandardTaxCalculation(unittest.TestCase):
    """Test standard tax calculation (non-Beckham Law)."""

    def test_exact_calculation_60000_no_region(self):
        """Test exact tax calculation for €60,000 with no regional tax."""
        result = calculate_tax(60000, region='none')

        # Verify Social Security
        expected_ss = 60000 * SOCIAL_SECURITY_RATE
        self.assertAlmostEqual(result.social_security_tax, expected_ss, places=2)

        # Verify income after SS
        expected_income_after_ss = 60000 - expected_ss
        self.assertAlmostEqual(result.income_after_ss, expected_income_after_ss, places=2)

        # Verify personal allowance
        self.assertEqual(result.personal_allowance, PERSONAL_ALLOWANCE_UNDER_65)

        # Verify taxable income
        expected_taxable = max(0, expected_income_after_ss - PERSONAL_ALLOWANCE_UNDER_65)
        self.assertAlmostEqual(result.taxable_income, expected_taxable, places=2)

        # Verify net income calculation
        expected_net = result.gross_income - result.total_deductions
        self.assertAlmostEqual(result.net_income, expected_net, places=2)

        # Verify effective rate
        expected_rate = (result.total_deductions / result.gross_income) * 100
        self.assertAlmostEqual(result.effective_rate, expected_rate, places=2)

    def test_exact_calculation_60000_madrid(self):
        """Test exact tax calculation for €60,000 in Madrid region."""
        result = calculate_tax(60000, region='madrid')

        # Should have both state and regional tax
        self.assertGreater(result.state_irpf_tax, 0)
        self.assertGreater(result.regional_irpf_tax, 0)
        self.assertEqual(result.region, 'madrid')

        # Total IRPF should be sum of state and regional
        self.assertAlmostEqual(result.irpf_tax, result.state_irpf_tax + result.regional_irpf_tax, places=2)

    def test_income_below_personal_allowance(self):
        """Test tax calculation when income is below personal allowance."""
        income = 5000  # Below personal allowance
        result = calculate_tax(income, region='none')
        self.assertEqual(result.taxable_income, 0)
        self.assertEqual(result.irpf_tax, 0.0)
        # Should still pay Social Security
        self.assertGreater(result.social_security_tax, 0)

    def test_income_exactly_at_personal_allowance(self):
        """Test tax calculation when income exactly equals personal allowance after SS."""
        # Income after SS should equal personal allowance
        income_after_ss = PERSONAL_ALLOWANCE_UNDER_65
        income = income_after_ss / (1 - SOCIAL_SECURITY_RATE)
        result = calculate_tax(income, region='none')
        self.assertAlmostEqual(result.taxable_income, 0, places=2)
        self.assertAlmostEqual(result.irpf_tax, 0.0, places=2)

    def test_age_based_allowance(self):
        """Test tax calculation with age-based personal allowance."""
        result_young = calculate_tax(60000, taxpayer_age=30, region='none')
        result_65 = calculate_tax(60000, taxpayer_age=65, region='none')
        result_75 = calculate_tax(60000, taxpayer_age=75, region='none')

        self.assertEqual(result_young.personal_allowance, PERSONAL_ALLOWANCE_UNDER_65)
        self.assertEqual(result_65.personal_allowance, PERSONAL_ALLOWANCE_65_74)
        self.assertEqual(result_75.personal_allowance, PERSONAL_ALLOWANCE_75_PLUS)

        # Higher allowance should result in lower tax
        self.assertLess(result_75.irpf_tax, result_young.irpf_tax)
        self.assertLess(result_65.irpf_tax, result_young.irpf_tax)

    def test_custom_personal_allowance(self):
        """Test tax calculation with custom personal allowance."""
        custom_allowance = 10000
        result = calculate_tax(60000, personal_allowance=custom_allowance, region='none')
        self.assertEqual(result.personal_allowance, custom_allowance)

    def test_custom_social_security_rate(self):
        """Test tax calculation with custom social security rate."""
        custom_rate = 0.05
        result = calculate_tax(60000, social_security_rate=custom_rate, region='none')
        expected_ss = 60000 * custom_rate
        self.assertAlmostEqual(result.social_security_tax, expected_ss, places=2)

    def test_social_security_rate_zero(self):
        """Test tax calculation with zero social security rate."""
        result = calculate_tax(60000, social_security_rate=0.0, region='none')
        self.assertEqual(result.social_security_tax, 0.0)
        self.assertEqual(result.income_after_ss, result.gross_income)

    def test_with_dependents(self):
        """Test tax calculation with dependents."""
        dependents = DependentInfo(children_3_plus=2, large_family=True)
        result = calculate_tax(60000, dependents=dependents, region='none')
        self.assertGreater(result.dependent_allowances, 0)
        self.assertGreater(result.total_allowances, result.personal_allowance)
        # Taxable income should be reduced by total allowances
        expected_taxable = max(0, result.income_after_ss - result.total_allowances)
        self.assertAlmostEqual(result.taxable_income, expected_taxable, places=2)

    def test_all_regions(self):
        """Test that all valid regions work correctly."""
        valid_regions = ['madrid', 'catalonia', 'andalusia', 'valencia', 'basque',
                         'galicia', 'castilla_leon', 'canary_islands', 'none']
        for region in valid_regions:
            result = calculate_tax(60000, region=region)
            self.assertEqual(result.region, region)
            if region == 'none':
                self.assertEqual(result.regional_irpf_tax, 0.0)
            else:
                self.assertGreater(result.regional_irpf_tax, 0)

    def test_region_normalization(self):
        """Test that region names are normalized to lowercase."""
        result = calculate_tax(60000, region='MADRID')
        self.assertEqual(result.region, 'madrid')

    def test_breakdown_included(self):
        """Test that tax breakdown is included in result."""
        result = calculate_tax(60000, region='madrid')
        self.assertGreater(len(result.state_breakdown), 0)
        self.assertGreater(len(result.regional_breakdown), 0)
        # Verify breakdown sums match total tax
        state_sum = sum(b.tax_amount for b in result.state_breakdown)
        self.assertAlmostEqual(result.state_irpf_tax, state_sum, places=2)
        regional_sum = sum(b.tax_amount for b in result.regional_breakdown)
        self.assertAlmostEqual(result.regional_irpf_tax, regional_sum, places=2)

    def test_high_income_highest_bracket(self):
        """Test tax calculation for high income hitting highest bracket (47%)."""
        # Income that after SS exceeds €300k threshold
        high_income = 350000
        result = calculate_tax(high_income, region='none')
        income_after_ss = high_income * (1 - SOCIAL_SECURITY_RATE)
        if income_after_ss > 300000:
            # Should have breakdown entry with 47% rate
            self.assertTrue(any(b.rate == 0.47 for b in result.state_breakdown))
            # Verify highest bracket tax is calculated
            highest_bracket_tax = sum(b.tax_amount for b in result.state_breakdown if b.rate == 0.47)
            self.assertGreater(highest_bracket_tax, 0)

    def test_none_dependents(self):
        """Test that None dependents are handled correctly."""
        result = calculate_tax(60000, dependents=None, region='none')
        self.assertIsNotNone(result.dependents)
        self.assertEqual(result.dependent_allowances, 0)


class TestBeckhamLawCalculation(unittest.TestCase):
    """Test Beckham Law tax calculation."""

    def test_beckham_law_below_threshold(self):
        """Test Beckham Law for income below threshold."""
        income = 500000
        result = calculate_tax(income, beckham_law=True, region='none')
        self.assertTrue(result.beckham_law)
        self.assertEqual(result.regional_irpf_tax, 0.0)
        income_after_ss = income * (1 - SOCIAL_SECURITY_RATE)
        expected_tax = income_after_ss * BECKHAM_LAW_RATE
        self.assertAlmostEqual(result.beckham_law_tax, expected_tax, places=0)
        self.assertEqual(result.beckham_law_excess_tax, 0.0)

    def test_beckham_law_at_threshold(self):
        """Test Beckham Law for income at threshold."""
        # Income after SS should be at threshold
        income_after_ss = BECKHAM_LAW_THRESHOLD
        income = income_after_ss / (1 - SOCIAL_SECURITY_RATE)
        result = calculate_tax(income, beckham_law=True, region='none')
        self.assertTrue(result.beckham_law)
        expected_tax = BECKHAM_LAW_THRESHOLD * BECKHAM_LAW_RATE
        self.assertAlmostEqual(result.beckham_law_tax, expected_tax, places=0)
        self.assertEqual(result.beckham_law_excess_tax, 0.0)

    def test_beckham_law_above_threshold(self):
        """Test Beckham Law for income above threshold."""
        income = 700000
        result = calculate_tax(income, beckham_law=True, region='none')
        self.assertTrue(result.beckham_law)
        income_after_ss = income * (1 - SOCIAL_SECURITY_RATE)
        expected_flat_tax = BECKHAM_LAW_THRESHOLD * BECKHAM_LAW_RATE
        self.assertAlmostEqual(result.beckham_law_tax, expected_flat_tax, places=0)
        self.assertGreater(result.beckham_law_excess_tax, 0)
        self.assertGreater(len(result.state_breakdown), 0)
        # Total IRPF should be flat tax + excess tax
        self.assertAlmostEqual(result.irpf_tax, result.beckham_law_tax + result.beckham_law_excess_tax, places=2)

    def test_beckham_law_no_allowances(self):
        """Test that Beckham Law doesn't apply personal allowances."""
        result = calculate_tax(500000, beckham_law=True, region='none')
        self.assertTrue(result.beckham_law)
        self.assertEqual(result.personal_allowance, 0)
        self.assertEqual(result.dependent_allowances, 0)
        self.assertEqual(result.total_allowances, 0)
        # Taxable income should equal income after SS
        self.assertAlmostEqual(result.taxable_income, result.income_after_ss, places=2)

    def test_beckham_law_no_regional_tax(self):
        """Test that Beckham Law doesn't apply regional tax."""
        result = calculate_tax(500000, beckham_law=True, region='madrid')
        self.assertTrue(result.beckham_law)
        self.assertEqual(result.regional_irpf_tax, 0.0)
        self.assertEqual(len(result.regional_breakdown), 0)

    def test_beckham_law_vs_standard(self):
        """Test that Beckham Law results in different tax than standard."""
        income = 500000
        result_beckham = calculate_tax(income, beckham_law=True, region='none')
        result_standard = calculate_tax(income, beckham_law=False, region='none')
        self.assertNotEqual(result_beckham.irpf_tax, result_standard.irpf_tax)
        # Beckham Law should generally result in lower tax for high earners
        self.assertLess(result_beckham.irpf_tax, result_standard.irpf_tax)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def test_zero_income(self):
        """Test calculation with zero income."""
        result = calculate_tax(0, region='none')
        self.assertEqual(result.gross_income, 0)
        self.assertEqual(result.social_security_tax, 0)
        self.assertEqual(result.irpf_tax, 0)
        self.assertEqual(result.net_income, 0)
        self.assertEqual(result.effective_rate, 0)
        self.assertEqual(result.taxable_income, 0)

    def test_very_low_income(self):
        """Test calculation with very low income (below personal allowance)."""
        result = calculate_tax(1000, region='none')
        self.assertGreaterEqual(result.net_income, 0)
        self.assertLessEqual(result.effective_rate, 100)
        # Should only pay Social Security, no IRPF
        self.assertEqual(result.irpf_tax, 0.0)
        self.assertGreater(result.social_security_tax, 0)

    def test_very_high_income(self):
        """Test calculation with very high income."""
        result = calculate_tax(1000000, region='none')
        self.assertGreater(result.irpf_tax, 0)
        self.assertLess(result.net_income, result.gross_income)
        # Should hit highest bracket
        self.assertTrue(any(b.rate == 0.47 for b in result.state_breakdown))
        # Net income should be positive
        self.assertGreater(result.net_income, 0)

    def test_income_at_bracket_boundaries(self):
        """Test calculations at exact state bracket boundaries."""
        # Test at €12,450 boundary
        result = calculate_tax(12450, region='none')
        self.assertGreater(result.irpf_tax, 0)

        # Test at €20,200 boundary
        result = calculate_tax(20200, region='none')
        self.assertGreater(result.irpf_tax, 0)

        # Test at €35,200 boundary
        result = calculate_tax(35200, region='none')
        self.assertGreater(result.irpf_tax, 0)

        # Test at €60,000 boundary
        result = calculate_tax(60000, region='none')
        self.assertGreater(result.irpf_tax, 0)

        # Test at €300,000 boundary
        # Need to account for SS deduction
        income_after_ss_at_300k = 300000
        income = income_after_ss_at_300k / (1 - SOCIAL_SECURITY_RATE)
        result = calculate_tax(income, region='none')
        # Should have breakdown entries with 45% and 47% rates
        rates = [b.rate for b in result.state_breakdown]
        self.assertTrue(0.45 in rates or 0.47 in rates)


class TestTaxResultStructure(unittest.TestCase):
    """Test TaxResult dataclass structure."""

    def test_tax_result_attributes(self):
        """Test that TaxResult has all required attributes."""
        result = calculate_tax(60000.0, region='none')
        self.assertIsInstance(result.gross_income, (int, float))
        self.assertIsInstance(result.social_security_tax, (int, float))
        self.assertIsInstance(result.income_after_ss, (int, float))
        self.assertIsInstance(result.personal_allowance, (int, float))
        self.assertIsInstance(result.dependent_allowances, (int, float))
        self.assertIsInstance(result.total_allowances, (int, float))
        self.assertIsInstance(result.taxable_income, (int, float))
        self.assertIsInstance(result.state_irpf_tax, (int, float))
        self.assertIsInstance(result.regional_irpf_tax, (int, float))
        self.assertIsInstance(result.irpf_tax, (int, float))
        self.assertIsInstance(result.total_deductions, (int, float))
        self.assertIsInstance(result.net_income, (int, float))
        self.assertIsInstance(result.effective_rate, (int, float))
        self.assertIsInstance(result.region, str)
        self.assertIsInstance(result.beckham_law, bool)
        self.assertIsInstance(result.beckham_law_tax, (int, float))
        self.assertIsInstance(result.beckham_law_excess_tax, (int, float))
        self.assertIsInstance(result.taxpayer_age, (int, type(None)))
        self.assertIsInstance(result.dependents, DependentInfo)
        self.assertIsInstance(result.state_breakdown, list)
        self.assertIsInstance(result.regional_breakdown, list)

    def test_tax_result_consistency(self):
        """Test that TaxResult values are internally consistent."""
        result = calculate_tax(60000, region='madrid')
        # Total deductions should equal SS + IRPF
        self.assertAlmostEqual(result.total_deductions,
                              result.social_security_tax + result.irpf_tax, places=2)
        # Net income should equal gross - total deductions
        self.assertAlmostEqual(result.net_income,
                              result.gross_income - result.total_deductions, places=2)
        # IRPF should equal state + regional
        self.assertAlmostEqual(result.irpf_tax,
                              result.state_irpf_tax + result.regional_irpf_tax, places=2)
        # Total allowances should equal personal + dependent
        self.assertAlmostEqual(result.total_allowances,
                              result.personal_allowance + result.dependent_allowances, places=2)


class TestAutonomoCalculation(unittest.TestCase):
    """Test autónomo (self-employed) tax calculation."""

    def test_autonomo_basic(self):
        """Test basic autónomo calculation."""
        result = calculate_tax(60000, region='madrid', is_autonomo=True)
        self.assertTrue(result.is_autonomo)
        self.assertIsNotNone(result.contribution_base)
        # Should have social security tax
        self.assertGreater(result.social_security_tax, 0)
        # Personal allowance should not apply for autónomos
        self.assertEqual(result.personal_allowance, 0)
        self.assertEqual(result.total_allowances, 0)

    def test_autonomo_reduced_rate_months_1_12(self):
        """Test autónomo with reduced rate for first 12 months."""
        result = calculate_tax(60000, region='madrid', is_autonomo=True, months_as_autonomo=6)
        self.assertTrue(result.is_autonomo)
        self.assertEqual(result.months_as_autonomo, 6)
        # Should use reduced rate: €80/month
        expected_ss = AUTONOMO_REDUCED_RATE_MONTHS_1_12 * 12
        self.assertAlmostEqual(result.social_security_tax, expected_ss, places=2)

    def test_autonomo_reduced_rate_months_13_24(self):
        """Test autónomo with reduced rate for months 13-24."""
        result = calculate_tax(60000, region='madrid', is_autonomo=True, months_as_autonomo=18)
        self.assertTrue(result.is_autonomo)
        self.assertEqual(result.months_as_autonomo, 18)
        # Should use reduced rate: €160/month
        expected_ss = AUTONOMO_REDUCED_RATE_MONTHS_13_24 * 12
        self.assertAlmostEqual(result.social_security_tax, expected_ss, places=2)

    def test_autonomo_full_rate(self):
        """Test autónomo with full rate (25+ months)."""
        result = calculate_tax(60000, region='madrid', is_autonomo=True, months_as_autonomo=25)
        self.assertTrue(result.is_autonomo)
        self.assertEqual(result.months_as_autonomo, 25)
        # Should use full rate: 30% of contribution base
        monthly_base = result.contribution_base / 12
        expected_ss = monthly_base * AUTONOMO_FULL_RATE * 12
        self.assertAlmostEqual(result.social_security_tax, expected_ss, places=0)

    def test_autonomo_contribution_base_estimation(self):
        """Test autónomo contribution base estimation."""
        income = 60000
        result = calculate_tax(income, region='madrid', is_autonomo=True)
        # Contribution base should be estimated as percentage of income
        expected_monthly_base = (income / 12) * AUTONOMO_DEFAULT_BASE_PERCENTAGE
        # Clamped to min/max
        expected_monthly_base = max(AUTONOMO_MIN_BASE_MONTHLY,
                                   min(expected_monthly_base, AUTONOMO_MAX_BASE_MONTHLY))
        expected_annual_base = expected_monthly_base * 12
        self.assertAlmostEqual(result.contribution_base, expected_annual_base, places=2)

    def test_autonomo_custom_contribution_base(self):
        """Test autónomo with custom contribution base."""
        custom_base = 40000  # annual
        result = calculate_tax(60000, region='madrid', is_autonomo=True,
                              contribution_base=custom_base, months_as_autonomo=25)
        self.assertEqual(result.contribution_base, custom_base)
        # SS should be 30% of custom base
        expected_ss = (custom_base / 12) * AUTONOMO_FULL_RATE * 12
        self.assertAlmostEqual(result.social_security_tax, expected_ss, places=2)

    def test_autonomo_business_expenses(self):
        """Test autónomo with business expenses."""
        expenses = 2000
        # Test without general deduction to match expected calculation
        result = calculate_tax(60000, region='madrid', is_autonomo=True,
                              business_expenses=expenses, months_as_autonomo=6,
                              apply_general_deduction=False)
        self.assertEqual(result.business_expenses, expenses)
        # Taxable income should be: gross - expenses - SS
        expected_taxable = 60000 - expenses - result.social_security_tax
        self.assertAlmostEqual(result.taxable_income, expected_taxable, places=2)

    def test_autonomo_general_deduction(self):
        """Test autónomo with 5% general deduction."""
        result = calculate_tax(60000, region='madrid', is_autonomo=True,
                              business_expenses=2000, months_as_autonomo=6,
                              apply_general_deduction=True)
        # With general deduction: (gross - expenses) * 0.95 - SS
        net_after_expenses = 60000 - 2000
        general_deduction = net_after_expenses * AUTONOMO_GENERAL_EXPENSE_RATE
        expected_taxable = net_after_expenses - general_deduction - result.social_security_tax
        self.assertAlmostEqual(result.taxable_income, expected_taxable, places=2)

    def test_autonomo_no_general_deduction(self):
        """Test autónomo without 5% general deduction."""
        result = calculate_tax(60000, region='madrid', is_autonomo=True,
                              business_expenses=2000, months_as_autonomo=6,
                              apply_general_deduction=False)
        # Without general deduction: gross - expenses - SS
        expected_taxable = 60000 - 2000 - result.social_security_tax
        self.assertAlmostEqual(result.taxable_income, expected_taxable, places=2)

    def test_autonomo_no_personal_allowance(self):
        """Test that autónomos don't get personal allowance."""
        result = calculate_tax(60000, region='madrid', is_autonomo=True, taxpayer_age=30)
        self.assertTrue(result.is_autonomo)
        # Personal allowance should be 0 for autónomos
        self.assertEqual(result.personal_allowance, 0)
        self.assertEqual(result.total_allowances, 0)

    def test_autonomo_with_dependents(self):
        """Test autónomo with dependents (only dependent allowances apply)."""
        dependents = DependentInfo(children_3_plus=2)
        result = calculate_tax(60000, region='madrid', is_autonomo=True, dependents=dependents)
        self.assertTrue(result.is_autonomo)
        # Personal allowance should be 0, but dependent allowances should apply
        self.assertEqual(result.personal_allowance, 0)
        self.assertGreater(result.dependent_allowances, 0)
        self.assertEqual(result.total_allowances, result.dependent_allowances)

    def test_autonomo_vs_employee_ss_difference(self):
        """Test that autónomo SS is different from employee SS."""
        income = 60000
        result_autonomo = calculate_tax(income, region='madrid', is_autonomo=True, months_as_autonomo=6)
        result_employee = calculate_tax(income, region='madrid', is_autonomo=False)

        # Autónomo SS should be different (reduced rate €80/month = €960/year)
        # Employee SS should be 6.35% of income
        self.assertNotEqual(result_autonomo.social_security_tax, result_employee.social_security_tax)
        # Autónomo with reduced rate should have lower SS than employee
        self.assertLess(result_autonomo.social_security_tax, result_employee.social_security_tax)

    def test_autonomo_contribution_base_limits(self):
        """Test that contribution base is clamped to min/max limits."""
        # Low income - should use minimum base
        result_low = calculate_tax(10000, region='madrid', is_autonomo=True)
        expected_min_base = AUTONOMO_MIN_BASE_MONTHLY * 12
        self.assertGreaterEqual(result_low.contribution_base, expected_min_base)

        # High income - should use maximum base
        result_high = calculate_tax(200000, region='madrid', is_autonomo=True)
        expected_max_base = AUTONOMO_MAX_BASE_MONTHLY * 12
        self.assertLessEqual(result_high.contribution_base, expected_max_base)

    def test_autonomo_result_attributes(self):
        """Test that TaxResult has autónomo-specific attributes."""
        result = calculate_tax(60000, region='madrid', is_autonomo=True,
                              months_as_autonomo=6, business_expenses=2000)
        self.assertTrue(result.is_autonomo)
        self.assertIsNotNone(result.contribution_base)
        self.assertEqual(result.months_as_autonomo, 6)
        self.assertEqual(result.business_expenses, 2000)


if __name__ == '__main__':
    unittest.main()
