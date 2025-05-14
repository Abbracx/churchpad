import React from 'react';
import PaymentForm from './components/PaymentForm';
import { Elements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';

const stripePromise = loadStripe('pk_test_51HuF6XHvk2x7lwHj7VGBw8KWghsQTQfssUIvNuLe40QrtRBqyJM1UgN6Bo2QQgS6akMiSdJ6Ah4mCTtPq3K7n2iA00yfj6eXH1');

function App() {
  return (
    <div className="App">
      <h1>Stripe Payment</h1>
      <Elements stripe={stripePromise}>
        <PaymentForm />
      </Elements>
    </div>
  );
}

export default App;