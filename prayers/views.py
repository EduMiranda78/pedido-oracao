import csv
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from .forms import PrayerRequestForm
from .models import PrayerAudit, PrayerRequest


def health(request):
    return JsonResponse(
        {
            "status": "ok",
            "service": "pedido-oracao",
        }
    )


def manifest(request):
    """Serve o manifesto no topo da origem com o MIME esperado pelos navegadores."""
    manifest_path = Path(settings.BASE_DIR) / "static" / "manifest.webmanifest"
    response = FileResponse(
        manifest_path.open("rb"),
        content_type="application/manifest+json; charset=utf-8",
    )
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    return response


def offline(request):
    return render(request, "offline.html")


def service_worker(request):
    script = r"""
const CACHE_NAME = 'pedido-oracao-v1.1.4';
const STATIC_CACHE = [
  '/offline/',
  '/static/css/app.css',
  '/static/js/app.js',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_CACHE))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request).catch(() => caches.match('/offline/'))
    );
    return;
  }

  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(event.request).then((cached) => cached || fetch(event.request))
    );
  }
});
"""
    response = HttpResponse(script, content_type="application/javascript; charset=utf-8")
    response["Service-Worker-Allowed"] = "/"
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


def visible_queryset(user):
    queryset = PrayerRequest.objects.select_related(
        "created_by"
    )

    if user.is_staff:
        return queryset

    return queryset.filter(
        Q(is_reserved=False) |
        Q(created_by=user)
    )


def filtered_queryset(request):
    queryset = visible_queryset(request.user)

    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    reserved = request.GET.get("reserved", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()

    if search:
        queryset = queryset.filter(
            Q(requester_name__icontains=search) |
            Q(requester_origin__icontains=search) |
            Q(beneficiary_name__icontains=search) |
            Q(prayer_text__icontains=search)
        )

    if status:
        queryset = queryset.filter(status=status)

    if reserved == "yes":
        queryset = queryset.filter(is_reserved=True)
    elif reserved == "no":
        queryset = queryset.filter(is_reserved=False)

    if date_from:
        queryset = queryset.filter(
            created_at__date__gte=date_from
        )

    if date_to:
        queryset = queryset.filter(
            created_at__date__lte=date_to
        )

    return queryset


@login_required
def dashboard(request):
    queryset = visible_queryset(request.user)

    context = {
        "today_count": queryset.filter(
            created_at__date=timezone.localdate()
        ).count(),
        "new_count": queryset.filter(
            status=PrayerRequest.Status.NEW
        ).count(),
        "praying_count": queryset.filter(
            status=PrayerRequest.Status.PRAYING
        ).count(),
        "closed_count": queryset.filter(
            status=PrayerRequest.Status.CLOSED
        ).count(),
        "total_count": queryset.count(),
        "latest": queryset[:5],
    }

    return render(
        request,
        "prayers/dashboard.html",
        context,
    )


@login_required
def prayer_list(request):
    queryset = filtered_queryset(request)

    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    params = request.GET.copy()
    params.pop("page", None)

    context = {
        "page_obj": page_obj,
        "filter_query": params.urlencode(),
        "statuses": PrayerRequest.Status.choices,
    }

    return render(
        request,
        "prayers/prayer_list.html",
        context,
    )


@login_required
def prayer_create(request):
    if request.method == "POST":
        form = PrayerRequestForm(request.POST)

        if form.is_valid():
            prayer = form.save(commit=False)
            prayer.created_by = request.user
            prayer.sync_closed_at()
            prayer.save()

            PrayerAudit.objects.create(
                prayer_request=prayer,
                user=request.user,
                action=PrayerAudit.Action.CREATED,
                changes={
                    "status": prayer.status,
                    "reserved": prayer.is_reserved,
                },
            )

            messages.success(request, "Pedido de oração registrado com sucesso.")

            return redirect(
                "prayer_detail",
                pk=prayer.pk,
            )

    else:
        form = PrayerRequestForm(
            initial={
                "status": PrayerRequest.Status.NEW,
            }
        )

    return render(
        request,
        "prayers/prayer_form.html",
        {
            "form": form,
            "title": "Novo pedido de oração",
        },
    )


@login_required
def prayer_detail(request, pk):
    prayer = get_object_or_404(
        visible_queryset(request.user),
        pk=pk,
    )

    audits = None

    if request.user.is_staff:
        audits = prayer.audit_entries.select_related(
            "user"
        )

    return render(
        request,
        "prayers/prayer_detail.html",
        {
            "prayer": prayer,
            "audits": audits,
        },
    )


@login_required
def prayer_edit(request, pk):
    prayer = get_object_or_404(
        visible_queryset(request.user),
        pk=pk,
    )

    if not request.user.is_staff:
        if prayer.created_by_id != request.user.id:
            return HttpResponse(
                "Você não possui permissão para alterar este pedido.",
                status=403,
            )

    tracked_fields = [
        "requester_name",
        "requester_origin",
        "beneficiary_name",
        "prayer_text",
        "status",
        "is_reserved",
    ]

    before = model_to_dict(
        prayer,
        fields=tracked_fields,
    )

    if request.method == "POST":
        form = PrayerRequestForm(
            request.POST,
            instance=prayer,
        )

        if form.is_valid():
            prayer = form.save(commit=False)
            prayer.sync_closed_at()
            prayer.save()

            after = model_to_dict(
                prayer,
                fields=tracked_fields,
            )

            changes = {}

            for field in tracked_fields:
                if before.get(field) != after.get(field):
                    changes[field] = {
                        "before": before.get(field),
                        "after": after.get(field),
                    }

            if changes:
                PrayerAudit.objects.create(
                    prayer_request=prayer,
                    user=request.user,
                    action=PrayerAudit.Action.UPDATED,
                    changes=changes,
                )
                messages.success(request, "Pedido atualizado com sucesso.")
            else:
                messages.info(request, "Nenhuma alteração foi necessária.")

            return redirect(
                "prayer_detail",
                pk=prayer.pk,
            )

    else:
        form = PrayerRequestForm(
            instance=prayer
        )

    return render(
        request,
        "prayers/prayer_form.html",
        {
            "form": form,
            "title": f"Editar pedido #{prayer.pk}",
            "prayer": prayer,
        },
    )


@login_required
def print_list(request):
    queryset = filtered_queryset(request)

    return render(
        request,
        "prayers/print_list.html",
        {
            "requests": queryset,
        },
    )


@login_required
def export_csv(request):
    queryset = filtered_queryset(request)

    response = HttpResponse(
        content_type="text/csv; charset=utf-8"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="pedidos_oracao.csv"'

    response.write("\ufeff")

    writer = csv.writer(
        response,
        delimiter=";",
    )

    writer.writerow(
        [
            "Número",
            "Data",
            "Solicitante",
            "De onde é?",
            "Para quem",
            "Pedido",
            "Status",
            "Reservado",
            "Cadastrado por",
        ]
    )

    for prayer in queryset:
        writer.writerow(
            [
                prayer.pk,
                timezone.localtime(
                    prayer.created_at
                ).strftime("%d/%m/%Y %H:%M"),
                prayer.requester_name,
                prayer.requester_origin,
                prayer.beneficiary_name,
                prayer.prayer_text,
                prayer.get_status_display(),
                "Sim" if prayer.is_reserved else "Não",
                prayer.created_by.username
                if prayer.created_by
                else "",
            ]
        )

    return response


@login_required
def export_xlsx(request):
    queryset = filtered_queryset(request)

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Pedidos de Oração"

    sheet.append(
        [
            "Número",
            "Data",
            "Solicitante",
            "De onde é?",
            "Para quem",
            "Pedido",
            "Status",
            "Reservado",
            "Cadastrado por",
        ]
    )

    for prayer in queryset:
        sheet.append(
            [
                prayer.pk,
                timezone.localtime(
                    prayer.created_at
                ).strftime("%d/%m/%Y %H:%M"),
                prayer.requester_name,
                prayer.requester_origin,
                prayer.beneficiary_name,
                prayer.prayer_text,
                prayer.get_status_display(),
                "Sim" if prayer.is_reserved else "Não",
                prayer.created_by.username
                if prayer.created_by
                else "",
            ]
        )

    widths = {
        "A": 10,
        "B": 20,
        "C": 28,
        "D": 28,
        "E": 28,
        "F": 60,
        "G": 18,
        "H": 12,
        "I": 20,
    }

    for column, width in widths.items():
        sheet.column_dimensions[column].width = width

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="pedidos_oracao.xlsx"'

    return response


@login_required
def export_pdf(request):
    queryset = filtered_queryset(request)

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="pedidos_oracao.pdf"'

    document = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(
        Paragraph(
            "GRUPO REDE",
            styles["Title"],
        )
    )

    story.append(
        Paragraph(
            "Pedidos de Oração",
            styles["Heading2"],
        )
    )

    story.append(Spacer(1, 0.4 * cm))

    for prayer in queryset:
        date = timezone.localtime(
            prayer.created_at
        ).strftime("%d/%m/%Y %H:%M")

        story.append(
            Paragraph(
                f"<b>Pedido #{prayer.pk}</b> - {date}",
                styles["Heading3"],
            )
        )

        story.append(
            Paragraph(
                "<b>Solicitante:</b> "
                + escape(prayer.requester_name),
                styles["BodyText"],
            )
        )

        if prayer.requester_origin:
            story.append(
                Paragraph(
                    "<b>De onde é:</b> "
                    + escape(prayer.requester_origin),
                    styles["BodyText"],
                )
            )

        story.append(
            Paragraph(
                "<b>Orar por:</b> "
                + escape(prayer.beneficiary_name),
                styles["BodyText"],
            )
        )

        story.append(
            Paragraph(
                "<b>Status:</b> "
                + escape(prayer.get_status_display()),
                styles["BodyText"],
            )
        )

        text = escape(
            prayer.prayer_text
        ).replace("\n", "<br/>")

        story.append(
            Paragraph(
                "<b>Pedido:</b><br/>" + text,
                styles["BodyText"],
            )
        )

        story.append(
            Spacer(1, 0.6 * cm)
        )

    document.build(story)

    return response
