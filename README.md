# House-Rental-Management-System
This is a project using Html, CSS, JavaScript, python, Django and SQL Lite. It helps the customers to find a good rental home within a specified location and helps customer to contact owner of the corresponding house and make a deal.

## Features

- User Authentication (Admin, Owner, Tenant)
- Property Listing and Management
- Booking System
- Messaging System
- Help Desk Support
- Dashboard for different user types
- Payment Processing System

## Payment System

The House Rental Management System includes a robust payment processing system that allows tenants to pay rent to property owners with a 5% platform fee collected by the admin.

### Payment Features

- **For Tenants:**
  - View rented properties and monthly payment amounts
  - Initiate payments for active rentals
  - Choose from multiple payment methods (Credit Card, Debit Card, Net Banking, UPI)
  - View payment history and receipts
  - Automatic email confirmation of payments

- **For Property Owners:**
  - Track incoming payments from tenants
  - View payment history and earnings reports
  - See breakdown of rent amounts and platform fees
  - Monitor payment status

- **For Admins:**
  - Monitor all system payments
  - Track platform earnings (5% of all payments)
  - Generate payment reports
  - View payment statistics

### Payment Process

1. Tenant initiates payment from their dashboard
2. Payment details are entered (simulated payment gateway)
3. System records the payment details:
   - 95% goes to the property owner
   - 5% is retained as platform fee
4. Both tenant and owner receive email confirmations
5. Payment history is updated for all parties

### Payment Database Schema

The payment system uses the `Payment` model with the following fields:
- `booking`: Reference to the booking/rental agreement
- `tenant`: User making the payment
- `owner`: Property owner receiving the payment
- `amount`: Total payment amount
- `platform_fee`: 5% of the total amount
- `amount_to_owner`: 95% of the total amount
- `payment_date`: When the payment was made
- `payment_month`: Month for which rent is being paid
- `transaction_id`: Unique payment identifier
- `payment_method`: How the payment was made
- `status`: Payment status (Pending, Completed, Failed, Refunded)
- `notes`: Additional payment information

## Installation and Setup
