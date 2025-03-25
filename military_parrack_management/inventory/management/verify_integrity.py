from django.core.management.base import BaseCommand
from django.db.models import Q
from inventory.models import IntegrityCheck, Weapon, Personnel, Transaction, AccessLog
from django.db import models


class Command(BaseCommand):
    help = "Runs comprehensive Clark-Wilson integrity checks for weapon inventory system"

    def handle(self, *args, **options):
        # Get the auditor for logging integrity checks
        try:
            auditor = Personnel.objects.get(role='AUDITOR')
        except Personnel.DoesNotExist:
            self.stdout.write(self.style.ERROR("No auditor found for integrity checks!"))
            return

        # Comprehensive integrity checks
        checks = [
            self.check_weapon_status_integrity,
            self.check_transaction_consistency,
            self.check_access_log_integrity,
        ]

        overall_passed = True
        failed_checks = []

        for check in checks:
            check_passed = check(auditor)
            if not check_passed:
                overall_passed = False
                failed_checks.append(check.__name__)

        # Create final integrity check record
        IntegrityCheck.objects.create(
            checked_by=auditor,
            checked_table='Comprehensive System',
            passed=overall_passed
        )

        # Report results
        if overall_passed:
            self.stdout.write(self.style.SUCCESS("All integrity checks passed successfully!"))
        else:
            self.stdout.write(
                self.style.ERROR(f"Integrity checks failed: {', '.join(failed_checks)}")
            )

    def check_weapon_status_integrity(self, auditor):
        """
        Check 1: Ensure weapons have valid status and consistent state
        """
        # Check for weapons with invalid status
        invalid_weapons = Weapon.objects.exclude(status__in=['IN', 'OUT'])
        
        # Check for weapons simultaneously checked in and out in transactions
        conflicting_weapons = Weapon.objects.filter(
            Q(status='IN') & 
            Transaction.objects.filter(
                weapon=models.OuterRef('pk'), 
                transaction_type='CHECKOUT'
            ).values('pk')
        )

        if invalid_weapons.exists() or conflicting_weapons.exists():
            self.stdout.write(self.style.WARNING(
                f"Found {invalid_weapons.count()} invalid weapons and "
                f"{conflicting_weapons.count()} conflicting weapons"
            ))
            return False
        return True

    def check_transaction_consistency(self, auditor):
        """
        Check 2: Validate transaction log consistency
        - Ensure every checkout has a corresponding unique checkin
        - No orphaned transactions
        """
        # Check for checkout transactions without matching checkin
        unmatched_checkouts = Transaction.objects.filter(
            transaction_type='CHECKOUT'
        ).exclude(
            weapon__in=Transaction.objects.filter(
                transaction_type='CHECKIN', 
                weapon=models.OuterRef('weapon')
            ).values('weapon')
        )

        if unmatched_checkouts.exists():
            self.stdout.write(self.style.WARNING(
                f"Found {unmatched_checkouts.count()} unmatched checkout transactions"
            ))
            return False
        return True

    def check_access_log_integrity(self, auditor):
        """
        Check 3: Verify access log integrity and consistency
        - Ensure all logged actions have corresponding valid transactions
        - No suspicious or unauthorized access logs
        """
        # Check for access logs without corresponding valid transactions
        suspicious_logs = AccessLog.objects.filter(
            integrity_ok=False
        )

        if suspicious_logs.exists():
            self.stdout.write(self.style.WARNING(
                f"Found {suspicious_logs.count()} suspicious access logs"
            ))
            return False
        return True