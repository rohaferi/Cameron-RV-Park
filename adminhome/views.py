import json, requests, datetime, boto3
import random
import time

from django.template import context

from django.http import HttpResponseRedirect
from django.core.files import File
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.views import View, generic
from django.urls import reverse

from .forms import ParkingCategoryForm, ParkingSpotForm, HomeForm, CustomUserForm, \
    CustomUserCreationForm, VehicleForm, VerifyVehicleForm, CustomUserChangeForm, UserPasswordChangeForm
import boto3

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib import messages

from .models import Booking, ParkingSpot, ParkingCategory, Vehicle, BookingStates, ViewBookings
from .filters import ParkingCatergoryFilter, ParkingSpotFilter, BookingFilter, PreviousAndCurrentBookingFilter
from .forms import BookingForm, ParkingCategoryForm, ParkingSpotForm, HomeForm, CustomUserForm, \
    CustomUserCreationForm, DateRangeForm, VehicleChangeForm

from datetime import date
from fpdf import FPDF
import string

################################################################################################################
#                                       USER AUTHENTICATION                                                    #
################################################################################################################

def signout(request):
    if (not request.user.is_authenticated):
        return HttpResponseRedirect(reverse('adminhome:index'))
    logout(request)
    return redirect("adminhome:index")


def signin(request):
    if request.method == "POST":
        form = CustomUserForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if request.user.is_staff or request.user.is_superuser:
                    return redirect("adminhome:adminhome")
                return redirect("adminhome:userhome")
    else:
        form = CustomUserForm
    return render(request=request,
                  template_name="adminhome/signin.html",
                  context={"form": form})


def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Created New Account: {username}")
            login(request, user)
            messages.info(request, f"you are now logged in as {username}")
            return redirect("adminhome:index")
    else:
        form = CustomUserCreationForm
    return render(request=request,
                  template_name="adminhome/signup.html",
                  context={"form": form})


################################################################################################################
#                                           PARKING SPOT                                                       #
################################################################################################################

def createparkingspot(request):
    if (not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))):
        return HttpResponseRedirect(reverse('adminhome:index'))

    if (request.method == "POST"):
        form = ParkingSpotForm(request.POST or None)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('adminhome:viewoneparkingspot', args=(form.instance.id,)))
        else:
            return render(request=request,
                          template_name="adminhome/createparkingspot.html",
                          context={"form": form})

    form = ParkingSpotForm
    return render(request=request,
                  template_name="adminhome/createparkingspot.html",
                  context={"form": form})


def viewparkingspot(request):
    if (not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))):
        return HttpResponseRedirect(reverse('adminhome:index'))
    parkingspot_list = ParkingSpotFilter(request.GET, queryset=ParkingSpot.objects.all())

    page = request.GET.get('page', 1)
    paginator = Paginator(parkingspot_list.qs, 2)

    try:
        parkingspot_paginated = paginator.page(page)
    except PageNotAnInteger:
        parkingspot_paginated = paginator.page(1)
    except EmptyPage:
        parkingspot_paginated = paginator.page(paginator.num_pages)
    return render(request, "adminhome/viewparkingspot.html", {'parkingspot_paginated': parkingspot_paginated,
                                                              'filter': parkingspot_list})


def viewoneparkingspot(request, pk):
    if (not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))):
        return HttpResponseRedirect(reverse('adminhome:index'))
    context = {}
    context["parkingspot"] = ParkingSpot.objects.get(id=pk)
    return render(request, "adminhome/viewoneparkingspot.html", context)


def updateparkingspot(request, pk):
    if (not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))):
        return HttpResponseRedirect(reverse('adminhome:index'))
    parkingspot = get_object_or_404(ParkingSpot, id=pk)
    form = ParkingSpotForm(request.POST or None, instance=parkingspot)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('adminhome:viewoneparkingspot', args=(form.instance.id,)))

    else:
        return render(request=request,
                      template_name=f"adminhome/updateparkingspot.html",
                      context={"form": form}
                      )


def deleteparkingspot(request, pk):
    if (not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))):
        return HttpResponseRedirect(reverse('adminhome:index'))

    context = {}
    parkingspot = get_object_or_404(ParkingSpot, id=pk)
    context["parkingspot"] = parkingspot

    if request.method == 'POST':
        parkingspot.delete()
        return HttpResponseRedirect(reverse("adminhome:viewparkingspot"))

    return render(request, "deleteparkingspot.html", context=context)


################################################################################################################
#                                       PARKING CATEGORY                                                       #
################################################################################################################

def createparkingcategory(request):
    if (not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))):
        return HttpResponseRedirect(reverse('adminhome:index'))

    if (request.method == "POST"):
        form = ParkingCategoryForm(request.POST or None)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('adminhome:viewoneparkingcategory', args=(form.instance.id,)))
        else:
            return render(request=request,
                          template_name="adminhome/createparkingcategory.html",
                          context={"form": form})

    form = ParkingCategoryForm
    return render(request=request,
                  template_name="adminhome/createparkingcategory.html",
                  context={"form": form})


def viewparkingcategory(request):
    if (not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))):
        return HttpResponseRedirect(reverse('adminhome:index'))

    parkingcategory_list = ParkingCatergoryFilter(request.GET, queryset=ParkingCategory.objects.all())

    page = request.GET.get('page', 1)
    paginator = Paginator(parkingcategory_list.qs, 2)

    try:
        parkingcategory_paginated = paginator.page(page)
    except PageNotAnInteger:
        parkingcategory_paginated = paginator.page(1)
    except EmptyPage:
        parkingcategory_paginated = paginator.page(paginator.num_pages)
    return render(request, "adminhome/viewparkingcategory.html",
                  {'parkingcategory_paginated': parkingcategory_paginated,
                   'filter': parkingcategory_list})


def viewoneparkingcategory(request, pk):
    if (not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))):
        return HttpResponseRedirect(reverse('adminhome:index'))
    context = {}
    context["parkingcategory"] = ParkingCategory.objects.get(id=pk)
    return render(request, "adminhome/viewoneparkingcategory.html", context)


def updateparkingcategory(request, pk):
    if (not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))):
        return HttpResponseRedirect(reverse('adminhome:index'))

    parkingcategory = get_object_or_404(ParkingCategory, id=pk)
    form = ParkingCategoryForm(request.POST or None, instance=parkingcategory)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('adminhome:viewoneparkingcategory', args=(form.instance.id,)))

    else:
        return render(request=request,
                      template_name=f"adminhome/updateparkingcategory.html",
                      context={"form": form}
                      )


def deleteparkingcategory(request, pk):
    if (not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))):
        return HttpResponseRedirect(reverse('adminhome:index'))

    context = {}
    parkingcategory = get_object_or_404(ParkingCategory, id=pk)
    context["parkingcategory"] = parkingcategory

    if request.method == 'POST':
        parkingcategory.delete()
        return HttpResponseRedirect(reverse("adminhome:viewparkingcategory"))

    return render(request, "deleteparkingcategory.html", context=context)


################################################################################################################
#                                           BOOKINGS                                                           #
################################################################################################################

def viewbookings(request, bookingsType):
    if (not (request.user.is_authenticated)):
        return signin(request)

    if (not (request.user.is_staff or request.user.is_superuser)):
        if (bookingsType == ViewBookings.UPCOMING_BOOKINGS):
            bookings_list = BookingFilter(request.GET, queryset=
            Booking.objects.filter(start_time__gte=datetime.datetime.now(), vehicle_id__user_id=request.user))
        elif (bookingsType == ViewBookings.PREVIOUS_BOOKINGS):
            bookings_list = PreviousAndCurrentBookingFilter(request.GET, queryset=
            Booking.objects.filter(end_time__lte=datetime.datetime.now(), vehicle_id__user_id=request.user))
        else:
            bookings_list = PreviousAndCurrentBookingFilter(request.GET, queryset=
            Booking.objects.filter(start_time__lte=datetime.datetime.now(), end_time__gte=datetime.datetime.now(),
                                   vehicle_id__user_id=request.user))
    else:
        if (bookingsType == ViewBookings.UPCOMING_BOOKINGS):
            bookings_list = BookingFilter(request.GET,
                                          queryset=Booking.objects.filter(start_time__gte=datetime.datetime.now()))
        elif (bookingsType == ViewBookings.PREVIOUS_BOOKINGS):
            bookings_list = PreviousAndCurrentBookingFilter(request.GET, queryset=Booking.objects.filter(
                end_time__lte=datetime.datetime.now()))
        else:
            bookings_list = PreviousAndCurrentBookingFilter(request.GET, queryset=
            Booking.objects.filter(start_time__lte=datetime.datetime.now(), end_time__gte=datetime.datetime.now()))

    # TODO: check the datetime.now() time-zone.
    print("date: ", datetime.date.today())

    page = request.GET.get('page', 1)
    paginator = Paginator(bookings_list.qs, 2)

    try:
        bookings_paginated = paginator.page(page)
    except PageNotAnInteger:
        bookings_paginated = paginator.page(1)
    except EmptyPage:
        bookings_paginated = paginator.page(paginator.num_pages)

    return render(request, "adminhome/viewbookings.html",
                  {'bookings_paginated': bookings_paginated, 'filter': bookings_list, 'bookingsType': bookingsType})


def viewupcomingbookings(request):
    return viewbookings(request, ViewBookings.UPCOMING_BOOKINGS)


def viewpreviousbookings(request):
    return viewbookings(request, ViewBookings.PREVIOUS_BOOKINGS)


def viewcurrentbookings(request):
    return viewbookings(request, ViewBookings.CURRENT_BOOKINGS)


def viewonebooking(request, bk_id):
    if (not (request.user.is_authenticated)):
        return signin(request)

    # NOTE: Logic for admin/user view is handled inside the HTML file.
    context = {}
    context["booking"] = Booking.objects.get(id=bk_id)
    return render(request, "adminhome/viewonebooking.html", context)


def editbooking(request, bk_id):
    if (not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))):
        return HttpResponseRedirect(reverse('adminhome:index'))

    booking = get_object_or_404(Booking, id=bk_id)
    form = BookingForm(request.POST or None, instance=booking)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('adminhome:viewonebooking', args=(form.instance.id,)))
    else:
        return render(request=request, template_name="adminhome/editbooking.html", context={"form": form})


def deletebooking(request, bk_id):
    if (not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))):
        return HttpResponseRedirect(reverse('adminhome:index'))

    context = {}
    booking = get_object_or_404(Booking, id=bk_id)
    context["booking"] = booking

    if request.method == 'POST':
        booking.delete()
        return HttpResponseRedirect(reverse("adminhome:viewupcomingbookings"))

    return render(request, "deletebooking.html", context=context)


################################################################################################################
#                                       ADMIN HOME                                                             #
################################################################################################################

def adminhome(request):
    if (not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))):
        return HttpResponseRedirect(reverse('adminhome:index'))
    return render(request, "adminhome/adminhome.html")


def edithome(request):
    if (not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))):
        return HttpResponseRedirect(reverse('adminhome:index'))
    return render(request, "adminhome/edithome.html",
                  {"form": HomeForm(request.POST or None, extra=get_home_metedata())})


def doedit(request):
    if (not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))):
        return HttpResponseRedirect(reverse('adminhome:index'))
    preview_home_metadata = {}
    preview_home_metadata['about'] = {}
    preview_home_metadata['about']['about_header'] = request.POST['about_header']
    preview_home_metadata['about']['about_body'] = request.POST['about_body']

    preview_home_metadata['ameneties'] = {}
    preview_home_metadata['ameneties']['ameneties_header'] = request.POST['ameneties_header']
    preview_home_metadata['ameneties']['ameneties_body'] = request.POST['ameneties_body']

    preview_home_metadata['contact'] = {}
    preview_home_metadata['contact']['phone'] = request.POST['phone']
    preview_home_metadata['contact']['email'] = request.POST['email']
    preview_home_metadata['contact']['location'] = request.POST['location']

    preview_home_metadata['carousel'] = [{} for i in range(3)]
    for i, c in enumerate(request.POST):
        if (c.startswith('carousel_header')):
            preview_home_metadata['carousel'][int(c.split('_')[-1])]['header'] = request.POST[c]
        if (c.startswith('carousel_body')):
            preview_home_metadata['carousel'][int(c.split('_')[-1])]['body'] = request.POST[c]

    session = boto3.Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION_NAME,
    )

    s3 = session.resource('s3')

    sobj = s3.Object(settings.AWS_BUCKET_NAME, settings.AWS_HOME_METADATA_KEY)

    sobj.put(
        Body=(bytes(json.dumps(preview_home_metadata).encode('UTF-8')))
    )

    for i, c in enumerate(request.FILES):
        s3.Bucket(settings.AWS_BUCKET_NAME).put_object(Key=('media/%s.jpg' % c), Body=request.FILES[c])

    return HttpResponseRedirect(reverse('adminhome:edithome'))


def index(request):
    return render(request, "adminhome/index.html", {"metadata": get_home_metedata()})


def get_home_metedata():
    return requests.get('https://d1dmjo0dbygy5s.cloudfront.net/home_metadata.json').json()


def userhome(request):
    if (not request.user.is_authenticated):
        return HttpResponseRedirect(reverse('adminhome:index'))
    if (request.user.is_staff or request.user.is_superuser):
        return HttpResponseRedirect(reverse('adminhome:adminhome'))
    return render(request, "adminhome/userhome.html")


def changepassword(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('adminhome:index'))

    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseRedirect(reverse('adminhome:index'))

    if request.method == "POST":
        form = UserPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect("adminhome:viewprofile")
    else:
        form = UserPasswordChangeForm(request.user)
    return render(request=request,
                  template_name="adminhome/user_changepassword.html",
                  context={"form": form})


def editprofile(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('adminhome:index'))

    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseRedirect(reverse('adminhome:index'))

    if request.method == "POST":
        form = CustomUserChangeForm(request.POST or None, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("adminhome:viewprofile")
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request=request,
                  template_name="adminhome/user_editprofile.html",
                  context={"form": form})


def viewprofile(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('adminhome:index'))

    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseRedirect(reverse('adminhome:index'))

    user = request.user
    vehicles = user.vehicle_set.all()

    return render(request, "adminhome/user_viewprofile.html", {'user': user, 'vehicles': vehicles})


def addvehicle(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('adminhome:index'))

    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseRedirect(reverse('adminhome:index'))

    if request.method == "POST":
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.user_id_id = request.user.id
            vehicle.insurance_doc.name = '{}'.format(vehicle.uuid)
            vehicle.insurance_doc.name = '{}'.format(vehicle.uuid)
            vehicle.save()
            return HttpResponseRedirect(reverse('adminhome:userhome'))
    else:
        form = VehicleForm
    return render(request=request,
                  template_name="adminhome/user_addvehicle.html",
                  context={"form": form})


def unverifiedvehicles(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('adminhome:index'))

    if not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseRedirect(reverse('adminhome:index'))

    unverified_vehicles = Vehicle.objects.filter(is_verified=False)
    form = VerifyVehicleForm

    return render(request, "adminhome/admin_view_unverified_vehicles.html",
                  {'unverified_vehicles': unverified_vehicles,
                   'form': form})


def verifyvehicle(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('adminhome:index'))

    if not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseRedirect(reverse('adminhome:index'))

    if request.method == 'POST':
        vehicle = Vehicle.objects.get(pk=pk)
        vehicle.is_verified = True
        vehicle.insurance_expiry_date = request.POST['insurance_expiry_date']
        vehicle.save()
    return HttpResponseRedirect(reverse('adminhome:unverifiedvehicles'))


def editvehicle(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('adminhome:index'))

    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseRedirect(reverse('adminhome:index'))

    vehicle = Vehicle.objects.get(pk=pk)

    if request.method == 'POST':
        form = VehicleChangeForm(request.POST, request.FILES, instance=vehicle)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.is_verified = False
            vehicle.save()
            return HttpResponseRedirect(reverse('adminhome:viewprofile'))
    else:
        form = VehicleChangeForm(instance=vehicle)
    return render(request, "adminhome/user_editvehicle.html", context={"form": form})


def checkavailability(request):
    parking_categories_all = ParkingCategory.objects.all()
    parking_categories_available = []
    start_date = ''
    end_date = ''
    print("here")
    if (request.method == "POST"):
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        print(start_date)
        for parking_category in parking_categories_all:
            _count = 0
            print(parking_category)
            for parking_spot in parking_category.parking_spot.all():
                print(parking_spot)
                if (parking_spot.is_active):
                    bookings = parking_spot.booking.exclude(start_time__date__gte=request.POST['end_date'], ).exclude(
                        end_time__date__lt=request.POST['start_date'], )
                    if (not bookings.exists()):
                        _count = _count + 1
            if (_count > 0):
                parking_categories_available.append(parking_category)

    form = DateRangeForm
    return render(
        request,
        "adminhome/checkavailability.html",
        {
            'parking_categories_available': parking_categories_available,
            'form': form,
            'start_date': start_date,
            'end_date': end_date,
        }
    )


def showparkingspotschedule(request, pk, start_date, end_date):
    if (not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))):
        return HttpResponseRedirect(reverse('adminhome:index'))
    start_time = datetime.datetime.combine(datetime.datetime.strptime(start_date, '%Y-%m-%d'),
                                           datetime.datetime.min.time())
    end_time = datetime.datetime.combine(datetime.datetime.strptime(end_date, '%Y-%m-%d'), datetime.datetime.min.time())
    twd = (end_time - start_time).days

    pc = []
    parking_spot = ParkingSpot.objects.get(id=pk)

    if (parking_spot.is_active):
        pc.append([parking_spot, [0, []]])
        bookings = parking_spot.booking.filter(start_time__lte=end_time, ).filter(end_time__gte=start_time, ).order_by(
            'start_time', 'end_time')
        len_bookings = len(bookings)
        if (len_bookings == 0):
            pc[-1][1][1].append([False, 100, ""])
            pc[-1][1][0] = 100
        else:
            bookings[0].start_time = bookings[0].start_time.replace(tzinfo=None)
            bookings[0].end_time = bookings[0].end_time.replace(tzinfo=None)
            if (bookings[0].start_time > start_time):
                wd = bookings[0].start_time - start_time
                pc[-1][1][1].append([False, (100 * wd.days) / twd, ""])
                pc[-1][1][0] += (100 * wd.days) / twd
            i = 0
            for booking in bookings:
                booking.start_time = booking.start_time.replace(tzinfo=None)
                booking.end_time = booking.end_time.replace(tzinfo=None)
                s = max(booking.start_time, start_time)
                e = min(booking.end_time, end_time)
                wd = e - s
                pc[-1][1][1].append([True, (100 * wd.days) / twd, booking])
                i = i + 1
                if (i < len_bookings):
                    bookings[i].start_time = bookings[i].start_time.replace(tzinfo=None)
                    bookings[i].end_time = bookings[i].end_time.replace(tzinfo=None)
                    s = max(booking.start_time, start_time)
                    wd = bookings[i].start_time - e
                    pc[-1][1][1].append([False, (100 * wd.days) / twd, ""])
                    pc[-1][1][0] += (100 * wd.days) / twd
            if (bookings[len_bookings - 1].end_time < end_time):
                wd = end_time - bookings[len_bookings - 1].end_time
                pc[-1][1][1].append([False, (100 * wd.days) / twd, ""])
                pc[-1][1][0] += (100 * wd.days) / twd

    pc.sort(reverse=True, key=lambda x: x[1][0])

    return render(request,
                  "adminhome/showparkingspotschedule.html",
                  {
                      'start_date': start_date,
                      'end_date': end_date,
                      'parking_spot': parking_spot,
                      'pc': pc
                  }
                  )


def confirmassignslot(request, pk, ps):
    if (not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))):
        return HttpResponseRedirect(reverse('adminhome:index'))

    context = {}
    booking = Booking.objects.get(id=pk)
    parking_spot = ParkingSpot.objects.get(id=ps)
    context["booking"] = booking
    context["parking_spot"] = parking_spot

    if request.method == 'POST':
        booking.parking_spot_id = parking_spot
        booking.save()
        return HttpResponseRedirect(reverse("adminhome:viewonebooking", args=(booking.id,)))

    return render(request, "confirmassignslot.html", context=context)


def assignslot(request, pk):
    if (not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))):
        return HttpResponseRedirect(reverse('adminhome:index'))

    current_booking = Booking.objects.get(id=pk)
    twd = (current_booking.end_time - current_booking.start_time).days

    pc = []
    for parking_spot in current_booking.pc_id.parking_spot.all():
        if (parking_spot.is_active):
            pc.append([parking_spot, [0, []]])
            bookings = parking_spot.booking.filter(start_time__lte=current_booking.end_time, ).filter(
                end_time__gte=current_booking.start_time, ).order_by('start_time', 'end_time')
            len_bookings = len(bookings)
            if (len_bookings == 0):
                pc[-1][1][1].append([False, 100, ""])
                pc[-1][1][0] = 100
                continue
            if (bookings[0].start_time > current_booking.start_time):
                wd = bookings[0].start_time - current_booking.start_time
                pc[-1][1][1].append([False, (100 * wd.days) / twd, ""])
                pc[-1][1][0] += (100 * wd.days) / twd
            i = 0
            for booking in bookings:
                s = max(booking.start_time, current_booking.start_time)
                e = min(booking.end_time, current_booking.end_time)
                wd = e - s
                pc[-1][1][1].append([True, (100 * wd.days) / twd, booking])
                i = i + 1
                if (i < len_bookings):
                    wd = bookings[i].start_time - e
                    pc[-1][1][1].append([False, (100 * wd.days) / twd, ""])
                    pc[-1][1][0] += (100 * wd.days) / twd
            if (bookings[len_bookings - 1].end_time < current_booking.end_time):
                wd = current_booking.end_time - bookings[len_bookings - 1].end_time
                pc[-1][1][1].append([False, (100 * wd.days) / twd, ""])
                pc[-1][1][0] += (100 * wd.days) / twd

    pc.sort(reverse=True, key=lambda x: x[1][0])

    return render(request,
                  "adminhome/assignslot.html",
                  {
                      'current_booking': current_booking,
                      'pc': pc
                  }
                  )


def booking_pick_vehicle(request, parking_category_id, start_date, end_date):
    if (not request.user.is_authenticated):
        return HttpResponseRedirect(reverse('adminhome:userhome'))
    if (request.user.is_staff or request.user.is_superuser):
        return HttpResponseRedirect(reverse('adminhome:adminhome'))

    # Obtain a list of the user's vehicles.
    vehicles_list = Vehicle.objects.all()
    user_vehicles = []
    for vehicle in vehicles_list:
        if (vehicle.user_id == request.user):
            user_vehicles.append(vehicle)

    return render(request,

                  "adminhome/booking_pick_vehicle.html",
                  {
                      'user_vehicles': user_vehicles,
                      'start_date': start_date,
                      'end_date': end_date,
                      'parking_category_id': parking_category_id,
                  }
                  )


def create_booking(request, vehicle_id, parking_category_id, start_date, end_date):
    vehicle = Vehicle.objects.get(id=vehicle_id)
    pc = ParkingCategory.objects.get(id=parking_category_id)
    booking_obj = Booking(vehicle_id=vehicle, pc_id=pc, state=BookingStates.NEW, start_time=start_date,
                          end_time=end_date, lease_doc_url='', lease_is_signed_by_user=False, admin_comments='')

    if (request.method == "POST"):
        booking_obj.save()
        return render(request, "adminhome/userhome.html")

    return render(
        request,
        "adminhome/bookingconfirmation.html",
        {'booking': booking_obj}
    )


def viewlease(request):
    if (not request.user.is_authenticated):
        return HttpResponseRedirect(reverse('adminhome:index'))
    if (request.user.is_staff or request.user.is_superuser):
        return HttpResponseRedirect(reverse('adminhome:adminhome'))

    # file return the correct lease from db
    booking_id = 1
    vehicle = Booking.objects.get(id=booking_id).vehicle_id
    generatelease(booking_id)
    lease_url = Booking.objects.get(id=booking_id).lease_doc_url

    return HttpResponseRedirect(lease_url)

def generatelease(booking_id):

    booking = Booking.objects.get(id=booking_id)
    vehicle = booking.vehicle_id
    parking_category = booking.pc_id
    user = vehicle.user_id

    lease_duration = (booking.end_time - booking.start_time).days

    if 7 <= lease_duration <= 30:
        freq = 'Week'
        price = parking_category.weekly_rate
    elif lease_duration < 7:
        freq = 'Day'
        price = parking_category.daily_rate
    else:
        freq = 'Month'
        price = parking_category.monthly_rate

    lease_variables = {
        '<lease_date>': date.today().strftime("%b %d %Y"),
        '<user_name>': str(user.first_name) + " " + str(user.last_name),
        '<parking_spot>': "TBD",
        '<price>': str(price),
        '<lease_frequency>': freq,
        '<start_date>': booking.start_time.strftime("%b %d %Y"),
        '<end_date>': booking.end_time.strftime("%b %d %Y")
    }

    # read the sample lease
    f = open("lease_template/sample_lease.txt", "r")
    content = f.read()

    # Change the variable values
    for key, value in lease_variables.items():
        if key in content:
            content = content.replace(key, value)

    # convert it into pdf
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', size=12)
    pdf.multi_cell(w=0, h=5, txt=content, border=0, align='1', fill=False)

    # save the file in the s3 aws
    session = boto3.Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION_NAME,
    )

    s3 = session.resource('s3')
    key_value = 'lease/{}_{}_lease_{}.pdf'.format(vehicle.user_id, booking_id,
                                                  ''.join(random.choice(string.ascii_lowercase) for i in range(20)))
    s3.Bucket(settings.AWS_BUCKET_NAME).put_object(Key=key_value,
                                                   Body=pdf.output("{}_{}_lease.pdf".format(vehicle.user_id, booking_id)
                                                                   ,'S').encode('latin-1'),
                                                   ContentType='application/pdf')
    s3_url = 'https://d1dmjo0dbygy5s.cloudfront.net/'
    booking.lease_doc_url = s3_url + key_value
    booking.save()





