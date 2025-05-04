from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail
from django.conf import settings
from .models import House, BookingRequest, HelpDeskModel, Message, Payment
from HouseRentManagementApp.models import UserProfile, OTP
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.db.models import Count, Avg, Q, Sum
from datetime import datetime
import uuid

# Create your views here.
def AllUser(request):
    u = UserProfile.objects.filter(verified=True).exclude(user=request.user)
    if request.method == "POST":
        search = request.POST.get("search")
        u = UserProfile.objects.filter(user__first_name__icontains=search, verified=True).exclude(user=request.user)
    page = request.GET.get('page', 1)

    paginator = Paginator(u, 10)
    try:
        u = paginator.page(page)
    except PageNotAnInteger:
        u = paginator.page(1)
    except EmptyPage:
        u = paginator.page(paginator.num_pages)
    return render(request, 'all-user.html', {'user':u})


def AddAdmin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        DOB = request.POST.get('dob')
        profile_pic = request.FILES.get('pic')
        gender=request.POST.get('gender')
        address= request.POST.get('address')
        
        if pass1!=pass2:
            msg='Password should be same.'
            return render(request,'add-admin.html',{'msg':msg})
        if len(contact)!=10:
            msg='Contact should be 10 digit.'
            return render(request,'add-admin.html',{'msg':msg})
        try:
            user=User.objects.create_user(
                username=username,
                email=email,
                password=pass1,
                first_name=first_name,
                last_name=last_name
                )
        except:
            msg='Usename already exist.'
            return render(request,'add-admin.html',{'msg':msg})
        UserProfile.objects.create(
            user=user,
            profilePicture=profile_pic,
            contact_No=contact,
            address=address,
            gender=gender,
            DOB=DOB,
            userType="Admin"
            )
        return redirect('all-user')
    return render(request, 'add-admin.html')


def Profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Import models at the top of the function
    from django.db.models import Count
    from django.contrib.auth.models import User
    from .models import House, HelpDeskModel
    
    context = {}
    
    # Add statistics for admin users
    if request.user.is_superuser:
        context['user_count'] = User.objects.count()
        context['house_count'] = House.objects.count()
        context['ticket_count'] = HelpDeskModel.objects.count()
    
    # Add property statistics for owners
    if hasattr(request.user, 'userprofile_set') and request.user.userprofile_set.exists():
        user_profile = request.user.userprofile_set.first()
        if user_profile.userType == "Owner":
            # Count rented properties for this owner
            context['rented_count'] = House.objects.filter(user=user_profile, status="Rented").count()
    
    return render(request, 'profile.html', context)


def ViewUser(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    u = UserProfile.objects.get(id=id)

    return render(request, 'view-user.html',{'user':u})


def DeleteUser(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    u = User.objects.get(id=id)
    u.delete()
    return redirect('all-user')


def DeleteHouse(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Only admin or the house owner can delete houses
    user_profile = request.user.userprofile_set.first()
    if user_profile.userType != "Admin" and user_profile.userType != "Owner":
        return redirect('dashboard')
    
    house = House.objects.get(id=id)
    
    # If user is an owner, they can only delete their own houses
    if user_profile.userType == "Owner" and house.user != user_profile:
        return redirect('my-house')
    
    # Delete the house
    house.delete()
    
    # Redirect based on user type
    if user_profile.userType == "Admin":
        return redirect('admin-panel')
    else:
        return redirect('my-house')


def ApproveOwnerRequest(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    u = UserProfile.objects.get(id=id)
    u.verified = True
    u.save()
    return redirect('approve-owner')



def EditProfile(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    u = UserProfile.objects.get(id=id)
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        dob = request.POST.get('dob')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        pic = request.FILES.get('pic')
        contact = request.POST.get('contact')

        if len(contact)!=10:
            msg = "Contact number should be 10 digit"
            return render(request,'edit-profile.html', {'details':u, 'msg':msg})
        
        if pic:
            u.profilePicture = pic
        u.DOB = dob
        u.address = address
        u.gender = gender
        u.contact_No = contact

        u.user.email = email
        u.user.first_name = first_name
        u.user.last_name = last_name
        u.user.save()
        u.save()
        return redirect('profile')
    return render(request,'edit-profile.html', {'details':u})



def ChangePassword(request):
    if not request.user.is_authenticated:
        return redirect('login')
    msg = ''
    if request.method == "POST":
        username = request.user.username
        oldpass = request.POST.get('oldpass')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1!=password2:
            msg='New and Confirm Password should be same.'
            return render(request,'changepass.html', {'msg':msg})
              
        user = User.objects.get(username=username)
        newpass = user.check_password(oldpass)
        
        if newpass:
            user.set_password(password1)
            user.save()
            data=authenticate(username=username,password=password1)
            if data !=None:
                login(request,data)
                return redirect('profile')
        msg='Old Password should be same.'
    return render(request,'changepass.html', {'msg':msg})


def MyHouse(request):
    if not request.user.is_authenticated:
        return redirect('login')
    houses = House.objects.filter(user=UserProfile.objects.get(user=request.user))
    
    # Count available and rented houses
    available_count = houses.filter(status='Available').count()
    rented_count = houses.filter(status='Rented').count()
    
    # Calculate monthly revenue from rented houses
    monthly_revenue = sum(house.price for house in houses.filter(status='Rented'))
    
    context = {
        'houses': houses,
        'available_count': available_count,
        'rented_count': rented_count,
        'monthly_revenue': monthly_revenue
    }
    
    return render(request, 'my-house.html', context)

# def Location(request,location):
#     return render(request, 'see-location.html')
def Location(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    h = House.objects.get(id=id)
    # house = get_object_or_404(House, location=location)  # Retrieve house by location
    return render(request, 'see-location.html', {'house': h})

def RentHouse(request):
    if not request.user.is_authenticated:
        return redirect('login')
    u = UserProfile.objects.get(user=request.user)
    if u.userType == "Owner":
        h = House.objects.filter(user=UserProfile.objects.get(user=request.user))
    else:
        h = House.objects.filter(status='Available')
    if request.method == "POST":
        search = request.POST.get('search')
        
        if u.userType == "Public":
            h = House.objects.filter(status='Available', city__icontains=search)
        elif u.userType == "Owner":
            h = House.objects.filter(user=UserProfile.objects.get(user=request.user), city__icontains=search)
        else:
            h = House.objects.filter(status='Available', city__icontains=search)
    page = request.GET.get('page', 1)

    paginator = Paginator(h, 10)
    try:
        h = paginator.page(page)
    except PageNotAnInteger:
        h = paginator.page(1)
    except EmptyPage:
        h = paginator.page(paginator.num_pages)
    return render(request, 'rent-house.html',{'houses':h})


def AddHouse(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == "POST":
        house_no = request.POST.get('house_no')
        room_size = request.POST.get('room_size')
        area = request.POST.get('area')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        image4 = request.FILES.get('image4')
        location = request.POST.get('location')
        price = request.POST.get('price')
        state = request.POST.get('state')

        House.objects.create(
            user = UserProfile.objects.get(user=request.user),
            house_no = house_no,
            room_size = room_size,
            area = area,
            city = city,
            pincode = pincode,
            image1 = image1,
            image2 = image2,
            image3 = image3,
            image4 = image4,
            location = location,
            price = price,
            state = state
        )
        return redirect('rent-house')
    return render(request, 'add-house.html')


def EditHouse(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    h = House.objects.get(id=id)
    if request.method == "POST":
        house_no = request.POST.get('house_no')
        room_size = request.POST.get('room_size')
        area = request.POST.get('area')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        image4 = request.FILES.get('image4')
        location = request.POST.get('location')
        price = request.POST.get('price')
        state = request.POST.get('state')

        if image1:
            h.image1 = image1
        if image2:
            h.image2 = image2
        if image3:
            h.image3 = image3
        if image4:
            h.image4 = image4
        
        h.house_no = house_no
        h.room_size = room_size
        h.area = area
        h.city = city
        h.pincode = pincode
        h.location = location
        h.price = price
        h.state = state
        h.save()
        return redirect('rent-house')
    return render(request, 'edit-house.html', {'house':h})


def ViewHouse(request,id):
    if not request.user.is_authenticated:
        return redirect('login')
    h = House.objects.get(id=id)
    return render(request, 'view-house.html',{'house_details':h})


def MyBooking(request):
    if not request.user.is_authenticated:
        return redirect('login')
    booking = BookingRequest.objects.filter(user=UserProfile.objects.get(user=request.user))
    return render(request, 'public-book-status.html',{'booking':booking})


def CustomerRequest(request):
    if not request.user.is_authenticated:
        return redirect('login')
    booking = BookingRequest.objects.filter(house__user=UserProfile.objects.get(user=request.user), status="Pending")
    return render(request, 'customer-request.html',{'requests':booking})


def ApprovedCustomer(request):
    booking = BookingRequest.objects.filter(house__user=UserProfile.objects.get(user=request.user), status="Accepted")
    return render(request, 'approved-customers.html',{'requests':booking})


def ApproveCustomerRequest(request, id):
    c = BookingRequest.objects.get(id=id)
    c.status = "Accepted"
    c.save()
    return redirect('approved-customer')


def ConfirmBooking(request, id):
    c = BookingRequest.objects.get(id=id)
    if c.house.status == "Booked":
        msg = 'House is already booked'
        booking = BookingRequest.objects.filter(house__user=UserProfile.objects.get(user=request.user), status="Accepted")
        return render(request, 'approved-customers.html',{'requests':booking, 'msg':msg})
    c.status = "Booked"
    c.house.status = "Booked"
    c.house.save()
    c.save()

    return redirect('approved-customer')


def AvailableHouse(request, id):
    h = House.objects.get(id=id)
    h.status = "Available"
    h.save()
    return redirect('rent-house')


def BookHouse(request,id):
    if not request.user.is_authenticated:
        return redirect('login')
    h = House.objects.get(id=id)
    user = UserProfile.objects.get(user=request.user)
    BookingRequest.objects.create(
        user = user,
        house = h
    )
    return redirect('my-booking')


def DeletePublicBooking(request,id):
    if not request.user.is_authenticated:
        return redirect('login')
    booking = BookingRequest.objects.get(id=id)
    booking.delete()
    return redirect('customer-request')


def HelpDeskView(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user_profile = UserProfile.objects.get(user=request.user)  # Fetch the user profile
    booked_houses = BookingRequest.objects.filter(user=user_profile, status="Booked").select_related('house')

    if not booked_houses.exists():
        return render(request, 'user-helpdesk.html', {'error': 'You cannot send a message. You must book a house first.'})

    if request.method == "POST":
        message_text = request.POST.get('message')

        for booking in booked_houses:
            house_owner = booking.house.user  # Fetch house owner
            house_owner_email = house_owner.user.email  # House owner email
            admin_email = 'admin@example.com'  # Change this to actual admin email

            # Save message in the database
            HelpDeskModel.objects.create(
                user=user_profile,
                house=booking.house,
                owner=house_owner,
                message=message_text
            )

            # Email Body
            subject = "HelpDesk Query - Home Rental Service"
            body = f"""
            Hi {house_owner.user.first_name},

            {request.user.first_name} has booked your house ({booking.house.house_no}) and wants to contact you.

            User Email: {request.user.email}
            House Owner Email: {house_owner_email}

            Message:
            {message_text}

            Regards,
            Home Rental Service
            """

            # Send Email to Owner & CC Admin
            send_mail(subject, body, settings.EMAIL_HOST_USER, [house_owner_email, admin_email], fail_silently=True)

        return render(request, 'user-helpdesk.html', {'success': 'Your message has been sent successfully.'})

    return render(request, 'user-helpdesk.html')

def ApproveOwner(request):
    if not request.user.is_authenticated:
        return redirect('login')
    unverified = UserProfile.objects.filter(userType="Owner", verified=False)
    return render(request, 'approve-owner.html',{'verified':unverified})



def ApproveAdmin(request):
    if not request.user.is_authenticated:
        return redirect('login')
    unverified = UserProfile.objects.filter(userType="Admin", verified=False)
    return render(request, 'approve-admin.html',{'verified':unverified})


def AdminHelpDesk(request):
    u = UserProfile.objects.get(user=request.user)
    if request.method == "POST":
        email = request.POST.get('email')
        message = request.POST.get('message')

        subject = 'From Home Rental Service'
        from_email = settings.EMAIL_HOST_USER
        to_email = [email]
        if u.userType == "Admin":
            body = f'Hi,  \n \n \t  email: {email} \n \n \t message: {message} \n\n Thanks, \n From Admin, \nHome Rental Service'
        else:
            body = f'Hi {email}, \n \n \t message: {message} \n\n Thanks, \n From Owner, \nHome Rental Service'         
        send_mail(subject, body, from_email, to_email, fail_silently=True)

    return render(request, 'admin-helpdesk.html')


def Dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    total_verified_owner = UserProfile.objects.filter(userType="Owner", verified=True).count()
    total_unverified_owner = UserProfile.objects.filter(userType="Owner", verified=False).count()

    total_verified_admin = UserProfile.objects.filter(userType="Admin", verified=True).count()
    total_unverified_admin = UserProfile.objects.filter(userType="Admin", verified=False).count()

    available_house = House.objects.filter(status="Available").count()
    booked_house = House.objects.filter(status="Booked").count()

    customer_request = BookingRequest.objects.filter(status="Pending").count()

    my_house = House.objects.filter(user=UserProfile.objects.get(user=request.user)).count()
    my_available_house = House.objects.filter(user=UserProfile.objects.get(user=request.user), status="Available").count()

    my_booking = BookingRequest.objects.filter(user=UserProfile.objects.get(user=request.user)).count()

    Dict = {
        "total_verified_owner":total_verified_owner,
        "total_unverified_owner":total_unverified_owner,
        "total_verified_admin":total_verified_admin,
        "total_unverified_admin":total_unverified_admin,
        "available_house":available_house,
        "booked_house":booked_house,
        "customer_request":customer_request,

        "my_house": my_house,
        "my_available_house":my_available_house,

        "my_booking":my_booking
    }
    return render(request, 'dashboard.html',Dict)

# Message-related views
def SendMessage(request, house_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Check if the user is a regular user (not an owner or admin)
    user_profile = request.user.userprofile_set.first()
    if user_profile.userType != "Public":
        messages.error(request, "Only regular users can send messages to house owners.")
        return redirect(f'/view-house/{house_id}/')
    
    if request.method == 'POST':
        message_text = request.POST.get('message')
        if not message_text:
            messages.error(request, "Message cannot be empty")
            return redirect(f'/view-house/{house_id}/')
        
        # Get the house and its owner
        house = get_object_or_404(House, id=house_id)
        owner_profile = house.user
        
        # Create the message
        message = Message.objects.create(
            sender=user_profile,
            receiver=owner_profile,
            house=house,
            message=message_text
        )
        
        # Send email notification to the house owner
        try:
            subject = f"New Message About Your Property: {house.house_no}"
            email_message = f"""
            Dear {owner_profile.user.first_name},

            You have received a new message from {user_profile.user.first_name} {user_profile.user.last_name} about your property ({house.house_no}, {house.area}).

            Message:
            "{message_text}"

            Please log in to your dashboard to respond to this inquiry.

            Best regards,
            Druk Rental Team
            """
            
            send_mail(
                subject,
                email_message,
                settings.EMAIL_HOST_USER,
                [owner_profile.user.email],
                fail_silently=False,
            )
        except Exception as e:
            # Log the error but continue execution
            print(f"Email could not be sent: {str(e)}")
        
        return render(request, 'view-house.html', {
            'house_details': house,
            'message_sent': True
        })
    
    return redirect(f'/view-house/{house_id}/')

def MarkAsRead(request, message_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get the message
    message = get_object_or_404(Message, id=message_id)
    
    # Check if the user is the receiver of the message
    user_profile = request.user.userprofile_set.first()
    if message.receiver != user_profile:
        messages.error(request, "You don't have permission to mark this message as read.")
        return redirect('/owner-panel/')
    
    # Mark the message as read
    message.is_read = True
    message.save()
    
    return redirect('/owner-panel/')

def ReplyToMessage(request, message_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Check if the user is a house owner
    user_profile = request.user.userprofile_set.first()
    if user_profile.userType != "Owner":
        messages.error(request, "Only house owners can reply to messages.")
        return redirect('/owner-panel/')
    
    if request.method == 'POST':
        reply_text = request.POST.get('reply')
        if not reply_text:
            messages.error(request, "Reply cannot be empty")
            return redirect('/owner-panel/')
        
        # Get the original message
        original_message = get_object_or_404(Message, id=message_id)
        
        # Create a new message as a reply
        reply = Message.objects.create(
            sender=user_profile,
            receiver=original_message.sender,
            house=original_message.house,
            message=reply_text
        )
        
        # Mark the original message as read
        original_message.is_read = True
        original_message.save()
        
        # Send email notification to the user
        try:
            subject = f"New Reply About Property: {original_message.house.house_no}"
            email_message = f"""
            Dear {original_message.sender.user.first_name},

            You have received a reply from {user_profile.user.first_name} {user_profile.user.last_name} regarding your inquiry about the property ({original_message.house.house_no}, {original_message.house.area}).

            Your original message:
            "{original_message.message}"

            Their reply:
            "{reply_text}"

            Please log in to continue the conversation.

            Best regards,
            Druk Rental Team
            """
            
            send_mail(
                subject,
                email_message,
                settings.EMAIL_HOST_USER,
                [original_message.sender.user.email],
                fail_silently=False,
            )
        except Exception as e:
            # Log the error but continue execution
            print(f"Email could not be sent: {str(e)}")
        
        messages.success(request, "Your reply has been sent successfully.")
        return redirect('/owner-panel/')
    
    return redirect('/owner-panel/')

# Add this function to retrieve owner messages for the dashboard
def OwnerPanel(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user_profile = request.user.userprofile_set.first()
    if user_profile.userType != "Owner":
        return redirect('/')
    
    # Get all messages for this owner (both sent and received)
    received_messages = Message.objects.filter(receiver=user_profile).order_by('-timestamp')
    sent_messages = Message.objects.filter(sender=user_profile).order_by('-timestamp')
    
    # Get properties with active bookings
    rented_properties = House.objects.filter(
        user=user_profile,
        status="Booked"
    )
    
    # Get all houses owned by this user
    all_properties = House.objects.filter(user=user_profile).count()
    
    # Get payment information for owner
    payments_received = Payment.objects.filter(owner=user_profile).order_by('-payment_date')
    
    # Prepare last payment for each booking for easier template rendering
    tenant_last_payments = {}
    for payment in payments_received:
        booking_id = payment.booking.id
        if booking_id not in tenant_last_payments:
            tenant_last_payments[booking_id] = payment
    
    # Payment statistics
    total_earnings = payments_received.filter(status="Completed").aggregate(
        total=Sum('amount_to_owner')
    )['total'] or 0
    pending_payments = payments_received.filter(status="Pending").count()
    
    # Calculate platform fees
    platform_fees = payments_received.filter(status="Completed").aggregate(
        total=Sum('platform_fee')
    )['total'] or 0
    
    # Monthly earnings (last 6 months)
    monthly_earnings = {}
    for payment in payments_received.filter(status="Completed"):
        month = payment.payment_month
        if month in monthly_earnings:
            monthly_earnings[month] += float(payment.amount_to_owner)
        else:
            monthly_earnings[month] = float(payment.amount_to_owner)
    
    # Combine messages and sort by timestamp
    all_messages = list(received_messages) + list(sent_messages)
    all_messages.sort(key=lambda x: x.timestamp, reverse=True)
    
    # Count unread messages
    unread_message_count = Message.objects.filter(receiver=user_profile, is_read=False).count()
    
    context = {
        'messages': received_messages,  # Keep this as received_messages for template compatibility
        'all_messages': all_messages,   # Add all messages as a separate variable
        'unread_message_count': unread_message_count,
        'rented_properties': rented_properties,
        'all_properties': all_properties,
        'rented_count': rented_properties.count(),
        'payments_received': payments_received,
        'tenant_last_payments': tenant_last_payments,  # Add the tenant_last_payments dictionary
        'total_earnings': total_earnings,
        'pending_payments': pending_payments,
        'platform_fees': platform_fees,
        'monthly_earnings': monthly_earnings,
        'debug_info': {
            'received': received_messages.count(),
            'sent': sent_messages.count(),
            'unread': unread_message_count,
            'payments': payments_received.count()
        }
    }
    
    return render(request, 'owner-panel.html', context)

# Add this function to retrieve user messages for the dashboard
def UserPanel(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user_profile = request.user.userprofile_set.first()
    if user_profile.userType != "Public":
        return redirect('/')
    
    # Get all messages for this user (both sent and received)
    received_messages = Message.objects.filter(receiver=user_profile).order_by('-timestamp')
    sent_messages = Message.objects.filter(sender=user_profile).order_by('-timestamp')
    
    # Get user's active bookings (properties they are renting)
    active_bookings = BookingRequest.objects.filter(
        user=user_profile, 
        status="Booked"
    ).select_related('house', 'house__user')
    
    # Get payment history for user
    payments = Payment.objects.filter(tenant=user_profile).order_by('-payment_date')
    
    # Payment statistics
    total_paid = payments.filter(status="Completed").aggregate(total=Sum('amount'))['total'] or 0
    pending_payments = payments.filter(status="Pending").count()
    
    # Check for payments due
    payment_due = False
    for booking in active_bookings:
        current_month = datetime.now().strftime('%B %Y')
        existing_payment = Payment.objects.filter(
            booking=booking,
            tenant=user_profile,
            payment_month=current_month
        ).exists()
        
        if not existing_payment:
            payment_due = True
            break
    
    # Properties count (rented)
    rented_count = active_bookings.count()
    
    # Combine messages and sort by timestamp
    all_messages = list(received_messages) + list(sent_messages)
    all_messages.sort(key=lambda x: x.timestamp, reverse=True)
    
    # Count unread messages
    unread_message_count = Message.objects.filter(receiver=user_profile, is_read=False).count()
    
    context = {
        'user_messages': received_messages,
        'all_user_messages': all_messages,
        'unread_message_count': unread_message_count,
        'active_bookings': active_bookings,
        'payments': payments,
        'total_paid': total_paid,
        'pending_payments': pending_payments,
        'payment_due': payment_due,
        'rented_count': rented_count,
        'debug_info': {
            'received': received_messages.count(),
            'sent': sent_messages.count(),
            'unread': unread_message_count,
            'bookings': active_bookings.count(),
            'payments': payments.count()
        }
    }
    
    return render(request, 'user-panel.html', context)

def AdminPanel(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Ensure the logged-in user is a verified admin
    user_profile = request.user.userprofile_set.first()
    if user_profile.userType != "Admin" or not user_profile.verified:
        return redirect('dashboard')
    
    # User statistics
    user_count = UserProfile.objects.all().count()
    owner_count = UserProfile.objects.filter(userType="Owner").count()
    public_user_count = UserProfile.objects.filter(userType="Public").count()
    admin_count = UserProfile.objects.filter(userType="Admin").count()
    
    # Property statistics
    property_count = House.objects.all().count()
    available_properties = House.objects.filter(status="Available").count()
    rented_properties = House.objects.filter(status="Booked").count()
    
    # Financial statistics
    total_rent_value = House.objects.filter(status="Booked").aggregate(Sum('price'))['price__sum'] or 0
    avg_rent_price = House.objects.aggregate(Avg('price'))['price__avg'] or 0
    
    # Payment statistics
    total_payments = Payment.objects.all().count()
    completed_payments = Payment.objects.filter(status="Completed").count()
    platform_earnings = Payment.objects.filter(status="Completed").aggregate(Sum('platform_fee'))['platform_fee__sum'] or 0
    
    # Verification statistics
    pending_verifications = UserProfile.objects.filter(verified=False).count()
    pending_owner_verifications = UserProfile.objects.filter(userType="Owner", verified=False).count()
    
    # Booking statistics
    total_bookings = BookingRequest.objects.all().count()
    pending_bookings = BookingRequest.objects.filter(status="Pending").count()
    accepted_bookings = BookingRequest.objects.filter(status="Accepted").count()
    completed_bookings = BookingRequest.objects.filter(status="Booked").count()
    
    # Help desk statistics
    total_helpdesk = HelpDeskModel.objects.all().count()
    
    # Recent Users - for User & Payments section
    recent_users = UserProfile.objects.all().order_by('-user__date_joined')[:10]
    
    # Recent Payments - for User & Payments section
    recent_payments = Payment.objects.all().order_by('-payment_date')[:10]
    
    # Recent activities
    recent_properties = House.objects.all().order_by('-id')[:5]
    recent_bookings = BookingRequest.objects.all().order_by('-request_date')[:5]
    recent_helpdesk = HelpDeskModel.objects.all().order_by('-timestamp')[:5]
    
    # Property statistics by city
    city_stats = House.objects.values('city').annotate(
        count=Count('id'),
        available=Count('id', filter=Q(status="Available")),
        rented=Count('id', filter=Q(status="Rented"))
    ).order_by('-count')[:5]
    
    context = {
        # User statistics
        'user_count': user_count,
        'owner_count': owner_count,
        'public_user_count': public_user_count,
        'admin_count': admin_count,
        
        # Property statistics
        'property_count': property_count,
        'available_properties': available_properties,
        'rented_properties': rented_properties,
        
        # Financial statistics
        'total_rent_value': total_rent_value,
        'avg_rent_price': avg_rent_price,
        
        # Payment statistics
        'total_payments': total_payments,
        'completed_payments': completed_payments,
        'platform_earnings': platform_earnings,
        
        # Verification statistics
        'pending_verifications': pending_verifications,
        'pending_owner_verifications': pending_owner_verifications,
        
        # Booking statistics
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'accepted_bookings': accepted_bookings,
        'completed_bookings': completed_bookings,
        
        # Help desk statistics
        'total_helpdesk': total_helpdesk,
        
        # Recent activities
        'recent_users': recent_users,
        'recent_properties': recent_properties,
        'recent_bookings': recent_bookings,
        'recent_helpdesk': recent_helpdesk,
        'recent_payments': recent_payments,
        
        # Property city statistics
        'city_stats': city_stats,
    }
    
    return render(request, 'admin-panel.html', context)

# Add admin functionality to change user type
def ChangeUserType(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Ensure the logged-in user is an admin
    user_profile = request.user.userprofile_set.first()
    if user_profile.userType != "Admin" or not user_profile.verified:
        return redirect('dashboard')
    
    if request.method == "POST":
        target_user = UserProfile.objects.get(id=id)
        new_type = request.POST.get('user_type')
        
        # Validate the user type
        if new_type in ['Public', 'Owner', 'Admin']:
            target_user.userType = new_type
            target_user.save()
            messages.success(request, f"User type changed to {new_type} successfully.")
        else:
            messages.error(request, "Invalid user type selected.")
        
        return redirect('view-user', id=id)
    
    return redirect('view-user', id=id)


# Add admin functionality to toggle verification status
def ToggleVerification(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Ensure the logged-in user is an admin
    user_profile = request.user.userprofile_set.first()
    if user_profile.userType != "Admin" or not user_profile.verified:
        return redirect('dashboard')
    
    target_user = UserProfile.objects.get(id=id)
    target_user.verified = not target_user.verified
    target_user.save()
    
    status = "verified" if target_user.verified else "unverified"
    messages.success(request, f"User {target_user.user.username} is now {status}.")
    
    # Determine where to redirect based on the context
    if 'approve-owner' in request.META.get('HTTP_REFERER', ''):
        return redirect('approve-owner')
    elif 'approve-admin' in request.META.get('HTTP_REFERER', ''):
        return redirect('approve-admin')
    else:
        return redirect('view-user', id=id)


# Add admin functionality to manage house statuses
def ToggleHouseStatus(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Ensure the logged-in user is an admin or the house owner
    user_profile = request.user.userprofile_set.first()
    if user_profile.userType not in ["Admin", "Owner"]:
        return redirect('dashboard')
    
    house = House.objects.get(id=id)
    
    # If user is an owner, they can only change status of their own houses
    if user_profile.userType == "Owner" and house.user != user_profile:
        return redirect('my-house')
    
    # Toggle the status
    house.status = "Booked" if house.status == "Available" else "Available"
    house.save()
    
    messages.success(request, f"House status changed to {house.status} successfully.")
    
    # Redirect based on user type
    if user_profile.userType == "Admin":
        return redirect('rent-house')
    else:
        return redirect('my-house')

# Payment Functionality
def InitiatePayment(request, booking_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get the booking
    booking = get_object_or_404(BookingRequest, id=booking_id)
    
    # Verify user is authorized to pay for this booking
    user_profile = request.user.userprofile_set.first()
    if booking.user != user_profile:
        messages.error(request, "You are not authorized to make payment for this booking")
        return redirect('user-panel')
    
    # Check if booking is active
    if booking.status != "Booked":
        messages.error(request, "You can only make payments for active bookings")
        return redirect('user-panel')
    
    # Calculate the current month and year for payment
    current_month = datetime.now().strftime('%B %Y')
    
    # Check if payment for this month already exists
    existing_payment = Payment.objects.filter(
        booking=booking,
        tenant=user_profile,
        payment_month=current_month
    ).exists()
    
    if existing_payment:
        messages.warning(request, f"You already have a payment for {current_month}. Please check your payment history.")
        return redirect('user-panel')
    
    # Set up payment information
    house = booking.house
    owner = house.user
    amount = house.price
    
    # Create a pending payment record
    payment = Payment.objects.create(
        booking=booking,
        tenant=user_profile,
        owner=owner,
        amount=amount,
        platform_fee=amount * 0.05,  # 5% platform fee
        amount_to_owner=amount * 0.95,  # 95% to owner
        payment_month=current_month,
        status="Pending"
    )
    
    # Prepare payment form context
    context = {
        'payment': payment,
        'house': house,
        'owner': owner,
        'booking': booking
    }
    
    return render(request, 'payment-form.html', context)

def ProcessPayment(request, payment_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get the payment
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Verify user is authorized
    user_profile = request.user.userprofile_set.first()
    if payment.tenant != user_profile:
        messages.error(request, "You are not authorized to process this payment")
        return redirect('user-panel')
    
    if request.method == "POST":
        # Get payment details from form
        payment_method = request.POST.get('payment_method')
        card_number = request.POST.get('card_number', '')
        expiry_date = request.POST.get('expiry_date', '')
        cvv = request.POST.get('cvv', '')
        
        # In a real system, we would process payment through a payment gateway
        # For this demo, we'll simulate payment success
        
        # Generate a random transaction ID
        transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        
        # Update payment record
        payment.payment_method = payment_method
        payment.transaction_id = transaction_id
        payment.status = "Completed"
        payment.save()
        
        # Send email notifications
        subject = f"Rent Payment Confirmation - {payment.payment_month}"
        
        # Email to tenant
        tenant_message = f"""
        Dear {payment.tenant.user.first_name},
        
        Your rent payment of ₹{payment.amount} for {payment.booking.house.house_no} ({payment.payment_month}) has been processed successfully.
        
        Transaction Details:
        - Transaction ID: {payment.transaction_id}
        - Date: {payment.payment_date.strftime('%d %b %Y, %I:%M %p')}
        - Amount: ₹{payment.amount}
        - Property: {payment.booking.house.house_no}, {payment.booking.house.area}
        - Payment Method: {payment.payment_method}
        
        Thank you for using our platform!
        
        Best regards,
        Druk Rental Team
        """
        
        send_mail(
            subject,
            tenant_message,
            settings.EMAIL_HOST_USER,
            [payment.tenant.user.email],
            fail_silently=True
        )
        
        # Email to owner
        owner_message = f"""
        Dear {payment.owner.user.first_name},
        
        A rent payment for your property has been processed.
        
        Payment Details:
        - Tenant: {payment.tenant.user.first_name} {payment.tenant.user.last_name}
        - Property: {payment.booking.house.house_no}, {payment.booking.house.area}
        - Month: {payment.payment_month}
        - Total Amount: ₹{payment.amount}
        - Platform Fee (5%): ₹{payment.platform_fee}
        - Your Earnings: ₹{payment.amount_to_owner}
        - Transaction ID: {payment.transaction_id}
        - Date: {payment.payment_date.strftime('%d %b %Y, %I:%M %p')}
        
        The amount will be credited to your account within 2-3 business days.
        
        Thank you for using our platform!
        
        Best regards,
        Druk Rental Team
        """
        
        send_mail(
            subject,
            owner_message,
            settings.EMAIL_HOST_USER,
            [payment.owner.user.email],
            fail_silently=True
        )
        
        messages.success(request, "Payment processed successfully!")
        return redirect('payment-success', payment_id=payment.id)
    
    # If GET request, show payment form
    context = {
        'payment': payment,
        'house': payment.booking.house,
        'owner': payment.owner,
        'booking': payment.booking
    }
    
    return render(request, 'payment-process.html', context)

def PaymentSuccess(request, payment_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get the payment
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Verify user is authorized
    user_profile = request.user.userprofile_set.first()
    if payment.tenant != user_profile and payment.owner != user_profile:
        messages.error(request, "You are not authorized to view this payment")
        return redirect('user-panel')
    
    context = {
        'payment': payment,
        'house': payment.booking.house,
        'owner': payment.owner,
        'booking': payment.booking
    }
    
    return render(request, 'payment-success.html', context)

def PaymentHistory(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user_profile = request.user.userprofile_set.first()
    
    # Get payment history based on user type
    if user_profile.userType == "Public":
        payments = Payment.objects.filter(tenant=user_profile).order_by('-payment_date')
        context = {
            'payments': payments,
            'total_paid': payments.filter(status="Completed").aggregate(total=Sum('amount'))['total'] or 0,
            'user_type': 'tenant'
        }
    elif user_profile.userType == "Owner":
        payments = Payment.objects.filter(owner=user_profile).order_by('-payment_date')
        
        # Calculate the count of unique tenants
        tenant_ids = payments.values_list('tenant', flat=True).distinct()
        unique_tenant_count = len(set(tenant_ids))
        
        context = {
            'payments': payments,
            'total_received': payments.filter(status="Completed").aggregate(total=Sum('amount_to_owner'))['total'] or 0,
            'total_platform_fee': payments.filter(status="Completed").aggregate(total=Sum('platform_fee'))['total'] or 0,
            'user_type': 'owner',
            'unique_tenant_count': unique_tenant_count
        }
    else:  # Admin
        payments = Payment.objects.all().order_by('-payment_date')
        
        # Calculate the count of unique tenants for admin view
        tenant_ids = payments.values_list('tenant', flat=True).distinct()
        unique_tenant_count = len(set(tenant_ids))
        
        context = {
            'payments': payments,
            'total_processed': payments.filter(status="Completed").aggregate(total=Sum('amount'))['total'] or 0,
            'total_platform_fee': payments.filter(status="Completed").aggregate(total=Sum('platform_fee'))['total'] or 0,
            'user_type': 'admin',
            'unique_tenant_count': unique_tenant_count
        }
    
    return render(request, 'payment-history.html', context)

def house_list(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user_profile = request.user.userprofile_set.first()
    
    # Get all houses for the owner
    houses = House.objects.filter(user=user_profile)
    
    # Get statistics
    total_houses = houses.count()
    available_houses = houses.filter(status='Available').count()
    rented_houses = houses.filter(status='Rented').count()
    total_revenue = sum(house.price for house in houses.filter(status='Rented'))
    
    context = {
        'houses': houses,
        'total_houses': total_houses,
        'available_houses': available_houses,
        'rented_houses': rented_houses,
        'total_revenue': total_revenue,
    }
    
    return render(request, 'house-list.html', context)
    