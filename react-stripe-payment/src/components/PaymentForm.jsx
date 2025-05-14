import React, { useState } from 'react';
import { useStripe, useElements, CardElement } from '@stripe/react-stripe-js';
import {SuccessMessage} from './SuccessMessage';
import '../styles/PaymentForm.css';

const PaymentForm = () => {
  const stripe = useStripe();
  const elements = useElements();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone_number: '',
    plan_id: '',
  });

  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Handle input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    setSuccess(null);
    setIsLoading(true);

    if (!stripe || !elements) {
      setError('Stripe has not loaded yet. Please try again later.');
      setIsLoading(false);
      return;
    }

    const cardElement = elements.getElement(CardElement);

    try {
      // Create a PaymentMethod
      const { paymentMethod, error: paymentMethodError } = await stripe.createPaymentMethod({
        type: 'card',
        card: cardElement,
        billing_details: {
          name: formData.name,
        },
      });

      if (paymentMethodError) {
        setError(paymentMethodError.message);
        setIsLoading(false);
        return;
      }

      // Fetch the PaymentIntent client secret from your backend
      const response = await fetch('http://0.0.0.0:8000/api/v1/subscribe/subscriptions/create/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          phone_number: formData.phone_number,
          plan_id: formData.plan_id,
          payment_method_id: paymentMethod.id,
        }),
      });

      const data = await response.json();
      const { client_secret } = data;

      if (!client_secret) {
        setError('Client secret not found in the response.');
        setIsLoading(false);
        return;
      }

      // Confirm the PaymentIntent
      const { error: confirmError, paymentIntent } = await stripe.confirmCardPayment(client_secret, {
        payment_method: {
          card: cardElement,
          billing_details: {
            name: formData.name,
          },
        },
      });

      if (confirmError) {
        setError(confirmError.message);
      } else if (paymentIntent.status === 'succeeded') {
        setSuccess('Payment succeeded! PaymentIntent ID: ' + paymentIntent.id);

        // Optionally, finalize the subscription
        const finalizeResponse = await fetch('http://0.0.0.0:8000/api/v1/subscribe/subscriptions/confirm/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            customer_id: data.customer_id, // Retrieved from the backend during PaymentIntent creation
            plan_id: formData.plan_id,
          }),
        });

        const finalizeData = await finalizeResponse.json();
        console.log('Subscription finalized:', finalizeData);
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="payment-form">
      <div>
        <label htmlFor="name">Name:</label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleInputChange}
          required
        />
      </div>
      <div>
        <label htmlFor="email">Email:</label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleInputChange}
          required
        />
      </div>
      <div>
        <label htmlFor="phone_number">Phone Number:</label>
        <input
          type="tel"
          id="phone_number"
          name="phone_number"
          value={formData.phone_number}
          onChange={handleInputChange}
          required
        />
      </div>
      <div>
        <label htmlFor="plan_id">Plan ID:</label>
        <input
          type="text"
          id="plan_id"
          name="plan_id"
          value={formData.plan_id}
          onChange={handleInputChange}
          required
        />
      </div>
      <div className="card-element">
        <CardElement />
      </div>
      <button type="submit" disabled={!stripe || isLoading}>
        {isLoading ? 'Processing...' : 'Pay'}
      </button>
      {error && <div className="error-message">{error}</div>}
      {/* {success && <div className="success-message">{success}</div>} */}
      { success && <SuccessMessage /> }
    </form>
  );
};

export default PaymentForm;