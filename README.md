# Spanish Tax Calculator

A comprehensive command-line tool for calculating Spanish personal income tax (IRPF) and Social Security contributions. This calculator supports all major tax scenarios including regional variations, dependent allowances, age-based adjustments, and special tax regimes like Beckham Law.

## Features

- **Complete Tax Calculation**: Calculates both IRPF (personal income tax) and Social Security contributions
- **Regional Support**: Supports all major Spanish regions with their specific tax brackets
- **Dependent Allowances**: Full support for children, ascendants, disabilities, and family situations
- **Age-Based Adjustments**: Automatic personal allowance adjustments based on taxpayer age
- **Beckham Law**: Special tax regime for foreign workers (24% flat rate up to €600k)
- **Beautiful Output**: Color-coded, aligned output with detailed breakdowns
- **Flexible Input**: Support for annual or monthly income input

## Installation

### Prerequisites

- Python 3.7 or higher
- Bash shell (for the setup script)

### Quick Start

1. Clone or download this repository
2. Make the shell script executable (if needed):
   ```bash
   chmod +x run.sh
   ```
3. Run the calculator:
   ```bash
   ./run.sh 60000
   ```

The script will automatically:
- Create a Python virtual environment
- Install dependencies (if any)
- Run the calculator

## Usage

### Basic Usage

```bash
# Calculate tax for €60,000 annual income
./run.sh 60000

# Or run directly with Python
python3 tax_calculator.py 60000
```

### Common Examples

```bash
# With region (Valencia)
./run.sh 60000 --region valencia

# With dependents (2 children: one under 3, one 6 years old)
./run.sh 81000 --children-under-3 1 --children-3-plus 1 --region valencia

# With detailed breakdown
./run.sh 60000 --region madrid --verbose

# Monthly income input
./run.sh 5000 --monthly --region catalonia

# Age-based personal allowance (65+)
./run.sh 60000 --age 68

# Beckham Law (24% flat rate)
./run.sh 100000 --beckham-law
```

## Command Line Options

### Income Options

- `income` (required): Annual income in euros (or monthly if `--monthly` is used)
- `--monthly`: Treat income as monthly instead of annual

### Tax Calculation Options

- `--region REGION`: Spanish region for regional IRPF tax
  - Options: `madrid`, `catalonia`, `andalusia`, `valencia`, `basque`, `galicia`, `castilla_leon`, `canary_islands`, `none`
  - Default: `none` (state tax only)

- `--beckham-law`: Apply Beckham Law (24% flat rate on income up to €600,000)
  - Income above €600k is taxed at normal progressive rates
  - Regional tax does not apply under Beckham Law

- `--allowance AMOUNT`: Custom personal allowance amount (overrides age-based calculation)
  - Default: €5,550 (or age-based if `--age` is provided)

- `--age AGE`: Taxpayer age in years (affects personal allowance)
  - Under 65: €5,550
  - 65-74: €6,700
  - 75+: €8,100

- `--ss-rate RATE`: Social Security rate as decimal
  - Default: 0.0635 (6.35%)

### Dependent Options

#### Children

- `--children-under-3 N`: Number of children under 3 years old
  - Base allowance: €2,400 (first), €2,700 (second), €4,000 (third), €4,500 (fourth+)
  - Additional: €2,800 per child under 3

- `--children-3-plus N`: Number of children 3 years old or older
  - Base allowance: €2,400 (first), €2,700 (second), €4,000 (third), €4,500 (fourth+)

- `--children-disability-33 N`: Number of children with 33%+ disability
  - Additional allowance: €3,000 per child

- `--children-disability-65 N`: Number of children with 65%+ disability
  - Additional allowance: €12,000 per child

#### Ascendants (Elderly Parents/Grandparents)

- `--ascendants-65 N`: Number of ascendants over 65 years old
  - Allowance: €1,150 per ascendant

- `--ascendants-disability-33 N`: Number of ascendants with 33%+ disability
  - Allowance: €3,000 per ascendant

- `--ascendants-disability-65 N`: Number of ascendants with 65%+ disability
  - Allowance: €12,000 per ascendant

#### Family Status

- `--large-family`: General large family status
  - Allowance: €2,400

- `--large-family-special`: Special large family (5+ children or 4+ with disability)
  - Allowance: €4,800

- `--single-parent`: Single parent family status
  - Allowance: €2,100

#### Taxpayer Disability

- `--taxpayer-disability-33`: Taxpayer has 33%+ disability
  - Allowance: €3,000

- `--taxpayer-disability-65`: Taxpayer has 65%+ disability
  - Allowance: €12,000

- `--taxpayer-disability-mobility`: Taxpayer has mobility disability
  - Allowance: €3,000

- `--taxpayer-disability-dependency`: Taxpayer requires assistance
  - Allowance: €12,000

### Output Options

- `--verbose` or `-v`: Show detailed tax bracket breakdown

## How It Works

### Calculation Flow

1. **Social Security Calculation**
   - Deducted from gross income: 6.35% (default, configurable)
   - This includes healthcare, unemployment, and pension contributions

2. **Allowance Calculation**
   - Personal allowance (age-based or custom)
   - Dependent allowances (children, ascendants, disabilities, family status)
   - Total allowances = Personal + Dependent allowances

3. **Taxable Income**
   - Taxable income = Income after Social Security - Total allowances

4. **IRPF Tax Calculation**
   - **State IRPF**: Progressive brackets (19%-47%)
   - **Regional IRPF**: Additional progressive brackets (varies by region, 8%-15%)
   - **Total IRPF** = State IRPF + Regional IRPF
   - **Beckham Law**: 24% flat rate on income up to €600k (if applicable)

5. **Net Income**
   - Net income = Gross income - Social Security - IRPF tax

### Tax Brackets (2024)

#### State IRPF Brackets
- €0 - €12,450: 19%
- €12,450 - €20,200: 24%
- €20,200 - €35,200: 30%
- €35,200 - €60,000: 37%
- €60,000 - €300,000: 45%
- Over €300,000: 47%

#### Regional IRPF (Examples)
- **Madrid**: 9%-14% (lower rates)
- **Catalonia**: 10%-15%
- **Valencia**: 10%-15%
- **Canary Islands**: 8%-13% (lowest rates)

### Social Security

- **Rate**: 6.35% of gross income (national, same across all regions)
- **Includes**: Healthcare, unemployment benefits, pension contributions, professional training
- **Coverage**: You and your dependents (spouse and children) are automatically covered

## Example Calculations

### Example 1: Single Person, €60,000, Madrid

```bash
./run.sh 60000 --region madrid
```

**Result:**
- Social Security: €3,810 (6.35%)
- State IRPF: €14,438.30
- Regional IRPF (Madrid): €5,398.30
- Total Tax: €23,646.60
- Net Income: €36,353.40
- Effective Rate: 39.41%

### Example 2: Family with 2 Children, €81,000, Valencia

```bash
./run.sh 81000 --children-under-3 1 --children-3-plus 1 --region valencia
```

**Result:**
- Social Security: €5,143.50
- Dependent Allowances: €7,900
  - First child (6 years): €2,400
  - Second child (0 weeks): €2,700 + €2,800 (under 3 bonus) = €5,500
- State IRPF: €18,984.42
- Regional IRPF (Valencia): €7,458.41
- Total Tax: €31,586.33
- Net Income: €49,413.67
- Effective Rate: 39.00%

### Example 3: High Earner with Beckham Law, €700,000

```bash
./run.sh 700000 --beckham-law --verbose
```

**Result:**
- First €600k: 24% = €144,000
- Excess €55,550: Progressive rates = €16,255
- Total IRPF: €160,255
- Effective Rate: 29.24%

## Understanding the Output

The calculator provides:

1. **Summary Section**
   - Gross income
   - Social Security deduction
   - Income after Social Security
   - Personal and dependent allowances
   - Taxable income
   - State and regional IRPF taxes
   - Total deductions
   - Net income
   - Effective tax rate

2. **Detailed Breakdown** (with `--verbose`)
   - Tax bracket-by-bracket breakdown
   - Shows how much income falls in each bracket
   - Shows tax amount for each bracket

3. **Monthly Breakdown**
   - All amounts converted to monthly figures
   - Useful for budgeting

## Important Notes

### Social Security
- **National Rate**: 6.35% is the same across all regions
- **Includes Healthcare**: No separate payment needed for government medical insurance
- **Coverage**: Automatic coverage for you and dependents

### Personal Allowance
- **Age-Based**: Automatically adjusts if you provide `--age`
- **Default**: €5,550 (under 65)
- **65-74**: €6,700
- **75+**: €8,100

### Regional Taxes
- Regional IRPF is **in addition to** state IRPF
- Total IRPF = State + Regional
- Some regions (like Madrid) have lower rates
- Canary Islands has the lowest regional rates

### Beckham Law
- Only applies to eligible foreign workers
- 24% flat rate on income up to €600,000
- Income above €600k taxed at normal progressive rates
- No regional tax under Beckham Law
- No personal allowance under Beckham Law

## Limitations

- Tax brackets are based on 2024 rates (may need updates for future years)
- Does not account for all possible deductions and credits
- Does not handle joint filing for married couples (calculates individual only)
- Contribution base limits for Social Security are not implemented
- Some regional variations may not be fully captured

## Contributing

Feel free to submit issues or pull requests to improve the calculator.

## License

This project is provided as-is for educational and personal use.
