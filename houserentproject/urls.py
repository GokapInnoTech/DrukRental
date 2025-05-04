"""houserentproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
# from HouseRentManagementApp import views
from HouseRentManagementApp.views import (
    IndexPage,
    AboutPage,
    ContactPage,
    ServicesPage,
    LoginPage,
    Logout,
    SignPage,
    OwnerSign,
    ForgotPage,
    ForgotPassword,
    SendEmailForForgotPassword
    # agent_view
    )
from AdminApp.views import (
    AllUser,
    ViewUser,
    AddAdmin,
    Profile, 
    DeleteUser,
    ChangePassword,
    EditProfile,
    EditHouse,
    RentHouse,
    house_list,

    ViewHouse,
    MyBooking,
    AddHouse,
    CustomerRequest,
    BookHouse,
    DeletePublicBooking,
    MyHouse,
    Location,

    HelpDeskView,
    AdminHelpDesk,
    ApproveOwner,
    ApproveAdmin,
    ApprovedCustomer,
    ApproveOwnerRequest,
    ApproveCustomerRequest,
    ConfirmBooking,
    AvailableHouse,

    Dashboard,
    
    # New messaging views
    SendMessage,
    MarkAsRead,
    ReplyToMessage,
    OwnerPanel,
    UserPanel,

    # Admin panel
    AdminPanel,
    DeleteHouse,
    ChangeUserType,
    ToggleVerification,
    ToggleHouseStatus,
    
    # Payment functionality
    InitiatePayment,
    ProcessPayment,
    PaymentSuccess,
    PaymentHistory
)

from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from HouseRentManagementApp import views
# from houserentproject import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',IndexPage,name='index') , 
    path('about/', AboutPage, name='about'),
    path('contact/', ContactPage, name='contact'),
    path('services/', ServicesPage),
    path('login/', LoginPage, name='login'),
    path('logout/', Logout, name='logout'),
    path('sign/', SignPage, name='sign'),
    path('owner-sign/', OwnerSign, name='owner-sign'),
    path('admin-sign/', AddAdmin, name='admin-sign'),
    path('forgot/', ForgotPage),
    path('forgotpassword/',ForgotPassword,name='forgotpassword'),
    path('sendotp/',SendEmailForForgotPassword,name="sendotp"),

    path('change-password/', ChangePassword, name="change-password"),
    path('profile/',Profile,name='profile'),
    path('delete-user/<int:id>/', DeleteUser, name='delete-user'),
    path('edit-profile/<int:id>/', EditProfile, name='edit-profile'),
    path('edit-house/<int:id>/', EditHouse, name='edit-house'),
    path('my-house/', MyHouse, name='my-house'),
    path('add-house/', AddHouse, name='add-house'),
    path('rent-house/', RentHouse, name='rent-house'),
    path('view-house/<int:id>/', ViewHouse, name='view-house'),
    path('book-house/<int:id>/', BookHouse, name='book-house'),
    path('delete-booking/<int:id>/', DeletePublicBooking, name='delete-booking'),
    path('my-booking/', MyBooking, name="my-booking"),
    path('customer-request/', CustomerRequest, name="customer-request"),

    path('helpdesk/', HelpDeskView, name='helpdesk'),
    path('admin-helpdesk/', AdminHelpDesk, name='admin-helpdesk'),
    path('all-user/', AllUser, name='all-user'),
    path('view-user/<int:id>/', ViewUser, name='view-user'),
    path('add-admin/', AddAdmin, name='add-admin'),
    path('approve-owner/', ApproveOwner, name='approve-owner'),
    path('approve-admin/', ApproveAdmin, name='approve-admin'),
    path('approved-customer/', ApprovedCustomer, name='approved-customer'),
    path('approve-owner-request/<int:id>/', ApproveOwnerRequest, name='approve-owner-request'),
    path('approve-customer-request/<int:id>/', ApproveCustomerRequest, name='approve-customer-request'),
    path('confirm-booking/<int:id>/', ConfirmBooking, name='confirm-booking'),
    path('available-house/<int:id>/', AvailableHouse, name='available-house'),
    path('location/<int:id>/', Location, name='location_view'),

    path('dashboard/', Dashboard, name='dashboard'),
    path('house-list/', house_list, name='house-list'),
    # path('agent/', agent_view, name='agent'),
    
    # Admin panel
    path('admin-panel/', AdminPanel, name='admin-panel'),
    path('delete-house/<int:id>/', DeleteHouse, name='delete-house'),
    path('change-user-type/<int:id>/', ChangeUserType, name='change-user-type'),
    path('toggle-verification/<int:id>/', ToggleVerification, name='toggle-verification'),
    path('toggle-house-status/<int:id>/', ToggleHouseStatus, name='toggle-house-status'),
    
    # Messaging
    path('send-message/<int:house_id>/', SendMessage, name='send-message'),
    path('mark-read/<int:message_id>/', MarkAsRead, name='mark-read'),
    path('reply-message/<int:message_id>/', ReplyToMessage, name='reply-message'),
    path('owner-panel/', OwnerPanel, name='owner-panel'),
    path('user-panel/', UserPanel, name='user-panel'),
    
    # Payment functionality
    path('initiate-payment/<int:booking_id>/', InitiatePayment, name='initiate-payment'),
    path('process-payment/<int:payment_id>/', ProcessPayment, name='process-payment'),
    path('payment-success/<int:payment_id>/', PaymentSuccess, name='payment-success'),
    path('payment-history/', PaymentHistory, name='payment-history'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
