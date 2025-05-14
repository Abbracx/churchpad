import { loadStripe } from '@stripe/stripe-js';

const stripePromise = loadStripe('pk_test_51HuF6XHvk2x7lwHj7VGBw8KWghsQTQfssUIvNuLe40QrtRBqyJM1UgN6Bo2QQgS6akMiSdJ6Ah4mCTtPq3K7n2iA00yfj6eXH1');

const createPaymentIntent = async (amount) => {
  const response = await fetch('/create-payment-intent', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ amount }),
  });

  if (!response.ok) {
    throw new Error('Failed to create payment intent');
  }

  return response.json();
};

export { stripePromise, createPaymentIntent };