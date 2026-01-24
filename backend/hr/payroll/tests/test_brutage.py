from decimal import Decimal
from django.test import SimpleTestCase
from unittest.mock import patch, MagicMock
from hr.payroll.services.brutage import GrossUpService
from hr.payroll.enums import LegalAllowanceType


class GrossUpServiceTest(SimpleTestCase):

    @patch('hr.payroll.services.brutage.SocialContributionService.calculate_contributions')
    @patch('hr.payroll.services.brutage.LegalAllowanceService.calculate_allowances')
    @patch('hr.payroll.services.brutage.TaxCalculationService.calculate_progressive_tax')
    def test_calculate_base_from_net_fixed(self, mock_tax, mock_allowances, mock_social):
        """
        Verify that GrossUpService finds the correct base for a target Net.
        Target Net: 285,714.5 FC (matching user example)
        Expected Base: 195,000 FC
        """
        target_net = Decimal('285714.5')
        
        # Setup mocks to simulate the example guide
        # Step A.1: CNSS = 9,750 on 195,000 Gross
        mock_social.side_effect = lambda gross, base, size: {
            'details': [{'type': 'CNSS', 'employee_amount': Decimal('9750.00'), 'employer_amount': Decimal('0')}]
        }
        
        # Step B: Allowances = 52,000 (Transport) + 50,000 (Logement) + 6,812 (Family) = 108,812
        mock_allowances.side_effect = lambda worked_days, child_count, gross_salary, base_salary: {
            'total_allowances': Decimal('108812.00'),
            'taxable_housing_excess': Decimal('0.00')
        }
        
        # Step A.3: IPR = 8,347.5
        mock_tax.side_effect = lambda taxable_base: Decimal('8347.5')
        
        # We need to ensure the mocks return values that lead to the target_net when base is 195,000
        # Formula in _derive_total_net: (Gross + Allowances) - (CNSS + IPR)
        # (195,000 + 108,812) - (9,750 + 8,347.5) = 303,812 - 18,097.5 = 285,714.5
        
        # Run calculation
        resolved_base = GrossUpService.calculate_base_from_net(
            target_net=target_net,
            company_size=1,
            worked_days=26,
            child_count=1
        )
        
        # Tolerance is 1.00 by default, check if it found 195,000
        self.assertAlmostEqual(resolved_base, Decimal('195000.00'), delta=Decimal('2.00'))

    @patch('hr.payroll.services.brutage.SocialContributionService.calculate_contributions')
    @patch('hr.payroll.services.brutage.LegalAllowanceService.calculate_allowances')
    @patch('hr.payroll.services.brutage.TaxCalculationService.calculate_progressive_tax')
    def test_calculate_base_from_net_hourly(self, mock_tax, mock_allowances, mock_social):
        """
        Verify hourly rate resolution.
        """
        target_net_hourly = Decimal('1000.00')
        std_hours = Decimal('195')
        
        # Mocking returns 0 deductions/allowances for simplicity to see if it converges to target
        mock_social.return_value = {'details': []}
        mock_allowances.return_value = {'total_allowances': Decimal('0'), 'taxable_housing_excess': Decimal('0')}
        mock_tax.return_value = Decimal('0')
        
        resolved_hourly = GrossUpService.calculate_base_from_net(
            target_net=target_net_hourly,
            is_hourly=True,
            std_monthly_hours=std_hours
        )
        
        self.assertAlmostEqual(resolved_hourly, Decimal('1000.00'), delta=Decimal('1.00'))
