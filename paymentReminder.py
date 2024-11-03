import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time

file_name = 'pay_info.json'
recipient_email = ""

def load_payments():
    try:
        with open(file_name, 'r') as file:
            return json.load(file) 
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_payinfo(payments):
    with open(file_name, 'w') as file:
        json.dump(payments, file)

def set_recipient_email():
    global recipient_email
    if len(recipient_email) == 0:
        recipient_email = input("Please enter the email you want to be notified on: ").strip()

def add_payinfo(payments):
    name = input("Enter payment name: ").strip()
    amount = float(input("Enter payment amount ($): "))
    due_date = input("Enter due date (YYYY-MM-DD): ").strip()

    payments.append({
        "Name": name,
        "Amount": amount,
        "Due_date": due_date,
        "Reminder_sent": False,
    })
    save_payinfo(payments)
    print(f"Payment '{name}' added.✅")

def view_payments(payments):
    if not payments:
        print('No payments found.')
        return

    for index, payment in enumerate(payments):
        status = 'Reminder sent' if payment['Reminder_sent'] else 'Pending Reminder'
        print(f"{index + 1}. {payment['Name']} payment - ${payment['Amount']}\n Due on {payment['Due_date']} - ({status})")

def delete_reminder(payments):
    view_payments(payments)
    if not payments:
        return

    try:
        index = int(input("Enter the number of the payment you want to delete: ")) - 1
        if 0 <= index < len(payments):
            removed_payment = payments.pop(index)
            save_payinfo(payments)
            print(f"Payment '{removed_payment['Name']}' has been deleted.❌")
        else:
            print("Invalid payment number.")
    except ValueError:
        print("Please enter a valid number.")

def send_email(subject, body):
    global recipient_email
    sender_email = "pyreminder@gmail.com"
    sender_password = "pysword007"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_and_send_reminders(payments):
    today = datetime.today().date()
    for payment in payments:
        due_date = datetime.strptime(payment["Due_date"], "%Y-%m-%d").date()
        days_until_due = (due_date - today).days

        if days_until_due <= 2 and not payment["Reminder_sent"]:
            subject = f"Reminder: Upcoming Payment for {payment['Name']}"
            body = f"Your payment for {payment['Name']} of ${payment['Amount']} is due on {payment['Due_date']}. Please make sure you pay on time"
            
            send_email(subject, body)
            payment["Reminder_sent"] = True  # Mark the reminder as sent
            print(f"Reminder sent for '{payment['Name']}' payment.")

    save_payinfo(payments)
        

def automate_reminders(payments):
    schedule.every().day.at("09:00").do(check_and_send_reminders, payments)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    payments = load_payments()
    set_recipient_email()  # Set the recipient email once at the
    while True:
        print('\nPayment Reminder Menu:')
        print('1. Add Payment')
        print('2. View Payment')
        print('3. Start Reminder Automation')
        print('4. Delete Reminder')
        print('5. Exit')

        choice = input('Choose an option: ')

        if choice == '1':
            add_payinfo(payments)
        elif choice == '2':
            view_payments(payments)
        elif choice == '3':
            print('Starting automated reminder checks...')
            automate_reminders(payments)
        elif choice == '4':
            delete_reminder(payments)
        elif choice == '5':
            print('Exiting payment reminder platform.')
            break
        else: 
            print('Invalid choice. please type 1,2,3,or 4')

    payments


    