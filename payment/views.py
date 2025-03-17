from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from decimal import Decimal

from shortener.models import ClickData, Url
from .models import UserBalance, EarningRecord, PaymentTransaction, CountryRate, PaymentSetting
from .forms import WithdrawalRequestForm

@login_required
def earnings_dashboard(request):
    # Get or create user balance
    balance, created = UserBalance.objects.get_or_create(user=request.user)

    # Get earnings statistics
    today = timezone.now().date()

    # Today's earnings
    today_earnings = EarningRecord.objects.filter(
        user=request.user,
        timestamp__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0

    # This week's earnings
    week_earnings = EarningRecord.objects.filter(
        user=request.user,
        timestamp__date__gte=today - timedelta(days=7)
    ).aggregate(total=Sum('amount'))['total'] or 0

    # This month's earnings
    month_earnings = EarningRecord.objects.filter(
        user=request.user,
        timestamp__date__gte=today - timedelta(days=30)
    ).aggregate(total=Sum('amount'))['total'] or 0

    # All time earnings
    all_time_earnings = EarningRecord.objects.filter(
        user=request.user
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Recent transactions
    recent_transactions = PaymentTransaction.objects.filter(
        user=request.user
    ).order_by('-timestamp')[:10]

    # Recent earnings
    recent_earnings = EarningRecord.objects.filter(
        user=request.user
    ).order_by('-timestamp')[:20]

    # Country earnings breakdown
    country_earnings = EarningRecord.objects.filter(
        user=request.user
    ).values('country').annotate(
        total=Sum('amount')
    ).order_by('-total')[:10]

    # Get minimum withdrawal amount
    try:
        min_withdrawal = PaymentSetting.objects.first().min_withdrawal_amount
    except:
        min_withdrawal = Decimal('10.00')

    context = {
        'balance': balance,
        'today_earnings': today_earnings,
        'week_earnings': week_earnings,
        'month_earnings': month_earnings,
        'all_time_earnings': all_time_earnings,
        'recent_transactions': recent_transactions,
        'recent_earnings': recent_earnings,
        'country_earnings': country_earnings,
        'min_withdrawal': min_withdrawal,
    }

    return render(request, 'earnings_dashboard.html', context)

@login_required
def withdrawal_request(request):
    # Get user balance
    balance, created = UserBalance.objects.get_or_create(user=request.user)

    # Get minimum withdrawal amount
    try:
        payment_setting = PaymentSetting.objects.first()
        min_withdrawal = payment_setting.min_withdrawal_amount
    except:
        min_withdrawal = Decimal('10.00')

    if request.method == 'POST':
        form = WithdrawalRequestForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            payment_method = form.cleaned_data['payment_method']

            # Check if amount is valid
            if amount > balance.amount:
                messages.error(request, "Withdrawal amount exceeds your current balance.")
                return redirect('withdrawal_request')

            if amount < min_withdrawal:
                messages.error(request, f"Minimum withdrawal amount is {min_withdrawal}.")
                return redirect('withdrawal_request')

            # Create transaction
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.status = 'pending'

            # Store payment details based on payment method
            payment_details = {}
            if payment_method == 'paypal':
                payment_details = {
                    'paypal_email': form.cleaned_data.get('paypal_email')
                }
            elif payment_method == 'bank_transfer':
                payment_details = {
                    'bank_name': form.cleaned_data.get('bank_name'),
                    'account_name': form.cleaned_data.get('account_name'),
                    'account_number': form.cleaned_data.get('account_number'),
                    'routing_number': form.cleaned_data.get('routing_number')
                }
            elif payment_method == 'crypto':
                payment_details = {
                    'crypto_address': form.cleaned_data.get('crypto_address'),
                    'crypto_type': form.cleaned_data.get('crypto_type')
                }

            transaction.payment_details = payment_details
            transaction.save()

            # Deduct from balance
            balance.amount -= amount
            balance.save()

            messages.success(request, "Withdrawal request submitted successfully.")
            return redirect('earnings_dashboard')
    else:
        form = WithdrawalRequestForm()

    context = {
        'form': form,
        'balance': balance,
        'min_withdrawal': min_withdrawal,
    }

    return render(request, 'withdrawal_request.html', context)

@login_required
def earnings_history(request):
    # Get earnings by URL
    url_earnings = EarningRecord.objects.filter(
        user=request.user
    ).values('url__short_code', 'url__original_url').annotate(
        total=Sum('amount')
    ).order_by('-total')

    # Get earnings by country
    country_earnings = EarningRecord.objects.filter(
        user=request.user
    ).values('country').annotate(
        total=Sum('amount')
    ).order_by('-total')

    # Get earnings by date (last 30 days)
    today = timezone.now().date()
    date_earnings = []

    for i in range(30):
        date = today - timedelta(days=i)
        amount = EarningRecord.objects.filter(
            user=request.user,
            timestamp__date=date
        ).aggregate(total=Sum('amount'))['total'] or 0

        date_earnings.append({
            'date': date.strftime('%Y-%m-%d'),
            'amount': amount
        })

    context = {
        'url_earnings': url_earnings,
        'country_earnings': country_earnings,
        'date_earnings': date_earnings,
    }

    return render(request, 'earnings_history.html', context)

@login_required
def transaction_history(request):
    transactions = PaymentTransaction.objects.filter(
        user=request.user
    ).order_by('-timestamp')

    return render(request, 'transaction_history.html', {'transactions': transactions})