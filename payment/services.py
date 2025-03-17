from decimal import Decimal
from django.db import transaction
from .models import CountryRate, UserBalance, EarningRecord, PaymentSetting
from shortener.models import ClickData

class EarningService:
    @staticmethod
    def process_click_earning(click_data_id):
        """
        Process the earning for a click
        """
        try:
            click_data = ClickData.objects.get(id=click_data_id)

            # Check if this click already has an earning record
            if hasattr(click_data, 'earning'):
                return None

            # Get country rate
            country = click_data.country or 'Unknown'
            rate = EarningService._get_rate_for_country(country)

            # Create earning record
            with transaction.atomic():
                # Create earning record
                earning = EarningRecord.objects.create(
                    user=click_data.url.user,
                    url=click_data.url,
                    click=click_data,
                    amount=rate,
                    country=country
                )

                # Update user balance
                balance, created = UserBalance.objects.get_or_create(user=click_data.url.user)
                balance.amount += rate
                balance.save()

                return earning
        except Exception as e:
            print(f"Error processing earnings: {str(e)}")
            return None

    @staticmethod
    def _get_rate_for_country(country):
        """
        Get the payment rate for a country
        """
        try:
            # Get country code (just first 2 chars)
            country_code = country[:2].upper() if country and len(country) >= 2 else 'XX'

            # Try to get country specific rate
            try:
                country_rate = CountryRate.objects.get(country_code=country_code)
                return country_rate.rate_per_click
            except CountryRate.DoesNotExist:
                # Use default rate
                setting = PaymentSetting.objects.first()
                if setting:
                    return setting.default_rate
                else:
                    return Decimal('0.0010')  # Fallback default
        except:
            return Decimal('0.0010')  # Fallback default