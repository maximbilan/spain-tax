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
    ALLOWANCE_LARGE_FAMILY_GENERAL,
    ALLOWANCE_SINGLE_PARENT,
    ALLOWANCE_DISABILITY_33,
    ALLOWANCE_DISABILITY_65,
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

    def test_large_family(self):
        """Test allowance for large family."""
        dependents = DependentInfo(large_family=True)
        self.assertEqual(calculate_dependent_allowances(dependents), ALLOWANCE_LARGE_FAMILY_GENERAL)

    def test_large_family_special(self):
        """Test allowance for special large family."""
        dependents = DependentInfo(large_family_special=True)
        # Special takes precedence over general
        self.assertGreater(calculate_dependent_allowances(dependents), ALLOWANCE_LARGE_FAMILY_GENERAL)

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


class TestStandardTaxCalculation(unittest.TestCase):
    """Test standard tax calculation (non-Beckham Law)."""

    def test_low_income_no_region(self):
        """Test tax calculation for low income with no regional tax."""
        result = calculate_tax(20000, region='none')
        self.assertGreater(result.social_security_tax, 0)
        self.assertGreater(result.irpf_tax, 0)
        self.assertGreater(result.net_income, 0)
        self.assertLess(result.net_income, result.gross_income)
        self.assertEqual(result.regional_irpf_tax, 0.0)
        self.assertFalse(result.beckham_law)

    def test_income_with_personal_allowance(self):
        """Test that personal allowance reduces taxable income."""
        income = 30000
        result = calculate_tax(income, region='none')
        self.assertLess(result.taxable_income, result.income_after_ss)
        self.assertEqual(result.personal_allowance, PERSONAL_ALLOWANCE_UNDER_65)

    def test_income_below_allowance(self):
        """Test tax calculation when income is below personal allowance."""
        income = 5000  # Below personal allowance
        result = calculate_tax(income, region='none')
        self.assertEqual(result.taxable_income, 0)
        self.assertEqual(result.irpf_tax, 0.0)

    def test_madrid_region(self):
        """Test tax calculation for Madrid region."""
        result = calculate_tax(60000, region='madrid')
        self.assertGreater(result.regional_irpf_tax, 0)
        self.assertEqual(result.region, 'madrid')

    def test_catalonia_region(self):
        """Test tax calculation for Catalonia region."""
        result = calculate_tax(60000, region='catalonia')
        self.assertGreater(result.regional_irpf_tax, 0)
        self.assertEqual(result.region, 'catalonia')

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

    def test_with_dependents(self):
        """Test tax calculation with dependents."""
        dependents = DependentInfo(children_3_plus=2, large_family=True)
        result = calculate_tax(60000, dependents=dependents, region='none')
        self.assertGreater(result.dependent_allowances, 0)
        self.assertGreater(result.total_allowances, result.personal_allowance)

    def test_effective_rate_calculation(self):
        """Test that effective rate is calculated correctly."""
        result = calculate_tax(60000, region='none')
        expected_rate = (result.total_deductions / result.gross_income) * 100
        self.assertAlmostEqual(result.effective_rate, expected_rate, places=2)

    def test_net_income_calculation(self):
        """Test that net income is calculated correctly."""
        result = calculate_tax(60000, region='none')
        expected_net = result.gross_income - result.total_deductions
        self.assertAlmostEqual(result.net_income, expected_net, places=2)

    def test_breakdown_included(self):
        """Test that tax breakdown is included in result."""
        result = calculate_tax(60000, region='madrid')
        self.assertGreater(len(result.state_breakdown), 0)
        self.assertGreater(len(result.regional_breakdown), 0)

    def test_high_income(self):
        """Test tax calculation for high income."""
        result = calculate_tax(300000, region='none')
        self.assertGreater(result.irpf_tax, 0)
        # Should hit highest bracket (after SS deduction, need higher income)
        # Income after SS: 300000 * (1 - 0.0635) = 280950, which is below 300k threshold
        # So we need income that after SS is above 300k
        high_income = 350000
        result_high = calculate_tax(high_income, region='none')
        income_after_ss = high_income * (1 - SOCIAL_SECURITY_RATE)
        if income_after_ss > 300000:
            self.assertTrue(any(b.rate == 0.47 for b in result_high.state_breakdown))


class TestBeckhamLawCalculation(unittest.TestCase):
    """Test Beckham Law tax calculation."""

    def test_beckham_law_below_threshold(self):
        """Test Beckham Law for income below threshold."""
        income = 500000
        result = calculate_tax(income, beckham_law=True, region='none')
        self.assertTrue(result.beckham_law)
        self.assertEqual(result.regional_irpf_tax, 0.0)
        expected_tax = income * (1 - SOCIAL_SECURITY_RATE) * BECKHAM_LAW_RATE
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

    def test_beckham_law_no_allowances(self):
        """Test that Beckham Law doesn't apply personal allowances."""
        result = calculate_tax(500000, beckham_law=True, region='none')
        self.assertTrue(result.beckham_law)
        self.assertEqual(result.personal_allowance, 0)
        self.assertEqual(result.dependent_allowances, 0)
        self.assertEqual(result.total_allowances, 0)

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

    def test_very_low_income(self):
        """Test calculation with very low income."""
        result = calculate_tax(1000, region='none')
        self.assertGreaterEqual(result.net_income, 0)
        self.assertLessEqual(result.effective_rate, 100)

    def test_very_high_income(self):
        """Test calculation with very high income."""
        result = calculate_tax(1000000, region='none')
        self.assertGreater(result.irpf_tax, 0)
        self.assertLess(result.net_income, result.gross_income)
        # Should hit highest bracket
        self.assertTrue(any(b.rate == 0.47 for b in result.state_breakdown))

    def test_region_normalization(self):
        """Test that region names are normalized to lowercase."""
        result = calculate_tax(60000, region='MADRID')
        self.assertEqual(result.region, 'madrid')

    def test_none_dependents(self):
        """Test that None dependents are handled correctly."""
        result = calculate_tax(60000, dependents=None, region='none')
        self.assertIsNotNone(result.dependents)
        self.assertEqual(result.dependent_allowances, 0)

    def test_all_regions(self):
        """Test that all valid regions work."""
        valid_regions = ['madrid', 'catalonia', 'andalusia', 'valencia', 'basque',
                         'galicia', 'castilla_leon', 'canary_islands', 'none']
        for region in valid_regions:
            result = calculate_tax(60000, region=region)
            self.assertEqual(result.region, region)


class TestTaxResultStructure(unittest.TestCase):
    """Test TaxResult dataclass structure."""

    def test_tax_result_attributes(self):
        """Test that TaxResult has all required attributes."""
        result = calculate_tax(60000.0, region='none')  # Use float to ensure float type
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
        self.assertIsInstance(result.dependents, DependentInfo)
        self.assertIsInstance(result.state_breakdown, list)
        self.assertIsInstance(result.regional_breakdown, list)


if __name__ == '__main__':
    unittest.main()
