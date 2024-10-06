from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404

from admin.mixins import AdminView, AdminTemplateView
from network.models import IPAddress, Network
from lbaas.models import LBaaS, LBaaSForwadRule, LBaaSVirtance
from lbaas.tasks import create_lbaas, reload_lbaas
from virtance.utils import make_ssh_private, decrypt_data, encrypt_data


class AdminLBaaSIndexView(AdminTemplateView):
    template_name = "admin/lbaas/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lbaas = LBaaS.objects.filter(is_deleted=False)
        for lb in lbaas:
            lb.num_rule = LBaaSForwadRule.objects.filter(lbaas=lb, is_deleted=False).count()
            lb.num_virtance = LBaaSVirtance.objects.filter(lbaas=lb, is_deleted=False).count()
        context["lbaas"] = lbaas
        return context


class AdminLBaaSDataView(AdminTemplateView):
    template_name = "admin/lbaas/lbaas.html"

    def get_object(self):
        return get_object_or_404(LBaaS, pk=self.kwargs["pk"], is_deleted=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lbaas = self.get_object()
        context["lbaas"] = lbaas
        context["rules"] = LBaaSForwadRule.objects.filter(lbaas=lbaas, is_deleted=False)
        context["virtances"] = LBaaSVirtance.objects.filter(lbaas=lbaas, is_deleted=False)
        context["ipv4_public"] = IPAddress.objects.get(network__type=Network.PUBLIC, virtance=lbaas.virtance)
        context["ipv4_private"] = IPAddress.objects.get(network__type=Network.PRIVATE, virtance=lbaas.virtance)     
        context["ipv4_compute"] = IPAddress.objects.get(network__type=Network.COMPUTE, virtance=lbaas.virtance)   
        return context


class AdminLBaaSRecreateAction(AdminView):
    def get_object(self):
        return get_object_or_404(LBaaS, pk=self.kwargs["pk"], is_deleted=False)

    def post(self, request, *args, **kwargs):
        lbaas = self.get_object()
        virtance = lbaas.virtance
        virtance.event = virtance.CREATE
        virtance.save()
        lbaas.event = LBaaS.CREATE
        lbaas.private_key = encrypt_data(make_ssh_private())
        lbaas.save()
        create_lbaas.delay(lbaas.id)
        return redirect(reverse("admin_lbaas_data", args=[kwargs.get("pk")]))


class AdminLBaaSReloadAction(AdminView):
    def get_object(self):
        return get_object_or_404(LBaaS, pk=self.kwargs["pk"], is_deleted=False)

    def post(self, request, *args, **kwargs):
        lbaas = self.get_object()
        lbaas.event = LBaaS.RELOAD
        lbaas.save()
        reload_lbaas.delay(lbaas.id)
        return redirect(reverse("admin_lbaas_data", args=[kwargs.get("pk")]))


class AdminLBaaSDownlodPrivateKeyAction(AdminView):
    def get_object(self):
        return get_object_or_404(LBaaS, pk=self.kwargs["pk"], is_deleted=False)

    def get(self, request, *args, **kwargs):
        lbaas = self.get_object()
        private_key = decrypt_data(lbaas.private_key)
        return HttpResponse(
            private_key,
            content_type="application/text",
            charset="utf-8",
            headers={"Content-Disposition": f"attachment; filename=private.pem"},
        )


class AdminLBaaSResetEventAction(AdminView):
    def get_object(self):
        return get_object_or_404(LBaaS, pk=self.kwargs["pk"], is_deleted=False)

    def post(self, request, *args, **kwargs):
        lbaas = self.get_object()
        lbaas.reset_event()
        return redirect(reverse("admin_lbaas_data", args=[kwargs.get("pk")]))
