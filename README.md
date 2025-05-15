# ChurchPad

ChurchPad is a subscription-based platform that integrates with Stripe for payment processing. This document provides all the necessary steps to set up and run the application in a local environment using Docker.

---

## Prerequisites

- **Docker**: Ensure Docker is installed and running on your machine.
- **Stripe Account**: A Stripe account is required to obtain API keys and configure webhooks.
- **Ngrok** (optional): For testing Stripe webhooks locally.

---

##  Setting Up the Application Locally

### 1. Clone the Repository
```bash
git clone https://github.com/Abbracx/churchpad.git
cd churchpad
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory and populate it with the required environment variables. An example `.env` file is provided below:

```
SECRET_KEY=''
DEBUG=True

SIGNING_KEY=''

# email creds mailtrap
EMAIL_HOST=mailhog
EMAIL_PORT=1025
DOMAIN=0.0.0.0:8000

POSTGRES_ENGINE=django.db.backends.postgresql
POSTGRES_USER=postgres
POSTGRES_PASSWORD=Password123
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=churchpad-db

# docker compose service connection string
DATABASE_URL=postgres://postgres:Password123@postgres:5432/churchpad-db

# celery connecction 
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
REDIS_URL=redis://redis:6379/0

CELERY_FLOWER_USER=admin
CELERY_FLOWER_PASSWORD=admin

# stripe creds
STRIPE_PUBLIC_KEY=
STRIPE_PRIVATE_KEY=

# Twillio connection
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# stripe webhook
STRIPE_WEBHOOK_SECRET=

```

### 3. Build and Start the Application
```
make build
```
This will spin up the following services
- Django Backend: Accessible at http://localhost:8000
- React Frontend: Accessible at http://localhost:8080
- Mailhog: Accessible at http://localhost:8025 (for testing email functionality)
- Postgres Database
- Redis
- Celery
- Nginx

### 4. Stripe Webhook Configuration
Stripe webhooks are used to handle events such as` payment_intent.succeeded` and `customer.subscription.created`. Follow these steps to configure the webhook:
- a. Start Ngrok (optional): If you are testing locally, use Ngrok to expose your local server to the internet:

```
ngrok http 8000
```

Copy the generated Ngrok URL (e.g., `https://df19-102-89-33-105.ngrok-free.app`).

- b. Register the Webhook Endpoint: Go to your Stripe Dashboard and navigate to Developers > Webhooks. Click Add Endpoint and configure it as follows:

URL: `https://your-ngrok-url/api/v1/subscribe/stripe-webhook/`
Events to Send:
`payment_intent.succeeded`
`customer.subscription.created`
`customer.subscription.updated`
`customer.subscription.deleted`
`payment_failed`
- c. Update the `.env` File: Add the `STRIPE_WEBHOOK_SECRET `from the Stripe Dashboard to your `.env `file.

### 5. How Payment Intent is Used for Subscription

The application uses Stripe's Payment Intent API to handle subscriptions. Below is an overview of the process:

a. Frontend:

The user fills out the subscription form in the React frontend.
The form collects payment details using Stripe Elements and creates a `PaymentMethod`.

b. Backend:

The `PaymentMethod `is sent to the backend, which creates a `PaymentIntent `using the Stripe API.
The backend returns the `client_secret` to the frontend.

c. Frontend:

The frontend confirms the `PaymentIntent` using the `client_secret`.
Upon successful confirmation, the backend finalizes the subscription by creating a Stripe `Subscription` and saving the subscriber's details in the database.

### 6. Navigating to the Frontend

The React frontend is served via Nginx and is accessible at:

`http://localhost:8080`

Features:
- Payment Form: Located at the root URL (/).
- Stripe Integration: Securely handles payment processing using Stripe Elements.

### 7. Additional Commands

`make migrate`

`make createsuperuser`

check the makefile for more commands.

Access the Django admin panel is accessible at: `http://localhost:8000/admin`

### 8. Testing
Run Tests
`make test`

View Test Coverage
`make cov`

### 9. Troubleshooting
Common Issues

a. Ngrok Not Working: Ensure Ngrok is running and the correct URL is registered in Stripe.

b. 502 Bad Gateway: Check if all services are running: `docker-compose ps`

c Webhook Signature Verification Failed: Ensure the `STRIPE_WEBHOOK_SECRET` in your `.env` file matches the secret in the Stripe Dashboard.





