from datetime import datetime

from django.db.models import Sum
from django.shortcuts import render
from django.views.generic.base import View

from .models import Wallet, Transfer, PromoCode


class WalletsView(View):
    """Список кошельков на главной"""

    def get(self, request):
        wallets = Wallet.objects.all()
        transfers = Transfer.objects.order_by("-id")
        totals = wallets.aggregate(Sum('balance'))
        total = totals.get('balance__sum')
        last = Wallet.objects.last()
        return render(request, "coins/wallets.html",
                      {"wallet_list": wallets, "total_sum": total, "last_wallet": last, "transfer_list": transfers})


class TransferView(View):
    def post(self, request):
        sender = request.user
        try:
            receiver = Wallet.objects.get(id=int(request.POST.get("id")))
        except:
            return render(request, "coins/transfer.html",
                          {"successfully": False, "reason": "receiver_does_not_exist_error"})
        if sender is not None and receiver is not None and sender != receiver and request.POST.get("amount", False):
            amount = float(request.POST["amount"])
            if amount <= float(sender.balance):
                sender.balance = float(sender.balance) - amount
                receiver.balance = float(receiver.balance) + amount
                sender.save()
                receiver.save()
                Transfer.objects.create(sender=sender, receiver=receiver, amount=amount)
            else:
                return render(request, "coins/transfer.html", {"successfully": False, "reason": "low_balance_error"})
        else:
            return render(request, "coins/transfer.html", {"successfully": False, "reason": "incorrect_request_error"})
        return render(request, "coins/transfer.html", {"successfully": True, "reason": None})


class PromoCodeView(View):
    def post(self, request):
        key = request.POST.get("key", False)
        if key:
            try:
                key = PromoCode.objects.get(key=str(key).upper())
            except:
                return render(request, "coins/promocode.html", {"successfully": False, "reason": "key_does_not_exist_error"})
            if not key.is_applied:
                user = request.user
                wallet = Wallet.objects.get(user=user)
                wallet.balance = float(wallet.balance) + float(key.amount)
                key.is_applied = True
                key.save()
                wallet.save()
            else:
                return render(request, "coins/promocode.html", {"successfully": False, "reason": "key_already_applied_error"})
        else:
            return render(request, "coins/promocode.html", {"successfully": False, "reason": "incorrect_request_error"})
        return render(request, "coins/promocode.html", {"successfully": True, "reason": None})
